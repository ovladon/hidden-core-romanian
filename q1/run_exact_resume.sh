#!/usr/bin/env bash
# A doua runda ILP: reia fiecare graf de la ciclurile si solutia din q1/exact/<cod> (prima runda) si continua cu
# rezolvari mai lungi; rezultatele inlocuiesc q1/exact/<cod>.* doar daca intervalul s-a strans.
# Pentru graful DEX din lucrarea ConsILR porneste si de la multimea de 6.325 de cuvinte gasita atunci.
# Fiecare graf porneste imediat ce prima runda l-a terminat (asteapta fisierul _names.txt, scris ultimul).
cd "$(dirname "$0")/.."
mkdir -p q1/exact2
{
  echo "dex_llm out/graph_src12_freq_noexpr_first_ai.tsv out/kernel_src12_freq_noexpr_first_ai.json"
  echo "wordnet crossling/wordnet_freq.tsv crossling/wordnet_freq.json"
  for c in dex ro_wikt it es pt fr en simple de nl pl cs ru el; do
    echo "$c crossling/graphs/${c}_freq.tsv crossling/graphs/${c}_freq.json"
  done
} | xargs -P 6 -L 1 bash -c '
  until [ -s q1/exact/$0_names.txt ]; do sleep 30; done
  extra=""; [ "$0" = dex_llm ] && extra="--start-set out/minset_exact_src12_freq_noexpr_first_ai.json"
  python3 -u exact_minset.py "$1" "$2" --time 900 --iters 80 --budget ${BUDGET:-7200} --gap 0.002 \
      --resume q1/exact/$0 $extra --out q1/exact2/$0 --certificate > q1/exact2/$0.log 2>&1
  python3 - "$0" <<EOF
import json, shutil, sys
c = sys.argv[1]; a = json.load(open(f"q1/exact/{c}.json")); b = json.load(open(f"q1/exact2/{c}.json"))
better = (b["upper_bound"] - b["lower_bound"]) < (a["upper_bound"] - a["lower_bound"])
print(c, "runda 1:", a["lower_bound"], a["upper_bound"], "| runda 2:", b["lower_bound"], b["upper_bound"],
      "-> inlocuit" if better else "-> pastrat")
if better:
    for ext in (".json", ".lp", "_cycles.json.gz", "_names.txt", ".log"):
        shutil.copy(f"q1/exact2/{c}{ext}", f"q1/exact/{c}{ext}" if ext != ".log" else f"q1/exact/{c}_round2.log")
EOF'
echo EXACT2_GATA
