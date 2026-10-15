#!/usr/bin/env bash
# MinSet exact (limite ILP + certificat) pentru toate dictionarele, cate 6 in paralel.
cd "$(dirname "$0")/.."
{
  echo "dex_llm out/graph_src12_freq_noexpr_first_ai.tsv out/kernel_src12_freq_noexpr_first_ai.json"
  echo "wordnet crossling/wordnet_freq.tsv crossling/wordnet_freq.json"
  for c in dex ro_wikt it es pt fr en simple de nl pl cs ru el; do
    echo "$c crossling/graphs/${c}_freq.tsv crossling/graphs/${c}_freq.json"
  done
} | xargs -P 6 -L 1 bash -c 'python3 -u exact_minset.py "$1" "$2" --time 300 --iters 80 --budget 3600 --gap 0.002 \
      --out q1/exact/$0 --certificate > q1/exact/$0.log 2>&1; echo "$0 gata"'
echo EXACT_GATA
