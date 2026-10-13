#!/usr/bin/env python3
"""Tabelul de robustete: aceleasi masuri sub trei moduri de a rezolva formele ambigue
(regula frecventei / modelul / toate variantele). Daca concluziile nu se schimba, nu depind de lematizare."""
import json, sys, collections, subprocess

RUNS = [("regula frecvenței", "out/kernel_src12_freq_noexpr_first.json", "out/graph_src12_freq_noexpr_first.tsv"),
        ("model (Haiku)*", "out/kernel_src12_freq_noexpr_first_ai.json", "out/graph_src12_freq_noexpr_first_ai.tsv"),
        ("toate variantele", "out/kernel_src12_all_noexpr_first.json", "out/graph_src12_all_noexpr_first.tsv")]


def mutual(graph):
    out = collections.defaultdict(set)
    for line in open(graph, encoding="utf8"):
        u, v = line.rstrip("\n").split("\t"); out[u].add(v)
    return sum(1 for u in out for v in out[u] if u < v and u in out.get(v, ()))


def lower_bound(graph, kern):
    r = subprocess.run([sys.executable, "bounds.py", graph, kern], capture_output=True, text=True).stdout
    return int(r.split("limita inferioara MinSet): ")[1].split()[0])


print(f"{'regim':<20}{'muchii':>9}{'Kernel':>14}{'Core':>14}{'MinSet (interval)':>24}{'perechi reciproce':>19}")
for name, kp, gp in RUNS:
    try:
        k = json.load(open(kp, encoding="utf8"))
    except FileNotFoundError:
        print(f"{name:<20}  (lipsește {kp})"); continue
    H = k["heads"]; lb = lower_bound(gp, kp)
    print(f"{name:<20}{k['edges']:>9}{len(k['kernel']):>8} ({len(k['kernel'])/H:.0%})"
          f"{len(k['core']):>8} ({len(k['core'])/H:.0%})"
          f"{lb:>10}–{len(k['minset'])} ({lb/H:.1%}–{len(k['minset'])/H:.1%})"
          f"{mutual(gp):>14}")
