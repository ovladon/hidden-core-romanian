#!/usr/bin/env bash
# Regenereaza graful principal (regula de departajare determinista) si recalculeaza limitele MinSet prin ILP.
set -e
cd "$(dirname "$0")/.."
python3 kernel.py --sources 1,2 --no-expr --first-sense --choices ai/choices_haiku12.json --out out > q1/rebuild_ai_kernel.log 2>&1
python3 -u exact_minset.py out/graph_src12_freq_noexpr_first_ai.tsv out/kernel_src12_freq_noexpr_first_ai.json \
    --time 300 --iters 60 --budget 3600 --gap 0.002 > out/exact_ai.log 2>&1
python3 pairs.py out/graph_src12_freq_noexpr_first_ai.tsv out/kernel_src12_freq_noexpr_first_ai.json > q1/rebuild_pairs.log 2>&1
python3 pairs.py out/graph_src12_freq_noexpr_first.tsv out/kernel_src12_freq_noexpr_first.json > /dev/null 2>&1 || true
echo GATA
