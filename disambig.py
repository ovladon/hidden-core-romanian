#!/usr/bin/env python3
"""Pasul 2: un model citeste fiecare definitie DEX '98 si alege lema corecta pentru cuvintele ambigue.

O forma ca "are" poate veni din "avea" sau din "ara"; regula frecventei alege uneori gresit.
Modelul primeste definitia intreaga (contextul) si variantele posibile cu partea de vorbire,
si raspunde doar cu numarul variantei. Fiecare raspuns brut se salveaza (reluabil, auditabil).

  export ANTHROPIC_API_KEY=...             # cheia nu se scrie in fisiere
  python3 disambig.py --pilot 20                    # masoara costul pe 20 de cereri
  python3 disambig.py                               # rularea completa
  python3 disambig.py --model claude-opus-5 --sample 400 --tag opus_sample   # validare
"""
import argparse, collections, json, os, random, re, sys, time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kernel
from llm import ask

POS = {"M": "subst.", "F": "subst.", "N": "subst.", "MF": "subst.", "SF": "subst.", "FF": "subst.",
       "NL": "subst.", "A": "adj.", "AF": "adj.", "AM": "adj.", "AN": "adj.", "V": "verb", "VT": "verb",
       "P": "pron.", "PT": "pron."}
PRICE = {"claude-haiku-4-5-20251001": (1.0, 5.0), "claude-opus-5": (5.0, 25.0), "claude-sonnet-5": (3.0, 15.0)}
PER_REQ = 15

INSTR = (
    "Ești lexicograf. Pentru fiecare definiție din DEX de mai jos, unele cuvinte sunt ambigue: "
    "aceeași formă poate aparține mai multor leme. Alege, în contextul definiției, lema din care "
    "provine fiecare cuvânt marcat.\n"
    "Răspunde DOAR cu câte o linie de forma ID.k=n (ID = numărul definiției, k = numărul cuvântului, "
    "n = numărul variantei alese). De regulă alegi O SINGURĂ variantă. Doar dacă același cuvânt apare "
    "de mai multe ori în definiție, cu funcții diferite, dai variantele respective separate prin "
    "virgulă (ID.k=n,m). Dacă nicio variantă nu se "
    "potrivește, scrie ID.k=0.\n"
    "Atenție la «a»: marca infinitivului (A face, de a merge) și prepoziția nu au variantă → 0; "
    "«a» înaintea unui genitiv (parte a corpului) → al; «a» auxiliar (a fost, a făcut) → avea. "
    "La «o»: articol sau numeral → un; pronume (o vede) → el. Fără explicații.\n\n")


def headwords(D):
    H = {kernel.norm(x).strip() for x in D.lexicon if x}
    return {h for h in H if re.fullmatch(f"[{kernel.LETTERS}-]+", h)}


def build_items(sources=(1, 2), reuse=None, reuse_sources=(1,)):
    """reuse: alegeri deja platite (cheie "lema\ttoken"). Le pastram cand varianta de raspuns e aceeasi
    ca la rularea veche; trimitem la model doar ce e nou sau ce si-a schimbat variantele."""
    kernel.MODE["first_sense"], kernel.MODE["no_expr"] = True, True
    D = kernel.load_defs(sources)
    L = pd.read_pickle("data/Lexeme.pkl"); F = pd.read_pickle("data/InflectedForm.pkl")
    H = headwords(D)
    H_old = headwords(kernel.load_defs(reuse_sources)) if reuse is not None else set()
    lexform = dict(zip(L.id, (kernel.norm(x) for x in L.formNoAccent)))
    pos = collections.defaultdict(set)
    for f_, mt, desc in zip(L.formNoAccent, L.modelType, L.description):
        p = POS.get(mt) or (desc.strip() if mt in ("I", "T", "IL") and desc and desc.strip() else "")
        if p: pos[kernel.norm(f_)].add(p)
    form2lem = collections.defaultdict(set); old2lem = collections.defaultdict(set)
    for form, lid in zip(F.formNoAccent, F.lexemeId):
        lem = lexform.get(lid)
        if lem in H: form2lem[kernel.norm(form)].add(lem)
        if lem in H_old: old2lem[kernel.norm(form)].add(lem)
    for h in H: form2lem[h].add(h)
    for h in H_old: old2lem[h].add(h)
    kept = {}
    tokre = re.compile(f"[{kernel.LETTERS}]+(?:-[{kernel.LETTERS}]+)*")
    items = []
    for lex, rep, did in zip(D.lexicon, D.internalRep, D.id):
        h = kernel.norm(lex).strip()
        if h not in H: continue
        text = re.sub(r"\s+", " ", kernel.clean(rep)).strip()
        amb, seen = [], set()
        for t in tokre.findall(kernel.norm(text)):
            c = form2lem.get(t)
            if c and len(c) > 1 and t not in seen:
                seen.add(t)
                k = f"{h}\t{t}"
                if reuse is not None and k in reuse and old2lem.get(t) == c:
                    kept[k] = reuse[k]; continue           # aceeasi intrebare, raspuns deja platit
                amb.append((t, sorted(c)))
        if amb:
            items.append({"def_id": int(did), "head": h, "text": text[:600], "amb": amb})
    if reuse is not None:
        return items, pos, kept
    return items, pos


