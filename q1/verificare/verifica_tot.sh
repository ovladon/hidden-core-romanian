#!/usr/bin/env bash
# Verificarea tuturor dictionarelor din pachet. Se ruleaza din dosarul pachetului dezarhivat:
#   bash verifica_tot.sh            # pasul 1 (limitele superioare si ciclurile certificatului), cateva minute
#   bash verifica_tot.sh 900        # si pasul 2: rezolva fiecare .lp cu HiGHS, cel mult 900 s pe dictionar
cd "$(dirname "$0")"
sec="$1"
for g in graphs/*.tsv.gz; do
  c=$(basename "$g" .tsv.gz)
  gunzip -kf "$g"
  python3 verify.py "graphs/$c.tsv" "exact/$c" || echo "   !! $c: verificarea a esuat"
  if [ -n "$sec" ]; then
    gunzip -kf "exact/$c.lp.gz"
    python3 solve_lp.py "exact/$c" "$sec"
  fi
done
