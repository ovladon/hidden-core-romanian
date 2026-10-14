#!/usr/bin/env python3
"""Converts the DEX (dexonline, sources 1-2) to the wiktextract JSONL format, so that the DEX can also be processed by
crossling/wiktionary_graph.py with exactly the same procedure as the Wiktionaries (control for the pipeline).

  - one entry per DEX definition: first sense, cleaned as in kernel.py (no examples, expressions, etymology);
  - part of speech from the first grammatical label (#s. f.#, #vb.#, #prep.# ...);
  - forms: the dexonline inflection tables of the headword (attached to its first entry).

  python3 crossling/dex_to_jsonl.py crossling/graphs/dex.jsonl.gz
  python3 crossling/dex_to_jsonl.py crossling/graphs/dex_nosyn.jsonl.gz --strip-synonyms   # contrafactual: fara cozi de sinonime
"""
import collections, gzip, json, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import kernel

kernel.MODE["first_sense"], kernel.MODE["no_expr"] = True, True
POS = [(r"^(s\.|subst\.)", "noun"), (r"^(vb\.|v\.)", "verb"), (r"^adj\. (dem|pos|nehot|interog|neg|pron|rel)", "det"),
       (r"^adj\.", "adj"), (r"^adv\.", "adv"), (r"^num\.", "num"), (r"^prep\.", "prep"), (r"^conj\.", "conj"),
       (r"^pron\.", "pron"), (r"^art\.", "article"), (r"^interj\.", "intj"), (r"^loc\.", "phrase")]


# coada de sinonime de la sfarsitul definitiei: "...; arbore, pom" (cuvinte simple separate prin virgula)
SYN_TAIL = re.compile(r";\s*[^\W\d_]+(?:-[^\W\d_]+)?(?:\s*,\s*[^\W\d_]+(?:-[^\W\d_]+)?){0,5}\s*$")


def main(dst, strip_synonyms=False):
    D = kernel.load_defs((1, 2))
    L = pd.read_pickle("data/Lexeme.pkl"); F = pd.read_pickle("data/InflectedForm.pkl")
    lexform = dict(zip(L.id, (kernel.norm(x) for x in L.formNoAccent)))
    forms = collections.defaultdict(set)
    for form, lid in zip(F.formNoAccent, F.lexemeId):
        lem = lexform.get(lid)
        if lem: forms[lem].add(kernel.norm(form))
    done, n = set(), 0
    with gzip.open(dst, "wt", encoding="utf8") as g:
        for lex, rep in zip(D.lexicon, D.internalRep):
            h = kernel.norm(lex).strip()
            tags = re.findall(r"#([^#]+)#", rep[:150])
            pos = next((p for rx, p in POS if tags and re.match(rx, tags[0].strip().lower())), None)
            if not h or pos is None: continue
            gloss = re.sub(r"\s+", " ", kernel.clean(rep)).strip(" ;,.*")
            gloss = re.sub(r"[@#$^]", "", gloss)
            if strip_synonyms:
                g2 = SYN_TAIL.sub("", gloss)
                STRIPPED[0] += g2 != gloss; gloss = g2
            if not gloss: continue
            e = {"word": h, "lang_code": "ro", "pos": pos, "senses": [{"glosses": [gloss]}],
                 "forms": [] if h in done else [{"form": f} for f in sorted(forms.get(h, ())) if f != h]}
            done.add(h)
            g.write(json.dumps(e, ensure_ascii=False) + "\n"); n += 1
    print(f"scrise {n} intrari in {dst}" + (f" | cozi de sinonime eliminate: {STRIPPED[0]}" if strip_synonyms else ""))


STRIPPED = [0]

if __name__ == "__main__":
    main(sys.argv[1], strip_synonyms="--strip-synonyms" in sys.argv)
