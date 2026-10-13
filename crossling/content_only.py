#!/usr/bin/env python3
"""Structura latenta a DEX doar pe cuvinte de continut (ca Vincent-Lamarre et al. 2016, care ignora cuvintele functionale).

Cuvintele functionale = cuvinte-titlu ale caror intrari DEX au toate, ca prima eticheta gramaticala, o clasa inchisa
(conj., prep., pron., art., interj., adjective pronominale); lista: out/function_words_dex.txt.

  python3 crossling/content_only.py [--ilp SECUNDE]
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import latent_structure as L

ap = argparse.ArgumentParser(); ap.add_argument("--ilp", type=float, default=0); a = ap.parse_args()
F = {w for w in open("out/function_words_dex.txt", encoding="utf8").read().split("\n") if w}
H = {w for w in open("out/headwords_src12.txt", encoding="utf8").read().split("\n") if w} - F
res = {}
for name, tag in (("most_frequent", "src12_freq_noexpr_first"), ("llm", "src12_freq_noexpr_first_ai"),
                  ("all_candidates", "src12_all_noexpr_first")):
    out, inn = L.load(f"out/graph_{tag}.tsv")
    for f in F & set(out):
        for v in out.pop(f): inn[v].discard(f)
        for u in inn.pop(f): out[u].discard(f)
    K = L.kernel(out, inn); comps = L.sccs(K, out); core = comps[0]
    M = L.greedy_fvs(K, out, inn); lb, lens = L.cycle_packing(K, out)
    if a.ilp and name == "llm":
        lb2, M2 = L.ilp_bounds(K, out, inn, a.ilp)
        lb = max(lb, lb2)
        if M2 is not None and len(M2) < len(M) and L.is_feedback(M2, K, out): M = M2
    N = len(H); pairs = sum(1 for u in out for v in out[u] if u < v and u in out[v])
    res[name] = {"content_headwords": N, "kernel": len(K), "core": len(core), "minset_lb": lb, "minset_ub": len(M),
                 "pairs": pairs}
    print(f"{name:15s} N={N} | Kernel {len(K)} ({100*len(K)/N:.1f}%) | Core {len(core)} ({100*len(core)/N:.1f}%) | "
          f"MinSet {lb}–{len(M)} ({100*lb/N:.1f}–{100*len(M)/N:.1f}%) | perechi {pairs}", flush=True)
json.dump(res, open("crossling/content_only.json", "w"), indent=1)
