#!/usr/bin/env python3
"""Straturile (Rest / Satelit / Core / MinSet) comparate cu liste de experti si cu frecventa."""
import json, re, sys, collections
import pandas as pd

def norm(s): return (s or "").lower().replace("ş","ș").replace("ţ","ț").strip()

def swadesh():
    raw = json.load(open("gold/swadesh_ro_raw.json", encoding="utf8"))
    out = set()
    for row in raw:
        for item in re.split(r"[,;/]", re.sub(r"\([^)]*\)", "", row[2])):
            w = norm(item)
            if w and " " not in w: out.add(w)
    return out

def main(path):
    k = json.load(open(path, encoding="utf8"))
    K, C, M = set(k["kernel"]), set(k["core"]), set(k["minset"])
    L = pd.read_pickle("data/Lexeme.pkl")
    fr = collections.defaultdict(float)
    for f, x in zip(L.formNoAccent, L.frequency): fr[norm(f)] = max(fr[norm(f)], x or 0)
    import kernel; D = kernel.load_defs((1, 2))
    H = {norm(x) for x in D.lexicon if x}
    H = {h for h in H if re.fullmatch(r"[a-zăâîșțáéíóúàèìòù-]+", h)}
    S = K - C; R = H - K
    layers = {"MinSet": M, "Core": C, "Sateliți": S, "Kernel": K, "Rest": R}
    sw = swadesh() & H
    print(f"dicționar: {len(H)} | Swadesh mapate: {len(sw)}")
    print(f"{'strat':<10}{'n':>7}{'% dicț.':>9}{'Swadesh în strat':>18}{'îmbogățire':>12}{'frecv. medie':>14}")
    for name, s in layers.items():
        n = len(s & H); share = n / len(H)
        hit = len(sw & s); rate = hit / len(sw)
        f = sum(fr[w] for w in s) / max(1, n)
        print(f"{name:<10}{n:>7}{share:>8.1%}{hit:>9} ({rate:>5.0%}){rate/share if share else 0:>11.1f}x{f:>14.2f}")
    print("Swadesh în afara Kernel-ului:", sorted(sw - K)[:40])

if __name__ == "__main__":
    main(sys.argv[1])
