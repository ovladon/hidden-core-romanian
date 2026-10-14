#!/usr/bin/env python3
"""Form -> lemma maps of each dictionary, with the same rules as crossling/wiktionary_graph.py (entries marked as forms
of a lemma; inflection tables of lemma entries, ignoring forms listed for more than 10 lemmas). Used to compute lemma
frequencies by summing the frequencies of all inflected forms.

  python3 -I q1/lemma_forms.py <extract.jsonl.gz> <lang_code> <out.json.gz>
"""
import collections, gzip, json, re, sys, unicodedata

WORD = re.compile(r"^[^\W\d_]+$")
STRESS = re.compile("[̀́]")
SKIP = {"romanization", "table-tags", "inflection-template", "auxiliary", "class", "error-unknown-tag"}
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower()


def main(path, lang, dst):
    key = f'"lang_code": "{lang}"'
    form_of, table = collections.defaultdict(set), collections.defaultdict(set)
    with gzip.open(path, "rt", encoding="utf8") as f:
        for line in f:
            if key not in line: continue
            d = json.loads(line)
            if d.get("lang_code") != lang: continue
            w = nf(d.get("word"))
            if not WORD.match(w): continue
            for s in d.get("senses") or []:
                for fo in s.get("form_of") or []:
                    lem = nf(fo.get("word"))
                    if WORD.match(lem) and lem != w: form_of[w].add(lem)
            for fm in d.get("forms") or []:
                form = nf(fm.get("form"))
                if WORD.match(form) and form != w and not set(fm.get("tags") or []) & SKIP: table[form].add(w)
    m = {f: sorted(l) for f, l in form_of.items()}
    for f, l in table.items():
        if len(l) <= 10: m[f] = sorted(set(m.get(f, [])) | l)
    json.dump(m, gzip.open(dst, "wt", encoding="utf8"), ensure_ascii=False)
    print(f"{dst}: {len(m)} forme")


if __name__ == "__main__":
    main(*sys.argv[1:4])