def render(batch, pos):
    out = [INSTR]
    for i, it in enumerate(batch, 1):
        out.append(f"[{i}] Cuvânt-titlu: {it['head']}\nDefiniție: {it['text']}")
        for k, (t, cands) in enumerate(it["amb"], 1):
            opts = " ".join(f"({n}) {c}" + (f" [{', '.join(sorted(pos[c]))[:40]}]" if pos[c] else "")
                            for n, c in enumerate(cands, 1))
            out.append(f"  {i}.{k} «{t}»: {opts}")
        out.append("")
    return "\n".join(out)


def parse(resp, batch):
    got = {}
    for i, k, ns in re.findall(r"(\d+)\.(\d+)[ \t]*=[ \t]*(\d+(?:[ \t]*,[ \t]*\d+)*)", resp or ""):
        i, k = int(i), int(k)
        if 1 <= i <= len(batch) and 1 <= k <= len(batch[i - 1]["amb"]):
            t, cands = batch[i - 1]["amb"][k - 1]
            picks = sorted({cands[int(n) - 1] for n in re.findall(r"\d+", ns) if 1 <= int(n) <= len(cands)})
            got[(batch[i - 1]["def_id"], t)] = picks            # [] = niciuna: tokenul se elimina
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    ap.add_argument("--tag", default="haiku")
    ap.add_argument("--pilot", type=int, default=0, help="doar N cereri, pentru estimarea costului")
    ap.add_argument("--sample", type=int, default=0, help="doar N definitii aleatoare (validare)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--sources", default="1,2")
    ap.add_argument("--reuse", help="alegeri vechi de refolosit (ex. ai/choices_haiku.json, rulate pe sursa 1)")
    args = ap.parse_args()
    key = os.environ.get("ANTHROPIC_API_KEY") or sys.exit("lipseste ANTHROPIC_API_KEY")

    sources = tuple(int(x) for x in args.sources.split(","))
    kept = {}
    if args.reuse:
        items, pos, kept = build_items(sources, json.load(open(args.reuse, encoding="utf8")))
        print(f"refolosite din {args.reuse}: {len(kept)} alegeri", flush=True)
    else:
        items, pos = build_items(sources)
    if args.sample:
        random.seed(2026); items = random.sample(items, args.sample)
    batches = [items[i:i + PER_REQ] for i in range(0, len(items), PER_REQ)]
    if args.pilot: batches = batches[:args.pilot]
    namb = sum(len(it["amb"]) for b in batches for it in b)
    print(f"{sum(len(b) for b in batches)} definitii cu cuvinte ambigue | {namb} decizii | "
          f"{len(batches)} cereri ({args.model})", flush=True)

    os.makedirs("ai", exist_ok=True)
    raw_path = f"ai/raw_{args.tag}.jsonl"
    done = set()
    if os.path.exists(raw_path):
        for line in open(raw_path, encoding="utf8"):
            r = json.loads(line)
            if not r.get("err"): done.add(r["batch"])
    todo = [(i, b) for i, b in enumerate(batches) if i not in done]
    print(f"deja facute: {len(done)} | de facut: {len(todo)}", flush=True)

    tin = tout = 0; t0 = time.time()
    with open(raw_path, "a", encoding="utf8") as fo, ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(ask, render(b, pos), args.model, "anthropic", key): (i, b) for i, b in todo}
        for n, (f, (i, b)) in enumerate(((f, futs[f]) for f in futs), 1):
            o, a, c, e = f.result(); tin += a; tout += c
            fo.write(json.dumps({"batch": i, "def_ids": [it["def_id"] for it in b], "resp": o,
                                 "tin": a, "tout": c, "err": e}, ensure_ascii=False) + "\n"); fo.flush()
            if n % 50 == 0 or n == len(todo):
                pi, po = PRICE.get(args.model, (0, 0))
                print(f"  {n}/{len(todo)} cereri | {tin} in / {tout} out | ~${tin*pi/1e6+tout*po/1e6:.2f} | "
                      f"{time.time()-t0:.0f}s", flush=True)

    # --- alegeri finale, din toate raspunsurile salvate
    byb = {}
    for line in open(raw_path, encoding="utf8"):
        r = json.loads(line)
        if not r.get("err"): byb[r["batch"]] = r["resp"]
    choices, nmiss = {}, 0
    for i, b in enumerate(batches):
        if i not in byb: continue
        got = parse(byb[i], b)
        for it in b:
            for t, _ in it["amb"]:
                if (it["def_id"], t) in got:
                    choices[f"{it['head']}\t{t}"] = got[(it["def_id"], t)]
                else:
                    nmiss += 1
    choices = {**kept, **choices}
    json.dump(choices, open(f"ai/choices_{args.tag}.json", "w"), ensure_ascii=False)
    pi, po = PRICE.get(args.model, (0, 0))
    print(f"alegeri: {len(choices)} | fara raspuns valid: {nmiss} | cost sesiune ~${tin*pi/1e6+tout*po/1e6:.2f}")
    if args.pilot and batches:
        per = (tin * pi + tout * po) / 1e6 / max(1, len(todo))
        total = len([items[i:i + PER_REQ] for i in range(0, len(items), PER_REQ)])
        print(f"estimare rulare completa: {total} cereri x ${per:.4f} = ~${per*total:.2f}")


if __name__ == "__main__":
    main()
