#!/usr/bin/env python3
"""Q1, task 3: are the short segments removed by counterfactual C3 synonyms of the headword?

Reference: the synonym relations recorded by the dexonline editors when they structure entries (table Relation,
type 1: a meaning of tree T1 has the synonym T2). The check is made on the DEX definitions used for the graphs
(crossling/graphs/dex.jsonl.gz, first sense of each content entry), with the C2 changes applied, as in C3.

For headwords that have at least one recorded synonym, a token "is a recorded synonym" if one of its candidate lemmas
(the dexonline inflection map) is recorded as a synonym of the headword. Three groups of definition material:
  tail      the synonym tails removed by C1 ("...; arbore, pom"), which are synonyms by construction (reference level)
  short     segments of at most two words between commas/semicolons, removed by C3
  long      the remaining segments (kept in C3)

  python3 -I q1/c3_precision.py              # writes q1/c3_precision.json
  python3 -I q1/c3_precision.py --variants   # and q1/cf/dex_C3syn.jsonl.gz, q1/cf/dex_C3non.jsonl.gz: the DEX with C2
                                             # applied and only the short segments that contain (C3syn) or do not
                                             # contain (C3non; only headwords with recorded synonyms) a recorded
                                             # synonym of the headword removed
"""
import collections, gzip, json, pickle, random, re, sys, unicodedata

STRESS = re.compile("[̀́]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower().strip()
TOKEN = re.compile(r"[^\W\d_]+")
WORD = re.compile(r"^[^\W\d_]+$")
CONTENT = {"noun", "verb", "adj", "adv", "num"}
SYN_WORD = r"[^\W\d_]+(?:-[^\W\d_]+)?"
SYN_TAIL = re.compile(r";\s*" + SYN_WORD + r"(?:\s*,\s*" + SYN_WORD + r"){0,5}\s*\.?\s*$")
SYN_ONLY = re.compile(r"^\s*" + SYN_WORD + r"(?:\s*[,;]\s*" + SYN_WORD + r"){0,4}\s*\.?\s*$")
SEG = re.compile(r"[,;]")


def synonyms():
    tree = pickle.load(open("data/Tree.pkl", "rb")); meaning = pickle.load(open("data/Meaning.pkl", "rb"))
    rel = pickle.load(open("data/Relation.pkl", "rb"))
    lemma = {i: nf(re.sub(r"\s*\(.*$", "", d)) for i, d in zip(tree.id, tree.description)}
    m2t = dict(zip(meaning.id, meaning.treeId))
    S = collections.defaultdict(set)
    for m, t, ty in zip(rel.meaningId, rel.treeId, rel.type):
        if ty != 1: continue
        a, b = lemma.get(m2t.get(m)), lemma.get(t)
        if a and b and a != b and WORD.match(a) and WORD.match(b): S[a].add(b); S[b].add(a)
    return S


def main():
    H = {l.strip() for l in open("crossling/graphs/dex_headwords.txt", encoding="utf8") if l.strip()}
    fmap = json.load(gzip.open("q1/forms/dex.json.gz", "rt", encoding="utf8"))
    cands = lambda t: set() if len(t) == 1 else ({t} | set(fmap.get(t, ()))) & H
    SYN = synonyms()
    units = {"tail": [], "short": [], "long": []}          # (headword, tokens)
    for line in gzip.open("crossling/graphs/dex.jsonl.gz", "rt", encoding="utf8"):
        d = json.loads(line)
        w = nf(d.get("word"))
        if d.get("pos") not in CONTENT or w not in H or not SYN.get(w): continue
        real = [s for s in d.get("senses") or [] if s.get("glosses") and not s.get("form_of")]
        if not real: continue
        g = nf(real[0]["glosses"][-1])
        if SYN_ONLY.match(g): continue
        m = SYN_TAIL.search(g)
        if m:
            for seg in SEG.split(m.group(0)):
                if TOKEN.findall(seg): units["tail"].append((w, TOKEN.findall(seg)))
            g = g[:m.start()]
        for seg in SEG.split(g):
            ts = TOKEN.findall(seg)
            if ts: units["short" if len(ts) <= 2 else "long"].append((w, ts))
    res = {"headwords_with_recorded_synonyms": len({w for k in units for w, _ in units[k]}),
           "synonym_pairs": sum(len(v) for v in SYN.values()) // 2}
    rng = random.Random(1); ex = {}
    for k, U in units.items():
        seg_hit = seg_n = tok_hit = tok_n = 0; miss = []
        for w, ts in U:
            hits = [bool(cands(t) & SYN[w]) for t in ts if cands(t) - {w}]
            if not hits: continue
            seg_n += 1; seg_hit += any(hits); tok_n += len(hits); tok_hit += sum(hits)
            if not any(hits) and k == "short": miss.append(f"{w}: {' '.join(ts)}")
        res[k] = {"segments": seg_n, "segments_with_recorded_synonym": seg_hit / seg_n if seg_n else None,
                  "tokens": tok_n, "tokens_recorded_synonym": tok_hit / tok_n if tok_n else None}
        if miss: ex[k + "_without_recorded_synonym"] = rng.sample(miss, min(25, len(miss)))
    res["examples"] = ex
    json.dump(res, open("q1/c3_precision.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "examples"}, indent=1))
    print("\n".join(ex.get("short_without_recorded_synonym", [])))
    if "--variants" in sys.argv: variants(H, cands, SYN)


def variants(H, cands, SYN):
    """Doua variante ale DEX-ului: C2 + scoaterea segmentelor scurte cu sinonim inregistrat / fara."""
    outs = {k: gzip.open(f"q1/cf/dex_{k}.jsonl.gz", "wt", encoding="utf8") for k in ("C3syn", "C3non")}
    n = collections.Counter()
    for line in gzip.open("crossling/graphs/dex.jsonl.gz", "rt", encoding="utf8"):
        d = json.loads(line)
        w = nf(d.get("word")); senses = d.get("senses") or []
        real = [i for i, s in enumerate(senses) if s.get("glosses") and not s.get("form_of")]
        if d.get("pos") not in CONTENT or not real:
            for f in outs.values(): f.write(line)
            continue
        g = nf(senses[real[0]]["glosses"][-1])
        if SYN_ONLY.match(g):                                   # C2: definitie formata numai din sinonime
            for f in outs.values(): f.write(line)               # (o scoate constructorul, cu --drop-synonym-only)
            continue
        g = SYN_TAIL.sub("", g).strip()                         # C1
        segs = [x for x in SEG.split(g)]
        def is_syn(x):
            return w in H and any(cands(t) & SYN.get(w, set()) for t in TOKEN.findall(x))
        short = lambda x: 0 < len(TOKEN.findall(x)) <= 2
        for k, f in outs.items():
            # C3non: doar la cuvintele-titlu cu sinonime inregistrate (la celelalte nu stim; segmentele raman)
            drop = (lambda x: is_syn(x)) if k == "C3syn" else (lambda x: bool(SYN.get(w)) and w in H and not is_syn(x))
            keep = [x.strip() for x in segs if not (short(x) and drop(x))]
            n[k] += len(keep) != len(segs)
            e = json.loads(line); e["senses"][real[0]]["glosses"][-1] = ", ".join(x for x in keep if x)
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    for f in outs.values(): f.close()
    print("definitii modificate:", dict(n))


if __name__ == "__main__":
    main()
