#!/usr/bin/env bash
# Contrafactualele gradate pe toate dictionarele, cu aceeasi procedura: C1 = fara cozi de sinonime; C2 = C1 + fara
# definitiile formate numai din sinonime; C3 = C2 + fara segmentele de cel mult doua cuvinte (sinonime in corpul definitiei). Rezultate in q1/cf/<cod>_<C>_{freq,all}.json si _stats.json.
cd "$(dirname "$0")/.."
mkdir -p q1/cf
run() {  # run <cod> <fisier> <lang>
  for c in ${LEVELS:-C0 C1 C2 C3}; do
    flags=""; [ $c = C1 ] && flags="--strip-tails"; [ $c = C2 ] && flags="--strip-tails --drop-synonym-only"
    [ $c = C3 ] && flags="--strip-tails --drop-synonym-only --strip-segments"
    python3 -I crossling/wiktionary_graph.py "$2" "$3" "q1/cf/${1}_${c}" $flags > /dev/null
    for r in freq all; do
      python3 latent_structure.py "q1/cf/${1}_${c}_${r}.tsv" --headwords "q1/cf/${1}_${c}_headwords.txt" \
          --json "q1/cf/${1}_${c}_${r}.json" > "q1/cf/${1}_${c}_${r}.log" 2>&1
    done
    echo "$1 $c gata"
  done
}
run dex crossling/graphs/dex.jsonl.gz ro
run ro_wikt crossling/graphs/ro_wiktionary.jsonl.gz ro
for l in it es pt cs el nl pl de ru fr; do run $l crossling/raw/$l/$l-extract.jsonl.gz $l; done
run simple crossling/raw/simple/simple-extract.jsonl.gz en
run en crossling/raw/en/raw-wiktextract-data.jsonl.gz en
echo TOATE_GATA
