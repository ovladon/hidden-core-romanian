#!/usr/bin/env python3
"""Aduna toate cifrele lucrarii intr-un singur results.json si deseneaza figurile.

Lucrarea, abstractul si prezentarea citesc DOAR din results.json, ca o rulare noua
(ex. dupa completarea dezambiguizarii) sa le actualizeze pe toate deodata.

  python3 collect_results.py            # scrie results/results.json + figures/*.png|svg
"""
import collections, json, os, re, subprocess, sys
import pandas as pd
from scipy.stats import hypergeom, binomtest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kernel, etym, layers

REG = {"freq": "src12_freq_noexpr_first", "ai": "src12_freq_noexpr_first_ai", "all": "src12_all_noexpr_first"}
MAIN = "ai"
# exemple variate de perechi reciproce (cate o pereche pe cuvant), pentru text si prezentare
PREFERRED = [("arbore", "copac"), ("amabil", "binevoitor"), ("primejdie", "risc"), ("balenă", "chit"), ("capelă", "paraclis"),
             ("apuca", "înșfăca"), ("consecință", "urmare"), ("asemănare", "similitudine"), ("năuci", "zăpăci"),
             ("preamări", "slăvi"), ("obscen", "trivial"), ("nedeslușit", "nelămurit")]
os.makedirs("results", exist_ok=True); os.makedirs("figures", exist_ok=True)


def graph(tag):
    out = collections.defaultdict(set)
    for line in open(f"out/graph_{tag}.tsv", encoding="utf8"):
        u, v = line.rstrip("\n").split("\t"); out[u].add(v)
    return out


LENS = {}


def lower_bound(tag):
    r = subprocess.run([sys.executable, "bounds.py", f"out/graph_{tag}.tsv", f"out/kernel_{tag}.json"],
                       capture_output=True, text=True).stdout
    m = re.search(r"lungimi: (\{.*?\})", r)
    if m: LENS[tag] = eval(m.group(1))
    return int(r.split("limita inferioara MinSet): ")[1].split()[0])


def ilp_bounds():
    """Limitele din rularile ILP (exact_minset.py): cea mai buna limita inferioara din toate jurnalele,
    cea mai buna limita superioara (solutia ILP reparata) si optimul exact, daca a fost demonstrat."""
    lb, ub, exact = None, None, None
    for f in ("out/exact_ai_run1.log", "out/exact_ai.log"):
        if not os.path.exists(f): continue
        for line in open(f, encoding="utf8"):
            m = re.search(r"limita inferioara=(\d+)", line)
            if m: lb = max(lb or 0, int(m.group(1)))
            m = re.search(r"limita superioara \(reparata\)=(\d+)", line)
            if m: ub = min(ub or 10**9, int(m.group(1)))
            m = re.search(r"OPTIM EXACT: MinSet = (\d+)", line)
            if m: exact = int(m.group(1))
    return lb, ub, exact


def best_minset(tag, k):
    """Cea mai mica multime de feedback gasita: solutia ILP reparata (daca exista si e mai mica) sau cea greedy."""
    f = f"out/minset_exact_{tag}.json"
    if os.path.exists(f):
        e = json.load(open(f, encoding="utf8"))
        if len(e["minset_best"]) < len(k["minset"]): return set(e["minset_best"])
    return set(k["minset"])


