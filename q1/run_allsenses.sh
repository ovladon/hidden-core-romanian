#!/usr/bin/env bash
# Toate sensurile, nu doar primul: aceeasi procedura pe cele 15 dictionare (q1/allsenses/<cod>_{freq,all}.json).
cd "$(dirname "$0")/.."
mkdir -p q1/allsenses
python3 crossling/dex_to_jsonl.py q1/allsenses/dex.jsonl.gz --all-senses
python3 -I crossling/rowiktionary_to_jsonl.py crossling/raw/ro/rowiktionary-latest-pages-articles.xml.bz2 \
    q1/allsenses/ro_wiktionary.jsonl.gz --all-senses
python3 crossling/wordnet_graph.py --all-senses       # nltk: nu in modul izolat
graph() {  # graph <cod> <sursa> <lang>
  python3 -I crossling/wiktionary_graph.py "$2" "$3" "q1/allsenses/$1" --all-senses > "q1/allsenses/$1_build.log" 2>&1
  for r in freq all; do
    python3 latent_structure.py "q1/allsenses/$1_$r.tsv" --headwords "q1/allsenses/$1_headwords.txt" \
        --json "q1/allsenses/$1_$r.json" > "q1/allsenses/$1_$r.log" 2>&1
  done
  echo "$1 gata"
}
export -f graph
{
  echo "dex q1/allsenses/dex.jsonl.gz ro"
  echo "ro_wikt q1/allsenses/ro_wiktionary.jsonl.gz ro"
  for l in it es pt cs el nl pl de ru fr; do echo "$l crossling/raw/$l/$l-extract.jsonl.gz $l"; done
  echo "simple crossling/raw/simple/simple-extract.jsonl.gz en"
  echo "en crossling/raw/en/raw-wiktextract-data.jsonl.gz en"
} | xargs -P 5 -L 1 bash -c 'graph "$@"' _
for r in freq all; do
  python3 latent_structure.py crossling/wordnet_allsenses_$r.tsv --headwords crossling/wordnet_allsenses_headwords.txt \
      --json q1/allsenses/wordnet_$r.json > q1/allsenses/wordnet_$r.log 2>&1
done
echo "wordnet gata"
echo TOATE_SENSURILE_GATA
