#!/usr/bin/env python3
"""Check of the data source: the main graph uses DEX '98 completed with DEX '96 for the headwords missing from
DEX '98 in the dexonline dump (letters G, H and part of I). This script rebuilds the graph from DEX '98 alone, in
the language-model regime, and compares its layers with those of the main graph (greedy and cycle-packing bounds
for the MinSet in both cases, so that the two are computed in the same way).

  python3 dex98_only.py        # writes results/dex98_only.json (needs data/*.pkl, see extract.py)
"""
import json, os, re, subprocess, sys

OUT = "out/dex98"
os.makedirs(OUT, exist_ok=True)
run = lambda *a: subprocess.run([sys.executable, *a], check=True, capture_output=True, text=True).stdout
log = run("kernel.py", "--sources", "1", "--ambig", "freq", "--no-expr", "--first-sense",
          "--choices", "ai/choices_haiku12.json", "--out", OUT)
H1 = int(re.search(r"cuvinte-titlu \(leme distincte\): (\d+)", log).group(1))
D1 = int(re.search(r"definitii \(surse \(1,\)\): (\d+)", log).group(1))
R = json.load(open("results/results.json", encoding="utf8"))
res = {}
for name, graph, H in (("dex98_dex96", "out/graph_src12_freq_noexpr_first_ai.tsv", R["data"]["headwords"]),
                       ("dex98_only", f"{OUT}/graph_src1_freq_noexpr_first_ai.tsv", H1)):
    js = f"{OUT}/{name}.json"
    run("latent_structure.py", graph, "--json", js)
    d = json.load(open(js)); k = len(d["kernel"])
    res[name] = {"headwords": H, "kernel": k / H, "minset_lb": d["minset_lower_bound"] / H,
                 "minset_ub": d["minset_upper_bound"] / H, "pairs_per_1000": 1000 * len(d["reciprocal_pairs"]) / H}
res["dex98_only"]["definitions"] = D1
json.dump(res, open("results/dex98_only.json", "w"), indent=1)
print(json.dumps(res, indent=1))
