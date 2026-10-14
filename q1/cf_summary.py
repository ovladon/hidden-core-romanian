#!/usr/bin/env python3
"""Q1, task 2: graded counterfactuals, identical for every dictionary.

  C0  the dictionary as it is
  C1  synonym tails removed ("...; arbore, pom")
  C2  C1 and definitions made only of synonyms ("Arbore, pom.") treated as absent

For each dictionary and level: share of definitions with a synonym tail / made only of synonyms, Kernel and MinSet
(range over the two regimes), MinSet/Kernel and reciprocal pairs per 1,000 headwords.

  python3 q1/cf_summary.py      # writes q1/cf_summary.json and prints a table
"""
import json, os

CODES = [("dex", "Romanian DEX"), ("ro_wikt", "Romanian Wiktionary*"), ("it", "Italian"), ("es", "Spanish"),
         ("pt", "Portuguese"), ("fr", "French"), ("en", "English Wiktionary"), ("simple", "Simple English"),
         ("de", "German"), ("nl", "Dutch"), ("pl", "Polish"), ("cs", "Czech"), ("ru", "Russian"), ("el", "Greek")]
rows = []
for code, name in CODES:
    r = {"code": code, "dictionary": name}
    for c in ("C0", "C1", "C2"):
        p = f"q1/cf/{code}_{c}"
        if not (os.path.exists(p + "_freq.json") and os.path.exists(p + "_all.json")): continue
        st = json.load(open(p + "_stats.json"))
        lv = {"synonym_tail_share": st["synonym_tail_share"], "synonym_only_share": st["synonym_only_share"]}
        ratios, pairs = [], []
        for g in ("freq", "all"):
            d = json.load(open(f"{p}_{g}.json")); N = d["headwords"]; k = len(d["kernel"])
            lo, hi = d["minset_lower_bound"], d["minset_upper_bound"]
            lv[g] = {"headwords": N, "kernel": k / N, "minset": [lo / N, hi / N]}
            ratios.append((lo + hi) / 2 / k); pairs.append(1000 * len(d["reciprocal_pairs"]) / N)
        lv["minset_over_kernel"] = sum(ratios) / 2; lv["pairs_per_1000"] = pairs[0]
        r[c] = lv
    if "C0" in r: rows.append(r)
json.dump(rows, open("q1/cf_summary.json", "w"), indent=1, ensure_ascii=False)
pc = lambda x: f"{100 * x:5.1f}%"
print(f"{'dictionary':22s} {'tails':>6s} {'syn-only':>8s} | {'MinSet/Kernel C0 → C1 → C2':>28s} | {'pairs/1000 C0 → C1 → C2':>24s}")
for r in rows:
    lv = [r.get(c) for c in ("C0", "C1", "C2")]
    mk = " → ".join(pc(x["minset_over_kernel"]) if x else "  –  " for x in lv)
    pp = " → ".join(f"{x['pairs_per_1000']:5.1f}" if x else "  –  " for x in lv)
    print(f"{r['dictionary']:22s} {pc(r['C0']['synonym_tail_share'])} {pc(r['C0']['synonym_only_share']):>8s} | {mk:>28s} | {pp:>24s}")
