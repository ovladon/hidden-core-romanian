#!/usr/bin/env python3
"""Dictionary graph of a monolingual Wiktionary (kaikki.org / wiktextract extract), built with the same procedure as
for the DEX and WordNet, so that the latent structures can be compared across languages.

Procedure (identical for every language):
  - vertices: single-word lemmas (letters only, case-folded) with a noun, verb, adjective, adverb or numeral entry;
    proper names, phrases, affixes, abbreviations and inflected-form entries are not vertices;
  - definition of a vertex: the first sense of each of its content entries (as the first sense of each DEX entry);
  - function words are ignored, as in Vincent-Lamarre et al. (2016): a word is a function word if it has a
    closed-class entry (preposition, pronoun, conjunction, article, determiner, particle, interjection) and either no
    content entry or is among the 300 most frequent tokens of the definitions; one-letter words are also ignored;
  - each definition token is mapped to the lemmas it can be a form of, using the dictionary's own inflection data
    (entries marked as forms of a lemma, and the inflection tables of lemma entries);
  - ambiguous tokens: regime "freq" links the candidate that is most frequent in the definitions, regime "all" links
    every candidate.

  python3 -I crossling/wiktionary_graph.py crossling/raw/it/it-extract.jsonl.gz it crossling/graphs/it
"""
import collections, gzip, json, os, re, sys, unicodedata

CONTENT = {"noun", "verb", "adj", "adv", "num"}
CLOSED = {"prep", "pron", "conj", "article", "det", "particle", "postp", "intj", "contraction", "prep_phrase"}
WORD = re.compile(r"^[^\W\d_]+$")
SKIP_TAGS = {"romanization", "table-tags", "inflection-template", "auxiliary", "class", "error-unknown-tag"}
TOKEN = re.compile(r"[^\W\d_]+")
STRESS = re.compile("[\u0300\u0301]")
# glose de tipul "plural of X" fara marcaj form_of (apar in Simple English Wiktionary): sunt forme flexionare, nu leme
FORMOF_EN = re.compile(r"^(?:the |an? )?(?:plural|past|present|third[- ]person|comparative|superlative|simple past|"
                       r"singular|gerund|participle)\b[^.;:]{0,40}?\bof ([^\W\d_]+)", re.I)


def nf(s):
    """NFC si fara accentele de pronuntie combinate (rusa le scrie cu U+0301 dupa vocala)."""
    return STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower()


# contrafactuale (q1): coada de sinonime "...; arbore, pom" si definitiile formate numai din sinonime ("arbore, pom")
SYN_WORD = r"[^\W\d_]+(?:-[^\W\d_]+)?"
SYN_TAIL = re.compile(r";\s*" + SYN_WORD + r"(?:\s*,\s*" + SYN_WORD + r"){0,5}\s*\.?\s*$")
SYN_ONLY = re.compile(r"^\s*" + SYN_WORD + r"(?:\s*[,;]\s*" + SYN_WORD + r"){0,4}\s*\.?\s*$")


SEG = re.compile(r"[,;]")


def strip_embedded(g):
    """C3: scoate orice segment (intre virgule / punct si virgula) format din cel mult doua cuvinte."""
    segs = [x for x in SEG.split(g) if len(TOKEN.findall(x)) > 2]
    return ", ".join(x.strip() for x in segs)


