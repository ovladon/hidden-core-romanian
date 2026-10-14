#!/usr/bin/env python3
"""Inspecteaza structura unui extras kaikki (wiktextract): coduri de limba, parti de vorbire, chei, un exemplu."""
import gzip, json, sys, collections
path, lang = sys.argv[1], sys.argv[2]
langs, pos, keys, sense_keys, n = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), 0
ex = None
with gzip.open(path, "rt", encoding="utf8") as f:
    for line in f:
        d = json.loads(line); n += 1
        langs[d.get("lang_code")] += 1
        if d.get("lang_code") == lang:
            pos[d.get("pos")] += 1; keys.update(d.keys())
            for s in d.get("senses", [])[:1]: sense_keys.update(s.keys())
            if ex is None and d.get("pos") == "noun" and d.get("forms"): ex = d
        if n >= 400000: break
print("intrari citite:", n, "| limbi:", langs.most_common(6))
print("pos:", pos.most_common(25))
print("chei:", keys.most_common(30)); print("chei sens:", sense_keys.most_common(20))
if ex:
    print("exemplu:", ex["word"], ex["pos"], [s.get("glosses") for s in ex["senses"][:2]], ex.get("forms", [])[:6])
