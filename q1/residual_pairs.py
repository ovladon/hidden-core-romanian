#!/usr/bin/env python3
"""Q1, task 3: what kind of reciprocal definitions remain after synonym tails and synonym-only definitions are removed
(counterfactual C2), in the DEX and in the other dictionaries?

For every reciprocal pair (u, v) of the C2 graph (q1/cf/<code>_C2_freq.json), each direction (u in the definition of v,
v in the definition of u) is classified from the definition text (with the C2 changes applied):
  embedded_synonym  u forms a bare segment of at most two words between commas/semicolons inside the definition
  derivational      u and v share a stem (common prefix >= 5 letters), e.g. masticare/masticatie
  parenthetical     u occurs only inside parentheses (labels such as "(despre plante)")
  analytic          any other occurrence
A pair is labelled by the first category, in this order, that describes either of its two directions.

  python3 -I q1/residual_pairs.py <code> [<code> ...]       # writes q1/residual_pairs.json
"""
import collections, gzip, json, os, re, sys, unicodedata

STRESS = re.compile("[̀́]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower().strip()
TOKEN = re.compile(r"[^\W\d_]+")
SYN_WORD = r"[^\W\d_]+(?:-[^\W\d_]+)?"
SYN_TAIL = re.compile(r";\s*" + SYN_WORD + r"(?:\s*,\s*" + SYN_WORD + r"){0,5}\s*\.?\s*$")
SYN_ONLY = re.compile(r"^\s*" + SYN_WORD + r"(?:\s*[,;]\s*" + SYN_WORD + r"){0,4}\s*\.?\s*$")
ORDER = ["embedded_synonym", "derivational", "parenthetical", "analytic"]


def prefix_len(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y: break
        n += 1
    return n


def analyse(code):
    H = {l.strip() for l in open(f"crossling/graphs/{code}_headwords.txt", encoding="utf8") if l.strip()}
    fmap = json.load(gzip.open(f"q1/forms/{code}.json.gz", "rt", encoding="utf8"))
    closed = {l.strip() for l in open(f"q1/human/{code}_records_closed.txt", encoding="utf8") if l.strip()}
    func = closed - H
    lem = lambda t: set() if (t in func or len(t) == 1) else ({t} | set(fmap.get(t, ()))) & H
    defs = collections.defaultdict(list)
    for r in (json.loads(l) for l in gzip.open(f"q1/human/{code}_records.jsonl.gz", "rt", encoding="utf8")):
        g = nf(r["gloss"])
        if SYN_ONLY.match(g): continue
        g = SYN_TAIL.sub("", g).strip()
        if g: defs[nf(r["word"])].append(g)

    def how(u, v):
        """Cum apare u in definitia lui v (prima ocurenta gasita)."""
        if prefix_len(u, v) >= 5: return "derivational"
        kinds = []
        for g in defs.get(v, []):
            depth = 0; plain = re.sub(r"\([^()]*\)", " ", g)
            if any(u in lem(t) for t in TOKEN.findall(plain)):
                for seg in re.split(r"[,;]", plain):
                    ts = TOKEN.findall(seg)
                    if 0 < len(ts) <= 2 and any(u in lem(t) for t in ts): return "embedded_synonym"
                kinds.append("analytic")
            elif any(u in lem(t) for t in TOKEN.findall(g)):
                kinds.append("parenthetical")
        return "analytic" if "analytic" in kinds else (kinds[0] if kinds else "analytic")

    d = json.load(open(f"q1/cf/{code}_C2_freq.json", encoding="utf8"))
    pairs = d["reciprocal_pairs"]; N = d["headwords"]
    cnt = collections.Counter(); ex = collections.defaultdict(list)
    for u, v in pairs:
        a, b = how(u, v), how(v, u)
        lab = min((a, b), key=ORDER.index)
        cnt[lab] += 1
        if len(ex[lab]) < 6: ex[lab].append(f"{u}–{v}")
    return {"headwords": N, "pairs": len(pairs), "pairs_per_1000": 1000 * len(pairs) / N,
            "by_type_per_1000": {k: 1000 * cnt[k] / N for k in ORDER},
            "share": {k: cnt[k] / max(1, len(pairs)) for k in ORDER}, "examples": dict(ex)}


if __name__ == "__main__":
    path = "q1/residual_pairs.json"
    out = json.load(open(path)) if os.path.exists(path) else {}
    for code in sys.argv[1:]:
        out[code] = analyse(code)
        r = out[code]
        print(f"{code:8s} perechi/1000 {r['pairs_per_1000']:5.1f} | " +
              " | ".join(f"{k} {r['by_type_per_1000'][k]:4.1f}" for k in ORDER) + f" | ex: {r['examples'].get('embedded_synonym', [])[:3]}")
    json.dump(out, open(path, "w"), indent=1, ensure_ascii=False)