def main():
    R = {"regimes": {}}
    D = kernel.load_defs((1, 2))
    R["data"] = {"definitions": int(len(D)),
                 "from_dex98": int((D.sourceId == 1).sum()), "from_dex96": int((D.sourceId == 2).sum())}
    H = {kernel.norm(x).strip() for x in D.lexicon if x}
    H = {h for h in H if re.fullmatch(f"[{kernel.LETTERS}-]+", h)}
    R["data"]["headwords"] = len(H)
    open("out/headwords_src12.txt", "w", encoding="utf8").write("\n".join(sorted(H)) + "\n")
    for name, tag in REG.items():
        k = json.load(open(f"out/kernel_{tag}.json", encoding="utf8"))
        g = graph(tag)
        mutual = sorted({tuple(sorted((u, v))) for u in list(g) for v in g[u] if u in g.get(v, ()) and u != v})
        R["regimes"][name] = {"edges": k["edges"], "kernel": len(k["kernel"]), "core": len(k["core"]),
                              "minset_ub": len(k["minset"]), "minset_lb": lower_bound(tag),
                              "mutual_pairs": len(mutual), "unk_rate": k["unk_rate"], "ambig_rate": k["ambig_rate"]}
    lens = LENS.get(REG[MAIN], {})
    if lens: R["two_cycle_share"] = lens.get(2, 0) / R["regimes"][MAIN]["minset_lb"]
    R["tokens"] = json.load(open(f"out/kernel_{REG[MAIN]}.json", encoding="utf8")).get("tokens", 773719)
    lb, ub, exact = ilp_bounds()
    k = json.load(open(f"out/kernel_{REG[MAIN]}.json", encoding="utf8"))
    K, C, M = set(k["kernel"]), set(k["core"]), best_minset(REG[MAIN], k); N = len(H)
    A = R["regimes"]["ai"]
    A["minset_ub_greedy"] = A["minset_ub"]; A["minset_ub"] = len(M)
    if lb: A["minset_lb_ilp"] = lb
    if ub: A["minset_ub_ilp_log"] = ub
    if exact: A["minset_exact"] = exact
    L = {"MinSet": M, "Core": C, "Satellites": K - C, "Kernel": K, "Rest": H - K}
    R["layers"] = {n: {"size": len(s & H), "share": len(s & H) / N} for n, s in L.items()}

    def enrich(G):
        res = {}
        for n, s in L.items():
            kk, n_, KK = len(s & G), len(G), len(s & H)
            res[n] = {"hits": kk, "n": n_, "rate": kk / n_, "expected": KK / N,
                      "ratio": (kk / n_) / (KK / N), "p": float(hypergeom.sf(kk - 1, N, KK, n_)) if kk else 1.0}
        return res
    sw = layers.swadesh() & H
    R["swadesh"] = {"mapped": len(sw), "layers": enrich(sw), "outside_kernel": sorted(sw - K)}
    G = json.load(open("gold/graur1954/graur1954_lemmas.json", encoding="utf8"))
    R["graur"] = {"entries": len(G), "linked": sum(1 for r in G if r["lemma"]),
                  "distinct": len({r["lemma"] for r in G if r["lemma"]}),
                  "categories_transcribed": dict(collections.Counter(r["cat"] for r in G)),
                  "categories_published": {"C": 964, "M": 217, "X": 238}}
    for cat, lab in ((None, "all"), ("C", "core"), ("M", "middle"), ("X", "maximal")):
        Gs = {r["lemma"] for r in G if r["lemma"] and (cat is None or r["cat"] == cat)}
        R["graur"][lab] = enrich(Gs)
    glem = {r["lemma"] for r in G if r["lemma"]}
    R["graur"]["outside_kernel"] = sorted(glem - K)
    ori = collections.Counter(r["origin"] for r in G)
    R["graur"]["own_labels"] = {"latin": (ori["l"] + ori["r(l)"]) / len(G), "slavic": (ori["s"] + ori["r(s)"]) / len(G),
                                "slavic_s_only": ori["s"] / len(G), "international": ori["i"] / len(G),
                                "unknown": ori["n"] / len(G)}

    # etimologie (acelasi clasificator DEX pentru ambele multimi)
    e = {}
    for lex, rep in zip(D.lexicon, D.internalRep):
        h = kernel.norm(lex)
        if h not in e or e[h] in ("nedeterminat", "altele"): e[h] = etym.etym(rep)
    GR2 = {"l": "latin", "s": "slav", "m": "maghiar", "t": "turc", "g": "grecesc"}
    agree = {}
    for code, lab in GR2.items():
        ws = [r["lemma"] for r in G if r["lemma"] and r["origin"] == code]
        agree[lab] = {"n": len(ws), "agree": sum(e.get(w) == lab for w in ws) / max(1, len(ws))}
    g = graph(REG[MAIN]); outdeg = collections.Counter({u: len(v) for u, v in g.items()})
    top = [w for w, _ in outdeg.most_common(1419)]
    def comp(ws):
        c = collections.Counter(e.get(w, "nedeterminat") for w in ws)
        return {kk: v / len(ws) for kk, v in c.most_common()}
    R["etymology"] = {"classifier_agreement_with_graur": agree, "graur_list": comp(sorted(glem)),
                      "top1419_definers": comp(top), "graur_in_top1419": len(glem & set(top)),
                      "top_definers_sample": top[:60]}
    # perechile reciproce (regimul principal)
    pairs = [l.rstrip("\n").split("\t") for l in open(f"out/pairs_{REG[MAIN]}.tsv", encoding="utf8")]
    R["pairs"] = {"n": len(pairs), "derivational": sum(int(p[2]) for p in pairs) / len(pairs),
                  "examples": [list(c) for c in PREFERRED if c in {tuple(p[:2]) for p in pairs}]}
    # validarea dezambiguizarii
    R["validation"] = {"opus_random_content": 0.869, "opus_random_function": 0.797, "opus_random_n_defs": 300,
                       "opus_alpha_content": 0.897, "ai_coverage": None, "cost_usd": 13.32 + 5.38 + 1.0 + 3.0}
    try:
        h12 = json.load(open("ai/choices_haiku12.json", encoding="utf8"))
        R["validation"]["ai_choices"] = len(h12)
    except FileNotFoundError:
        pass
    # calibrare: aceeasi procedura pe WordNet (crossling/wordnet_graph.py + latent_structure.py --ilp) si DEX fara
    # cuvintele functionale (crossling/content_only.py), ca la Vincent-Lamarre et al. (2016)
    cal = {}
    for reg in ("freq", "all"):
        f = f"crossling/wordnet_{reg}.json"
        if os.path.exists(f):
            w = json.load(open(f, encoding="utf8"))
            cal[f"wordnet_{reg}"] = {"headwords": w["headwords"], "kernel": len(w["kernel"]), "core": len(w["core"]),
                                     "minset_lb": w["minset_lower_bound"], "minset_ub": w["minset_upper_bound"]}
    if os.path.exists("crossling/content_only.json"):
        cal["dex_content_only"] = json.load(open("crossling/content_only.json", encoding="utf8"))
        cal["dex_function_words"] = sum(1 for l in open("out/function_words_dex.txt", encoding="utf8") if l.strip())
    cal["vincent_lamarre_wordnet"] = {"headwords": 85195, "kernel": 9802, "core": 6392, "minset": 1094}
    R["calibration"] = cal
    json.dump(R, open("results/results.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(json.dumps({kk: R["regimes"][kk] for kk in R["regimes"]}, indent=1))
    print("scris results/results.json")


if __name__ == "__main__":
    main()
