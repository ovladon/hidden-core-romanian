#!/usr/bin/env bash
cd "$(dirname "$0")/.."
python3 -I q1/lemma_forms.py crossling/graphs/dex.jsonl.gz ro q1/forms/dex.json.gz
python3 -I q1/lemma_forms.py crossling/graphs/ro_wiktionary.jsonl.gz ro q1/forms/ro_wikt.json.gz
for l in it es pt cs el nl pl de ru fr; do python3 -I q1/lemma_forms.py crossling/raw/$l/$l-extract.jsonl.gz $l q1/forms/$l.json.gz; done
python3 -I q1/lemma_forms.py crossling/raw/simple/simple-extract.jsonl.gz en q1/forms/simple.json.gz
python3 -I q1/lemma_forms.py crossling/raw/en/raw-wiktextract-data.jsonl.gz en q1/forms/en.json.gz
echo FORME_GATA
