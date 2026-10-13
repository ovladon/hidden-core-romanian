#!/usr/bin/env python3
"""Perechile care se definesc reciproc (2-cicluri): cate sunt, cat de rare, cat sunt derivate."""
import sys, json, collections, os
import pandas as pd

def norm(s): return (s or "").lower().replace("ş","ș").replace("ţ","ț").strip()

def main(graph, kern):
    out = collections.defaultdict(set)
    for line in open(graph, encoding="utf8"):
        u, v = line.rstrip("\n").split("\t"); out[u].add(v)
    pairs = sorted({tuple(sorted((u, v))) for u in list(out) for v in out[u] if u in out.get(v, ()) and u != v})
    L = pd.read_pickle("data/Lexeme.pkl")
    fr = collections.defaultdict(float)
    for f, x in zip(L.formNoAccent, L.frequency): fr[norm(f)] = max(fr[norm(f)], x or 0)
    def deriv(a, b):
        n = 0
        for x, y in zip(a, b):
            if x != y: break
            n += 1
        return n >= max(4, min(len(a), len(b)) - 3)
    d = sum(deriv(a, b) for a, b in pairs)
    k = json.load(open(kern, encoding="utf8")); K = set(k["kernel"]); C = set(k["core"])
    inCore = sum(a in C and b in C for a, b in pairs)
    sat = sum((a in K and a not in C) or (b in K and b not in C) for a, b in pairs)
    print(f"perechi care se definesc reciproc: {len(pairs)}")
    print(f"  aparent derivate (rădăcină comună): {d} ({d/len(pairs):.0%})")
    print(f"  ambele în Core: {inCore} | cel puțin una în Sateliți: {sat}")
    os.makedirs("out", exist_ok=True)
    tag = os.path.basename(graph).replace("graph_", "").replace(".tsv", "")
    with open(f"out/pairs_{tag}.tsv", "w", encoding="utf8") as f:
        for a, b in pairs: f.write(f"{a}\t{b}\t{int(deriv(a,b))}\n")
    print(f"scris out/pairs_{tag}.tsv")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
