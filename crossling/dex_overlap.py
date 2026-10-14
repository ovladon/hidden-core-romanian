#!/usr/bin/env python3
"""Cat din Wiktionary-ul romanesc e preluat din DEX: similaritatea primei definitii cu primul sens DEX (acelasi cuvant)."""
import difflib, gzip, json, re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import kernel
kernel.MODE["first_sense"], kernel.MODE["no_expr"] = True, True
D = kernel.load_defs((1, 2))
dex = {}
for lex, rep in zip(D.lexicon, D.internalRep):
    h = kernel.norm(lex).strip()
    if h not in dex: dex[h] = re.sub(r"\s+", " ", kernel.clean(rep)).strip(" ;,.*").lower()
norm = lambda s: re.sub(r"[^\w ]", " ", s.lower()).split()
sims = []
for l in gzip.open(sys.argv[1], "rt", encoding="utf8"):
    e = json.loads(l)
    if e["pos"] not in ("noun", "verb", "adj", "adv") or e["senses"][0].get("form_of"): continue
    w = e["word"].lower()
    if w in dex:
        a, b = norm(e["senses"][0]["glosses"][0]), norm(dex[w])
        if a and b: sims.append(difflib.SequenceMatcher(None, a, b).ratio())
sims.sort(); n = len(sims)
json.dump({"compared": n, "share_ge_0.8": sum(s >= 0.8 for s in sims) / n, "share_ge_0.5": sum(s >= 0.5 for s in sims) / n,
           "median": sims[n // 2]}, open("crossling/ro_wikt_overlap.json", "w"), indent=1)
print(f"definitii comparate: {n} | similaritate >= 0.8: {sum(s >= 0.8 for s in sims)/n:.1%} | >= 0.5: {sum(s >= 0.5 for s in sims)/n:.1%} | mediana: {sims[n//2]:.2f}")
