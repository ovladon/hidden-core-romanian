#!/usr/bin/env python3
"""Parts of speech of the headwords of a graph, from the lemma entries of the dictionary's own extract (for the
lenient accuracy criterion).

  python3 -I q1/pos_map.py <code> <extract.jsonl.gz> <lang_code>      # writes q1/pos/<code>.json.gz
"""
import collections, gzip, json, os, re, sys, unicodedata

STRESS = re.compile("[̀́]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower().strip()


def main(code, extract, lang):
    H = {l.strip() for l in open(f"crossling/graphs/{code}_headwords.txt", encoding="utf8") if l.strip()}
    pos = collections.defaultdict(set); key = f'"lang_code": "{lang}"'
    with gzip.open(extract, "rt", encoding="utf8") as f:
        for line in f:
            if key not in line: continue
            d = json.loads(line)
            w = nf(d.get("word"))
            if d.get("lang_code") != lang or w not in H or not d.get("pos"): continue
            # doar intrarile de lema: paginile de forme flexionare (ex. germana "Bäumen", plural de la "Baum") ar
            # adauga altor leme o parte de vorbire straina dupa trecerea la litere mici
            if any(s.get("glosses") and not s.get("form_of") and "form-of" not in (s.get("tags") or [])
                   for s in d.get("senses") or []):
                pos[w].add(d["pos"])
    os.makedirs("q1/pos", exist_ok=True)
    json.dump({w: sorted(p) for w, p in pos.items()}, gzip.open(f"q1/pos/{code}.json.gz", "wt", encoding="utf8"),
              ensure_ascii=False)
    print(code, len(pos), "of", len(H), "headwords with a part of speech")


if __name__ == "__main__":
    main(*sys.argv[1:4])
