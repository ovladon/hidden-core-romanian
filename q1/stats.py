#!/usr/bin/env python3
"""Q1, task 6: statistics for the claims of the paper.

  1. Reference inventories: Wilson 95% intervals for the shares in the Kernel and in the MinSet; Fisher exact tests
     between Graur's certainty groups.
  2. Cross-linguistic comparison (crossling/summary.json): position of the DEX in the distribution of MinSet/Kernel,
     rank correlations with the density of reciprocal pairs, dictionary size and definition length, and a least-squares
     fit of MinSet/Kernel on these predictors.

  python3 q1/stats.py        # writes q1/stats.json
"""
import json, math
import numpy as np
from scipy.stats import fisher_exact, spearmanr


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


R = json.load(open("results/results.json", encoding="utf8"))
out = {"inventories": {}, "graur_group_tests": {}, "crossling": {}}
groups = {"Swadesh": R["swadesh"]["layers"], "Graur all": R["graur"]["all"], "Graur most certain": R["graur"]["core"],
          "Graur middle": R["graur"]["middle"], "Graur maximal": R["graur"]["maximal"]}
for name, g in groups.items():
    out["inventories"][name] = {lay: {"hits": g[lay]["hits"], "n": g[lay]["n"], "share": round(g[lay]["rate"], 4),
                                      "ci95": wilson(g[lay]["hits"], g[lay]["n"]), "expected": round(g[lay]["expected"], 4),
                                      "p_hypergeom": g[lay]["p"]}
                                for lay in ("Kernel", "MinSet")}
for a, b in (("Graur most certain", "Graur middle"), ("Graur most certain", "Graur maximal"), ("Graur middle", "Graur maximal")):
    for lay in ("Kernel", "MinSet"):
        ga, gb = groups[a][lay], groups[b][lay]
        table = [[ga["hits"], ga["n"] - ga["hits"]], [gb["hits"], gb["n"] - gb["hits"]]]
        odds, p = fisher_exact(table)
        out["graur_group_tests"][f"{a} vs {b} ({lay})"] = {"shares": [round(ga["rate"], 3), round(gb["rate"], 3)],
                                                          "odds_ratio": round(odds, 2), "p_fisher": p}

S = json.load(open("crossling/summary.json", encoding="utf8"))
def ratio(r):
    vals = []
    for g in ("freq", "all"):
        d = r.get(g)
        if d: vals.append((d["minset_lb_n"] + d["minset_ub_n"]) / 2 / d["kernel_n"])
    return sum(vals) / len(vals)
rows = [{"code": r["code"], "language": r["language"], "ratio": ratio(r), "pairs": r["reciprocal_pairs_per_1000"],
         "logsize": math.log10(r["headwords"]), "tokens": r.get("tokens_per_definition")} for r in S]
other = [r for r in rows if r["language"] != "Romanian"]
dex = next(r for r in rows if r["code"] == "dex")
m, sd = np.mean([r["ratio"] for r in other]), np.std([r["ratio"] for r in other], ddof=1)
out["crossling"]["minset_over_kernel"] = {"dex": round(dex["ratio"], 4), "others_mean": round(m, 4), "others_sd": round(sd, 4),
                                          "others_range": [round(min(r["ratio"] for r in other), 4), round(max(r["ratio"] for r in other), 4)],
                                          "dex_z": round((dex["ratio"] - m) / sd, 1)}
def corr(sub, x, y="ratio"):
    sub = [r for r in sub if r[x] is not None]
    rho, p = spearmanr([r[x] for r in sub], [r[y] for r in sub])
    return {"rho": round(rho, 3), "p": round(p, 4), "n": len(sub)}
for x in ("pairs", "logsize", "tokens"):
    out["crossling"][f"spearman_ratio_vs_{x}_all"] = corr(rows, x)
    out["crossling"][f"spearman_ratio_vs_{x}_without_romanian"] = corr(other, x)
X = np.array([[1, r["pairs"], r["logsize"]] for r in rows]); y = np.array([r["ratio"] for r in rows])
beta, *_ = np.linalg.lstsq(X, y, rcond=None); pred = X @ beta
out["crossling"]["ols_ratio_on_pairs_and_logsize"] = {"intercept": round(beta[0], 4), "per_pair_per_1000": round(beta[1], 5),
                                                     "per_log10_size": round(beta[2], 4),
                                                     "r2": round(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum(), 3),
                                                     "n": len(rows)}
json.dump(out, open("q1/stats.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
