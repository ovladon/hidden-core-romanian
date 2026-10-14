#!/usr/bin/env bash
# Graful si structura latenta pentru o limba: crossling/run_lang.sh <cod> <fisier kaikki> [cod_limba_in_fisier]
set -e
cd "$(dirname "$0")/.."
code=$1; file=$2; lc=${3:-$1}
python3 -I crossling/wiktionary_graph.py "$file" "$lc" "crossling/graphs/$code" > "crossling/graphs/${code}_build.log"
for r in freq all; do
  python3 latent_structure.py "crossling/graphs/${code}_${r}.tsv" --headwords "crossling/graphs/${code}_headwords.txt" \
      --json "crossling/graphs/${code}_${r}.json" > "crossling/graphs/${code}_${r}.log" 2>&1
done
echo "$code: $(grep -h -E '^(Kernel|MinSet)' crossling/graphs/${code}_freq.log | tr -s ' ' | tr '\n' ' ') || all: $(grep -h -E '^(Kernel|MinSet)' crossling/graphs/${code}_all.log | tr -s ' ' | tr '\n' ' ')"
