#!/usr/bin/env python3
"""Cate glose din primele simturi au legaturi manuale (camp 'links' in wiktextract), pe limba."""
import gzip, json, sys, collections
path, lang, limit = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 300000
key = f'"lang_code": "{lang}"'
n = withl = 0; nl = 0; ex = None
with gzip.open(path, "rt", encoding="utf8") as f:
    for line in f:
        if key not in line: continue
        d = json.loads(line)
        if d.get("lang_code") != lang or d.get("pos") not in ("noun", "verb", "adj", "adv"): continue
        s = next((s for s in d.get("senses") or [] if s.get("glosses") and not s.get("form_of")), None)
        if not s: continue
        n += 1
        if s.get("links"):
            withl += 1; nl += len(s["links"])
            if ex is None: ex = (d["word"], s["glosses"][-1][:90], s["links"][:4])
        if n >= limit: break
print(lang, f"glose: {n} | cu legaturi: {withl} ({100*withl/max(1,n):.0f}%) | legaturi/glosa: {nl/max(1,withl):.1f} | exemplu: {ex}")
