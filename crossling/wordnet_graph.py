#!/usr/bin/env python3
"""Calibration: the same graph construction applied to Princeton WordNet 3.0 (NLTK), the one dictionary that
Vincent-Lamarre et al. (2016, Table 1) also analysed (Kernel 12%, Core 8%, MinSet 1%).

As in the DEX pipeline and in Vincent-Lamarre et al.:
  - a vertex is a single-word lemma (lower-case letters only; multiword expressions are excluded);
  - its definition is the union of the first (most frequent) sense of each part of speech;
  - function words (NLTK English stop-word list) are ignored, as in Vincent-Lamarre et al.;
  - each gloss token is mapped to the lemmas it can be an inflected form of (WordNet morphy);
    ambiguous tokens are linked to the most frequent candidate ("freq") or to all candidates ("all").

  python3 crossling/wordnet_graph.py          # writes crossling/wordnet_{freq,all}.tsv and wordnet_headwords.txt
"""
import collections, re
from nltk.corpus import stopwords, wordnet as wn

STOP = set(stopwords.words("english"))
WORD = re.compile(r"^[a-z]+$")
POS = ("n", "v", "a", "r")

lemmas = sorted({l.name().lower() for s in wn.all_synsets() for l in s.lemmas()})
heads = [w for w in lemmas if WORD.match(w) and w not in STOP]
H = set(heads)
freq = collections.Counter()
for s in wn.all_synsets():
    for l in s.lemmas():
        freq[l.name().lower()] += l.count()


def first_senses(w):
    """First (most frequent) synset of w for each part of speech; WordNet lists synsets by frequency."""
    out = []
    for p in POS:
        ss = wn.synsets(w, pos=p)
        if p == "a": ss = ss + [s for s in wn.synsets(w, pos="s") if s not in ss]
        if ss: out.append(ss[0])
    return out


def candidates(t):
    c = {t} & H
    for p in POS:
        for b in wn._morphy(t, p):
            if b in H: c.add(b)
    return c


arcs = {"freq": set(), "all": set()}
ntok = nunk = namb = 0
for v in heads:
    toks = []
    for s in first_senses(v):
        toks += re.findall(r"[a-z]+", s.definition().lower())
    for t in toks:
        if t in STOP: continue
        ntok += 1
        c = candidates(t)
        if not c: nunk += 1; continue
        if len(c) > 1: namb += 1
        pick = max(c, key=lambda x: (freq[x], x == t, x))
        if pick != v: arcs["freq"].add((pick, v))
        for u in c:
            if u != v: arcs["all"].add((u, v))
for k, A in arcs.items():
    with open(f"crossling/wordnet_{k}.tsv", "w", encoding="utf8") as f:
        for u, v in sorted(A): f.write(f"{u}\t{v}\n")
open("crossling/wordnet_headwords.txt", "w", encoding="utf8").write("\n".join(heads) + "\n")
print(f"WordNet {wn.get_version()}: {len(heads)} headwords | content tokens {ntok} | unknown {nunk / ntok:.1%} | "
      f"ambiguous {namb / ntok:.1%} | arcs freq {len(arcs['freq'])}, all {len(arcs['all'])}")
