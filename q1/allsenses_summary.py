#!/usr/bin/env python3
"""Q1: first sense only versus all senses, for the 15 dictionaries processed with the same procedure.

For each dictionary and each of the two regimes (most frequent candidate, all candidates): Kernel share, MinSet/Kernel
(middle of the greedy and cycle-packing bounds) and reciprocal pairs per 1,000 headwords; then the distance of the
DEX from the other dictionaries and the rank correlation between the two settings.

  python3 q1/allsenses_summary.py        # writes q1/allsenses_summary.json and prints a table
"""
import json, os, statistics
from scipy import stats

CODES = [("dex", "Romanian DEX"), ("ro_wikt", "Romanian Wiktionary*"), ("it", "Italian"), ("es", "Spanish"),
         ("pt", "Portuguese"), ("fr", "French"), ("en", "English Wiktionary"), ("simple", "Simple English"),
         ("wordnet", "English WordNet"), ("de", "German"), ("nl", "Dutch"), ("pl", "Polish"), ("cs", "Czech"),
         ("ru", "Russian"), ("el", "Greek")]


def measure(prefix):
    out = {}
    for g in ("freq", "all"):
        p = f"{prefix}_{g}.json"
        if not os.path.exists(p): return None
        d = json.load(open(p)); N = d["headwords"]; k = len(d["kernel"])
        out[g] = {"headwords": N, "kernel": k / N, "minset_over_kernel": (d["minset_lower_bound"] + d["minset_upper_bound"]) / 2 / k,
                  "pairs_per_1000": 1000 * len(d["reciprocal_pairs"]) / N}
    out["minset_over_kernel"] = (out["freq"]["minset_over_kernel"] + out["all"]["minset_over_kernel"]) / 2
    out["kernel"] = (out["freq"]["kernel"] + out["all"]["kernel"]) / 2
    out["pairs_per_1000"] = out["freq"]["pairs_per_1000"]
    return out


rows = {}
for c, name in CODES:
    first = measure("crossling/wordnet" if c == "wordnet" else f"crossling/graphs/{c}")
    alls = measure(f"q1/allsenses/{c}")
    if first and alls: rows[c] = {"dictionary": name, "first_sense": first, "all_senses": alls}

res = {"dictionaries": rows}
for key in ("first_sense", "all_senses"):
    oth = [r[key]["minset_over_kernel"] for c, r in rows.items() if c not in ("dex", "ro_wikt")]
    if "dex" in rows and len(oth) > 2:
        res[key] = {"others_min": min(oth), "others_max": max(oth), "others_mean": statistics.mean(oth),
                    "dex": rows["dex"][key]["minset_over_kernel"],
                    "dex_z": (rows["dex"][key]["minset_over_kernel"] - statistics.mean(oth)) / statistics.stdev(oth), "n": len(oth)}
if len(rows) > 3:
    a = [r["first_sense"]["minset_over_kernel"] for r in rows.values()]; b = [r["all_senses"]["minset_over_kernel"] for r in rows.values()]
    rho, p = stats.spearmanr(a, b); res["spearman_first_vs_all"] = {"rho": rho, "p": p, "n": len(a)}
json.dump(res, open("q1/allsenses_summary.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)

pc = lambda x: f"{100 * x:5.1f}%"
print(f"{'dictionary':22s} | {'Kernel first → all':>18s} | {'MinSet/Kernel first → all':>26s} | {'pairs/1000 first → all':>23s} | headwords first → all")
for c, r in rows.items():
    f, a = r["first_sense"], r["all_senses"]
    print(f"{r['dictionary']:22s} | {pc(f['kernel'])} → {pc(a['kernel'])} | {pc(f['minset_over_kernel'])} → {pc(a['minset_over_kernel'])}       "
          f"| {f['pairs_per_1000']:6.1f} → {a['pairs_per_1000']:6.1f}  | {f['freq']['headwords']:,} → {a['freq']['headwords']:,}")
for key in ("first_sense", "all_senses"):
    if key in res:
        x = res[key]
        print(f"{key}: others {pc(x['others_min'])}–{pc(x['others_max'])} (n = {x['n']}), DEX {pc(x['dex'])}, z = {x['dex_z']:.1f}")
if "spearman_first_vs_all" in res:
    print(f"Spearman first vs all: rho = {res['spearman_first_vs_all']['rho']:.2f} (p = {res['spearman_first_vs_all']['p']:.2g})")