def main(path, lang, out_prefix, strip_tails=False, drop_synonym_only=False, strip_segments=False):
    cf = collections.Counter()
    defs = collections.defaultdict(list)          # lemma -> first glosses of its content entries
    lemma_forms = collections.defaultdict(set)    # form -> lemmas (entries marked as forms of a lemma)
    table_forms = collections.defaultdict(set)    # form -> lemmas (inflection tables of lemma entries)
    closed, content = set(), set()
    n = 0
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf8") as f:
        key = f'"lang_code": "{lang}"'
        for line in f:
            if key not in line: continue                 # filtru rapid; verificarea exacta urmeaza
            d = json.loads(line)
            if d.get("lang_code") != lang: continue
            n += 1
            w = nf(d.get("word"))
            if not WORD.match(w): continue
            pos = d.get("pos")
            senses = d.get("senses") or []
            for s in senses:                       # entries for inflected forms: form -> lemma
                for fo in s.get("form_of") or []:
                    lem = nf(fo.get("word"))
                    if WORD.match(lem) and lem != w: lemma_forms[w].add(lem)
            if pos in CLOSED: closed.add(w); continue
            if pos not in CONTENT: continue
            for s in senses:
                m = FORMOF_EN.match((s.get("glosses") or [""])[-1])
                if m and nf(m.group(1)) != w: lemma_forms[w].add(nf(m.group(1)))
            real = [s for s in senses if s.get("glosses") and not s.get("form_of")
                    and not FORMOF_EN.match(s["glosses"][-1]) and "form-of" not in (s.get("tags") or []) and "no-gloss" not in (s.get("tags") or [])]
            if not real: continue
            g = nf(real[0]["glosses"][-1]); cf["definitions"] += 1
            if SYN_ONLY.match(g):
                cf["synonym_only"] += 1
                if drop_synonym_only: continue
            if SYN_TAIL.search(g):
                cf["synonym_tail"] += 1
                if strip_tails: g = SYN_TAIL.sub("", g).strip()
            if strip_segments:
                cf["embedded_stripped"] += any(0 < len(TOKEN.findall(x)) <= 2 for x in SEG.split(g))
                g = strip_embedded(g)
            if not g: continue
            content.add(w)
            defs[w].append(g)
            for fm in d.get("forms") or []:        # inflection tables of the lemma
                form = nf(fm.get("form"))
                tags = set(fm.get("tags") or [])
                if WORD.match(form) and form != w and not tags & SKIP_TAGS:
                    table_forms[form].add(w)
    # o forma listata in tabelele a peste 10 leme e un artefact (ex. auxiliarul "essere" in tabelele verbelor italiene)
    for form, lems in table_forms.items():
        if len(lems) <= 10: lemma_forms[form] |= lems
    tokfreq = collections.Counter(t for g in defs.values() for x in g for t in TOKEN.findall(x.lower()))
    top = {t for t, _ in tokfreq.most_common(300)}
    func = {w for w in closed if w not in content or w in top} | {w for w in set(tokfreq) | content if len(w) == 1}
    H = sorted(w for w in content if w not in func)
    Hs = set(H)

    def cands(t):
        c = ({t} & Hs) | (lemma_forms.get(t, set()) & Hs)
        return c

    # frecventa unui candidat: aparitiile formei lui in definitii + tokenii care trimit doar la el
    score = collections.Counter({w: tokfreq.get(w, 0) for w in H})
    for t, k in tokfreq.items():
        c = cands(t)
        if len(c) == 1: score[next(iter(c))] += k
    arcs = {"freq": set(), "all": set()}
    ntok = nunk = namb = 0
    for v in H:
        for g in defs[v]:
            for t in TOKEN.findall(g.lower()):
                if t in func: continue
                ntok += 1
                c = cands(t)
                if not c: nunk += 1; continue
                if len(c) > 1: namb += 1
                pick = max(c, key=lambda x: (score[x], x == t, x))
                if pick != v: arcs["freq"].add((pick, v))
                arcs["all"].update((u, v) for u in c if u != v)
    os.makedirs(os.path.dirname(out_prefix), exist_ok=True)
    for k, A in arcs.items():
        with open(f"{out_prefix}_{k}.tsv", "w", encoding="utf8") as f:
            for u, v in sorted(A): f.write(f"{u}\t{v}\n")
    with open(f"{out_prefix}_headwords.txt", "w", encoding="utf8") as f:
        f.write("\n".join(H) + "\n")
    stats = {"lang": lang, "entries": n, "headwords": len(H), "function_words": len(func), "tokens": ntok,
             "unknown_rate": nunk / max(1, ntok), "ambiguous_rate": namb / max(1, ntok),
             "arcs_freq": len(arcs["freq"]), "arcs_all": len(arcs["all"]),
             "mean_definition_tokens": ntok / max(1, len(H)),
             "definitions": cf["definitions"], "synonym_tail_share": cf["synonym_tail"] / max(1, cf["definitions"]),
             "synonym_only_share": cf["synonym_only"] / max(1, cf["definitions"]),
             "embedded_stripped_share": cf["embedded_stripped"] / max(1, cf["definitions"]),
             "counterfactual": {"strip_tails": strip_tails, "drop_synonym_only": drop_synonym_only,
                                "strip_segments": strip_segments}}
    json.dump(stats, open(f"{out_prefix}_stats.json", "w"), indent=1)
    print(json.dumps(stats))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], strip_tails="--strip-tails" in sys.argv,
         drop_synonym_only="--drop-synonym-only" in sys.argv, strip_segments="--strip-segments" in sys.argv)
