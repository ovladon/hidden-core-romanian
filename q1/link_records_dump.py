#!/usr/bin/env python3
"""Records for q1/links_gold.py for Wiktionary editions whose extracts lost the editors' links.

The first sense of each content entry is taken from the wiktextract extract, with the same rules as
crossling/wiktionary_graph.py. Its links are recovered from the wikitext dump of the same edition: in the page of the
word, the line whose text (wiki markup removed) best matches the gloss is located, and the links [[target|surface]]
on that line are kept (match: token-sequence similarity >= 0.8). The method is the same for every edition, whatever
its page layout.

  python3 -I q1/link_records_dump.py <extract.jsonl.gz> <lang> <dump.xml.bz2> <out.jsonl.gz>
"""
import bz2, difflib, gzip, json, re, sys, unicodedata

CONTENT = {"noun", "verb", "adj", "adv", "num"}
CLOSED = {"prep", "pron", "conj", "article", "det", "particle", "postp", "intj", "contraction", "prep_phrase"}
WORD = re.compile(r"^[^\W\d_]+$")
STRESS = re.compile("[̀́]")
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower()
toks = lambda s: re.findall(r"[^\W\d_]+", nf(s))


def dewiki(line):
    s = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", " ", line)
    for _ in range(3): s = re.sub(r"\{\{[^{}]*\}\}", " ", s)
    s = LINK.sub(lambda m: m.group(2) or m.group(1), s)
    return re.sub(r"'{2,}|<[^>]+>", " ", s)


def main(extract, lang, dump, dst):
    key = f'"lang_code": "{lang}"'; first, closed = {}, set()
    with gzip.open(extract, "rt", encoding="utf8") as f:
        for line in f:
            if key not in line: continue
            d = json.loads(line)
            if d.get("lang_code") != lang: continue
            w = nf(d.get("word"))
            if not WORD.match(w): continue
            if d.get("pos") in CLOSED: closed.add(w); continue
            if d.get("pos") not in CONTENT: continue
            real = [s for s in d.get("senses") or [] if s.get("glosses") and not s.get("form_of")
                    and "form-of" not in (s.get("tags") or []) and "no-gloss" not in (s.get("tags") or [])]
            if real: first.setdefault(w, []).append((d.get("word"), real[0]["glosses"][-1]))
    titles = {orig for v in first.values() for orig, _ in v}
    found, n = {}, 0
    title, buf, intext = None, [], False
    with bz2.open(dump, "rt", encoding="utf8") as f:
        for line in f:
            mt = re.search(r"<title>(.*?)</title>", line)
            if mt: title = mt.group(1).replace("&amp;", "&")
            if "<text" in line: intext = title in titles; buf = [line.split(">", 1)[-1]] if intext else []
            elif intext: buf.append(line)
            if intext and "</text>" in line:
                intext = False
                text = "".join(buf).split("</text>")[0].replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&quot;", '"')
                lines = [l for l in text.split("\n") if "[[" in l]
                found[title] = [(toks(dewiki(l)), l) for l in lines]
    with gzip.open(dst, "wt", encoding="utf8") as g:
        for w, entries in first.items():
            for orig, gloss in entries:
                gt, links = toks(gloss), []
                if gt and orig in found:
                    best, bl = 0.0, None
                    for lt, raw in found[orig]:
                        if not lt: continue
                        r = difflib.SequenceMatcher(None, gt, lt, autojunk=False).ratio()
                        if r > best: best, bl = r, raw
                    if best >= 0.8:
                        links = [[(s or t).strip(), t.strip()] for t, s in LINK.findall(bl) if ":" not in t]
                        n += 1
                g.write(json.dumps({"word": w, "gloss": gloss, "links": links}, ensure_ascii=False) + "\n")
    open(dst.replace(".jsonl.gz", "_closed.txt"), "w", encoding="utf8").write("\n".join(sorted(closed)) + "\n")
    print(f"{dst}: {sum(len(v) for v in first.values())} intrari | cu legaturi regasite: {n}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
