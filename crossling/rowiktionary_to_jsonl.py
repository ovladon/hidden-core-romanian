#!/usr/bin/env python3
"""Converts the Romanian Wiktionary dump (ro.wiktionary.org, wikitext) to the wiktextract JSONL format used by
crossling/wiktionary_graph.py, so that Romanian Wiktionary is processed exactly like the other Wiktionaries.

For every page with a Romanian section ({{limba|ron}}) and every part-of-speech header in it, one entry is written:
  - the first definition line of the block, with the wiki markup removed (links keep their visible form);
  - definitions of the type "forma de plural pentru [[X]]" become form_of links to X (inflected-form pages);
  - the parameters of the inflection template ({{substantiv-ron|nom-pl=...}}, {{verb-ron|...}}) become forms.

  python3 -I crossling/rowiktionary_to_jsonl.py crossling/raw/ro/rowiktionary-latest-pages-articles.xml.bz2 \
          crossling/graphs/ro_wiktionary.jsonl.gz
"""
import bz2, gzip, json, re, sys

POS = {"substantiv": "noun", "verb": "verb", "adjectiv": "adj", "adverb": "adv", "numeral": "num",
       "numeral colectiv": "num", "pronume": "pron", "prepoziție": "prep", "conjuncție": "conj",
       "interjecție": "intj", "articol": "article", "nume propriu": "name", "prefix": "prefix", "sufix": "suffix",
       "abreviere": "abbrev", "locuțiune": "phrase", "expresie": "phrase", "cuvânt compus": "phrase",
       "locuțiune adverbială": "phrase", "locuțiune adjectivală": "phrase"}
HEADER = re.compile(r"\{\{-([^|}]+?)-(?:\|ron)?\}\}")
FORM_OF = re.compile(r"^(forma|formă)\b.*?\b(pentru|a lui|a verbului|a substantivului|a adjectivului|de la)\b", re.I)


def clean(s):
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)          # [[lemă|formă]] -> formă
    s = re.sub(r"\{\{[^{}]*\}\}", " ", s)
    s = s.replace("'''", "").replace("''", "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"^\s*(\([^()]*\)\s*)+", "", s)                         # etichete initiale: (bot.), (reg.)
    return re.sub(r"\s+", " ", s).strip()


def entries(title, text):
    m = re.search(r"==\s*\{\{limba\|ron\}\}\s*==(.*?)(?=\n==\s*\{\{limba\||\Z)", text, re.S)
    if not m: return
    sec = m.group(1)
    heads = [(h.group(1), h.start(), h.end()) for h in HEADER.finditer(sec) if h.group(1) in POS]
    for i, (h, a, b) in enumerate(heads):
        block = sec[b: heads[i + 1][1] if i + 1 < len(heads) else len(sec)]
        nxt = HEADER.search(block)                                      # pana la urmatoarea sectiune (-sin-, -trans- ...)
        body = block[:nxt.start()] if nxt else block
        forms = []
        for tm in re.finditer(r"\{\{(?:substantiv|verb|adjectiv)-ron(.*?)\}\}", body, re.S):
            for k, v in re.findall(r"\|\s*([\w-]+)\s*=\s*([^|}]*)", tm.group(1)):
                if k in ("gen", "cj"): continue
                for f in re.split(r"[,/;]|<br\s*/?>", v):
                    f = clean(f)
                    if f: forms.append({"form": f})
        line = next((l for l in body.split("\n") if re.match(r"#(?![:*#])", l)), None)
        if not line: continue
        raw = line.lstrip("#").strip()
        gloss = clean(raw)
        e = {"word": title, "lang_code": "ro", "lang": "Română", "pos": POS[h], "forms": forms}
        if FORM_OF.match(gloss):
            target = re.findall(r"\[\[([^\]|]+)", raw)
            e["senses"] = [{"glosses": [gloss], "form_of": [{"word": target[-1]}] if target else [], "tags": ["form-of"]}]
        else:
            e["senses"] = [{"glosses": [gloss]}]
        yield e


def main(src, dst):
    title, buf, intext, n = None, [], False, 0
    with bz2.open(src, "rt", encoding="utf8") as f, gzip.open(dst, "wt", encoding="utf8") as g:
        for line in f:
            mt = re.search(r"<title>(.*?)</title>", line)
            if mt: title = mt.group(1)
            if "<text" in line:
                intext = True; buf = [line.split(">", 1)[-1]]
            elif intext:
                buf.append(line)
            if intext and "</text>" in line:
                intext = False
                text = "".join(buf).split("</text>")[0].replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                for e in entries(title, text):
                    g.write(json.dumps(e, ensure_ascii=False) + "\n"); n += 1
    print(f"scrise {n} intrari in {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
