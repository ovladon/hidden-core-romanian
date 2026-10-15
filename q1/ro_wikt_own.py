#!/usr/bin/env python3
"""Q1: is the DEX surplus Romanian, or the DEX's? The Romanian Wiktionary copies most of its first definitions from the
DEX, but not all. Its definitions are split by their similarity to the DEX first sense of the same word (as in
crossling/dex_overlap.py): copied (>= 0.8), adapted (0.5-0.8), own (< 0.5 or no DEX entry). For each group: synonym
tails, synonym-only definitions, short segments, and short segments that are synonyms recorded by the dexonline
editors. Then a graph built only from the own definitions, with the procedure used for every dictionary.

  python3 q1/ro_wikt_own.py        # writes q1/ro_wikt_own.json and q1/cf/ro_wikt_own_* (graph and analysis)
"""
import collections, difflib, gzip, json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kernel
from c3_precision import synonyms, nf, TOKEN, SYN_TAIL, SYN_ONLY, SEG, CONTENT

kernel.MODE["first_sense"], kernel.MODE["no_expr"] = True, True
SRC = "crossling/graphs/ro_wiktionary.jsonl.gz"
words = lambda s: re.sub(r"[^\w ]", " ", s.lower()).split()


def first_gloss(d):
    real = [s for s in d.get("senses") or [] if s.get("glosses") and not s.get("form_of")
            and "form-of" not in (s.get("tags") or []) and "no-gloss" not in (s.get("tags") or [])]
    return real[0]["glosses"][-1] if real else None


def main():
    D = kernel.load_defs((1, 2))
    dex = {}
    for lex, rep in zip(D.lexicon, D.internalRep):
        h = kernel.norm(lex).strip()
        if h not in dex: dex[h] = re.sub(r"\s+", " ", kernel.clean(rep)).strip(" ;,.*").lower()
    SYN = synonyms()
    H = {l.strip() for l in open("crossling/graphs/ro_wikt_headwords.txt", encoding="utf8") if l.strip()}
    fmap = json.load(gzip.open("q1/forms/ro_wikt.json.gz", "rt", encoding="utf8"))
    cands = lambda t: set() if len(t) == 1 else ({t} | set(fmap.get(t, ()))) & H
    st = collections.defaultdict(collections.Counter)
    os.makedirs("q1/cf", exist_ok=True)
    out = gzip.open("q1/cf/ro_wikt_own.jsonl.gz", "wt", encoding="utf8")
    for line in gzip.open(SRC, "rt", encoding="utf8"):
        d = json.loads(line)
        if d.get("pos") not in CONTENT:
            out.write(line); continue                          # intrarile necontent (forme, cuvinte functionale) raman
        g = first_gloss(d)
        if not g: out.write(line); continue
        w = nf(d.get("word"))
        a, b = words(g), words(dex.get(w, ""))
        sim = difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0
        grp = "copied" if sim >= 0.8 else "adapted" if sim >= 0.5 else "own"
        if grp == "own": out.write(line)                       # graful "own": doar definitiile proprii
        c = st[grp]; c["definitions"] += 1
        gg = nf(g)
        if SYN_ONLY.match(gg): c["synonym_only"] += 1; continue
        if SYN_TAIL.search(gg): c["synonym_tail"] += 1; gg = SYN_TAIL.sub("", gg)
        short = [x for x in SEG.split(gg) if 0 < len(TOKEN.findall(x)) <= 2]
        c["with_short_segment"] += bool(short)
        if SYN.get(w):
            c["with_recorded_synonyms"] += 1
            c["short_with_recorded_synonym"] += any(cands(t) & SYN[w] for x in short for t in TOKEN.findall(x))
    out.close()
    res = {}
    for grp, c in st.items():
        n = c["definitions"]
        res[grp] = {"definitions": n, "synonym_tail_share": c["synonym_tail"] / n, "synonym_only_share": c["synonym_only"] / n,
                    "short_segment_share": c["with_short_segment"] / n,
                    "short_recorded_synonym_share": c["short_with_recorded_synonym"] / max(1, c["with_recorded_synonyms"])}
    FLAGS = {"C0": [], "C2": ["--strip-tails", "--drop-synonym-only"],
             "C3": ["--strip-tails", "--drop-synonym-only", "--strip-segments"]}
    for lvl, flags in FLAGS.items():
        pre = "q1/cf/ro_wikt_own" + ("" if lvl == "C0" else "_" + lvl)
        subprocess.run([sys.executable, "-I", "crossling/wiktionary_graph.py", "q1/cf/ro_wikt_own.jsonl.gz", "ro", pre,
                        *flags], check=True, capture_output=True)
        g = {}
        for r in ("freq", "all"):
            subprocess.run([sys.executable, "latent_structure.py", f"{pre}_{r}.tsv", "--headwords", f"{pre}_headwords.txt",
                            "--json", f"{pre}_{r}.json"], capture_output=True)
            x = json.load(open(f"{pre}_{r}.json")); N = x["headwords"]; k = len(x["kernel"])
            g[r] = {"headwords": N, "kernel_size": k, "kernel": k / N,
                    "minset_over_kernel": (x["minset_lower_bound"] + x["minset_upper_bound"]) / 2 / k,
                    "pairs_per_1000": 1000 * len(x["reciprocal_pairs"]) / N}
        res["own_graph_" + lvl] = g
    json.dump(res, open("q1/ro_wikt_own.json", "w", encoding="utf8"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
