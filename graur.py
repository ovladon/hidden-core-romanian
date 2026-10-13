#!/usr/bin/env python3
"""Lista lui Graur (1954) -> leme DEX '98, apoi comparatia cu straturile grafului.

1. Ortografia din 1954 -> cea actuala (î din interiorul cuvantului -> â; sînt -> sunt; romîn -> român).
2. Forma -> cuvant-titlu DEX '98: direct, sau prin tabelul de forme flexionare dexonline
   (eram, ești -> fi; mie, mă -> eu; îl -> el). Cazurile ramase sunt rezolvate explicit in MANUAL.
3. Pentru fiecare strat (MinSet / Core / Sateliti / Kernel / Rest): cate cuvinte Graur cad acolo,
   fata de cat ar fi la intamplare (ponderea stratului in dictionar), cu test hipergeometric.

  python3 graur.py out/kernel_src1_freq_noexpr_first_ai.json
"""
import collections, json, re, sys
import pandas as pd
from scipy.stats import hypergeom

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import kernel

TRANS = "gold/graur1954/graur1954_transcriere.txt"
# forme pe care tabelul de flexiune nu le poate decide singur (omonime, clitice, prefixe)
MANUAL = {"mă": "eu", "o (pr.)": "el", "o (num.)": "un", "ia(că)": "iacă", "fie-": None,
          "îl": "el", "mie": "eu", "eram": "fi", "ești": "fi", "sunt": "fi", "însumi": "însuși",
          "dânsul": "dânsul", "vre": "vreun", "valma": "valmă", "ăl": "ăla", "ăst": "ăsta",
          "adins": "dinadins", "coperi": "acoperi", "înnota": "înota"}
# absente din DEX '98/'96 asa cum sunt digitizate in dexonline: ager, umbră (raman nelegate)


def modern(w):
    w = kernel.norm(w)
    w = re.sub(r"\s*\((adv|vb|conj|sbst|adj|pr|num)\.\)", lambda m: f" ({m.group(1)}.)", w)
    base = re.sub(r"[¹²]", "", w)
    if base.startswith("sînt"): return base.replace("sînt", "sunt", 1)
    out = []
    for i, ch in enumerate(base):
        # î in interior -> â (reforma din 1993); ramane la inceput si la sfarsit de cuvant
        if ch == "î" and 0 < i < len(base) - 1 and base[i - 1] not in " -(" and base[i + 1] not in " -)":
            out.append("â")
        else:
            out.append(ch)
    return "".join(out).replace("romîn", "român")


def load_graur():
    rows = []
    for line in open(TRANS, encoding="utf8"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        w, ori = line.split("|")
        cat = "M" if w.startswith("+") else "X" if w.endswith("+") else "C"
        rows.append({"orig": w.strip("+"), "cat": cat, "origin": ori})
    return rows


def resolve(rows):
    D = kernel.load_defs((1, 2))
    H = {kernel.norm(x).strip() for x in D.lexicon if x}
    L = pd.read_pickle("data/Lexeme.pkl"); F = pd.read_pickle("data/InflectedForm.pkl")
    lexform = dict(zip(L.id, (kernel.norm(x) for x in L.formNoAccent)))
    form2lem = collections.defaultdict(set)
    for form, lid in zip(F.formNoAccent, F.lexemeId):
        lem = lexform.get(lid)
        if lem in H: form2lem[kernel.norm(form)].add(lem)
    unres = []
    for r in rows:
        m = modern(r["orig"])
        key = re.sub(r"\s*\(.*\)", "", m).strip()
        r["modern"] = m
        if m in MANUAL or key in MANUAL:
            r["lemma"] = MANUAL.get(m, MANUAL.get(key)); r["how"] = "manual"
        elif key in H:
            r["lemma"] = key; r["how"] = "titlu"
        elif len(form2lem.get(key, ())) == 1:
            r["lemma"] = next(iter(form2lem[key])); r["how"] = "flexiune"
        else:
            r["lemma"] = None; r["how"] = "nerezolvat"; unres.append((r["orig"], m, sorted(form2lem.get(key, ()))))
        if r["lemma"] and r["lemma"] not in H:
            unres.append((r["orig"], m, ["(lema manuala absenta din DEX '98)", r["lemma"]])); r["lemma"] = None
    return rows, H, unres


def enrich(name, S, G, N):
    k, n, K = len(S & G), len(G), len(S)
    p = hypergeom.sf(k - 1, N, K, n) if k else 1.0
    return f"{name:<10}{K:>7} ({K/N:5.1%}) {k:>6}/{n} = {k/n:6.1%}   x{(k/n)/(K/N):4.1f}   p={p:.1e}"


def main(kpath):
    rows, H, unres = resolve(load_graur())
    print(f"Graur: {len(rows)} intrari | legate de o lema DEX '98: {sum(1 for r in rows if r['lemma'])} | "
          f"nerezolvate: {len(unres)}")
    for u in unres: print("   ?", u)
    k = json.load(open(kpath, encoding="utf8"))
    K, C, M = set(k["kernel"]), set(k["core"]), set(k["minset"])
    N = len(H)
    layers = {"MinSet": M, "Core": C, "Sateliți": K - C, "Kernel": K, "Rest": H - K}
    for sel, label in ((None, "TOATE"), ("C", "miez (fără cruce)"), ("M", "cercul mijlociu"), ("X", "cercul maximal")):
        G = {r["lemma"] for r in rows if r["lemma"] and (sel is None or r["cat"] == sel)}
        print(f"\n== Graur {label}: {len(G)} leme distincte")
        print(f"{'strat':<10}{'mărime (pondere)':>18}{'Graur în strat':>16}{'îmbogățire':>12}")
        for name, S in layers.items(): print(enrich(name, S, G, N))
    G = {r["lemma"] for r in rows if r["lemma"]}
    print("\nGraur în afara Kernel-ului:", sorted(G - K))
    json.dump([{**r} for r in rows], open("gold/graur1954/graur1954_lemmas.json", "w", encoding="utf8"),
              ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main(sys.argv[1])
