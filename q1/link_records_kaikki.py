#!/usr/bin/env python3
"""Records for q1/links_gold.py from a wiktextract extract that keeps the editors' links (the English edition):
first sense of each content entry, exactly as chosen by crossling/wiktionary_graph.py, with its links.

  python3 -I q1/link_records_kaikki.py <extract.jsonl.gz> <lang> <out.jsonl.gz>
"""
import gzip, json, re, sys, unicodedata

CONTENT = {"noun", "verb", "adj", "adv", "num"}
CLOSED = {"prep", "pron", "conj", "article", "det", "particle", "postp", "intj", "contraction", "prep_phrase"}
WORD = re.compile(r"^[^\W\d_]+$")
STRESS = re.compile("[̀́]")
FORMOF_EN = re.compile(r"^(?:the |an? )?(?:plural|past|present|third[- ]person|comparative|superlative|simple past|"
                       r"singular|gerund|participle)\b[^.;:]{0,40}?\bof ([^\W\d_]+)", re.I)
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower()


def main(path, lang, dst):
    key = f'"lang_code": "{lang}"'; n = 0; closed = set()
    with gzip.open(path, "rt", encoding="utf8") as f, gzip.open(dst, "wt", encoding="utf8") as g:
        for line in f:
            if key not in line: continue
            d = json.loads(line)
            if d.get("lang_code") != lang: continue
            w = nf(d.get("word"))
            if not WORD.match(w): continue
            if d.get("pos") in CLOSED: closed.add(w); continue
            if d.get("pos") not in CONTENT: continue
            real = [s for s in d.get("senses") or [] if s.get("glosses") and not s.get("form_of")
                    and not FORMOF_EN.match(s["glosses"][-1]) and "form-of" not in (s.get("tags") or [])
                    and "no-gloss" not in (s.get("tags") or [])]
            if not real: continue
            s = real[0]
            g.write(json.dumps({"word": w, "gloss": s["glosses"][-1], "links": s.get("links") or []}, ensure_ascii=False) + "\n")
            n += 1
    open(dst.replace(".jsonl.gz", "_closed.txt"), "w", encoding="utf8").write("\n".join(sorted(closed)) + "\n")
    print(f"{dst}: {n} intrari | cuvinte de clasa inchisa: {len(closed)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
