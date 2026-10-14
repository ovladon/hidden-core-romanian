#!/usr/bin/env python3
"""Cross-linguistic human gold standard for lemma assignment: the links that Wiktionary editors put in definitions.

Input: records (jsonl.gz), one per content entry: {"word", "gloss", "links": [[surface, target], ...]}, the gloss being
the first sense used by crossling/wiktionary_graph.py. The headwords and the form -> lemma map are those of the graph
(crossling/graphs/<code>_headwords.txt, q1/forms/<code>.json.gz), so candidates are exactly the ones of our procedure.

  1. Accuracy of the most-frequent-candidate rule on every ambiguous linked form (deliberate links: surface != target).
  2. A "human" regime: the graph rebuilt with every ambiguous form that the editors linked assigned to their target
     (the other forms as in the most-frequent regime); its latent structure is compared with the two automatic regimes.

  python3 -I q1/links_gold.py <records.jsonl.gz> <code>
"""
import collections, gzip, json, math, re, subprocess, sys, unicodedata

STRESS = re.compile("[̀́]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower().strip()
TOKEN = re.compile(r"[^\W\d_]+")


def wilson(k, n, z=1.96):
    if not n: return [0, 0]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def main(records, code):
    H = {l.strip() for l in open(f"crossling/graphs/{code}_headwords.txt", encoding="utf8") if l.strip()}
    fmap = json.load(gzip.open(f"q1/forms/{code}.json.gz", "rt", encoding="utf8"))
    # cuvintele functionale, ca in constructorul grafului: clasa inchisa si nu cuvant-titlu, plus cuvintele de o litera
    closed = {l.strip() for l in open(records.replace(".jsonl.gz", "_closed.txt"), encoding="utf8") if l.strip()}
    func = closed - H
    cands = lambda t: set() if (t in func or len(t) == 1) else ({t} | set(fmap.get(t, ()))) & H
    recs = [json.loads(l) for l in gzip.open(records, "rt", encoding="utf8")]
    recs = [r for r in recs if nf(r["word"]) in H]
    tokfreq = collections.Counter(t for r in recs for t in TOKEN.findall(nf(r["gloss"])))
    score = collections.Counter({w: tokfreq.get(w, 0) for w in H})
    for t, k in tokfreq.items():
        c = cands(t)
        if len(c) == 1: score[next(iter(c))] += k
    rule = lambda t, c: max(c, key=lambda x: (score[x], x == t, x))
    stats = collections.Counter(); human = {}
    for r in recs:
        v = nf(r["word"])
        for surface, target in r.get("links") or []:
            s, tg = nf(surface), nf(target)
            if not TOKEN.fullmatch(s or "-"): continue
            c = cands(s)
            if len(c) < 2 or tg not in c: continue
            grp = "deliberate" if s != tg else "plain"
            for g in (grp, "all"):
                stats[g] += 1; stats[g + "_ok"] += rule(s, c) == tg
            human[(v, s)] = tg
    res = {"code": code, "entries": len(recs), "entries_with_links": sum(1 for r in recs if r.get("links"))}
    for g in ("deliberate", "plain", "all"):
        n, k = stats[g], stats[g + "_ok"]
        res[g] = {"links": n, "rule_accuracy": k / n if n else None, "ci95": wilson(k, n)}
    # regimul "uman": formele legate de editori -> tinta lor; restul ca in regimul "cel mai frecvent"
    arcs = set()
    for r in recs:
        v = nf(r["word"])
        for t in TOKEN.findall(nf(r["gloss"])):
            c = cands(t)
            if not c: continue
            pick = human.get((v, t)) or (next(iter(c)) if len(c) == 1 else rule(t, c))
            if pick != v: arcs.add((pick, v))
    path = f"q1/human/{code}_human.tsv"
    with open(path, "w", encoding="utf8") as f:
        for u, w in sorted(arcs): f.write(f"{u}\t{w}\n")
    subprocess.run([sys.executable, "latent_structure.py", path, "--headwords", f"crossling/graphs/{code}_headwords.txt",
                    "--json", f"q1/human/{code}_human.json"], capture_output=True)
    d = json.load(open(f"q1/human/{code}_human.json")); N = d["headwords"]; k = len(d["kernel"])
    res["human_regime"] = {"arcs": len(arcs), "human_assignments": len(human), "kernel": k / N,
                           "minset": [d["minset_lower_bound"] / N, d["minset_upper_bound"] / N],
                           "minset_over_kernel": (d["minset_lower_bound"] + d["minset_upper_bound"]) / 2 / k,
                           "pairs_per_1000": 1000 * len(d["reciprocal_pairs"]) / N}
    json.dump(res, open(f"q1/human/{code}_gold.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
