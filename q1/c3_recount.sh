#!/usr/bin/env bash
# Reface doar constructorul C3 (graful iese identic; se corecteaza embedded_stripped_share din _stats.json).
cd "$(dirname "$0")/.."
one() { h=$(md5sum < "q1/cf/${1}_C3_freq.tsv")
  python3 -I crossling/wiktionary_graph.py "$2" "$3" "q1/cf/${1}_C3" --strip-tails --drop-synonym-only --strip-segments > /dev/null
  [ "$h" = "$(md5sum < "q1/cf/${1}_C3_freq.tsv")" ] && echo "$1 identic" || echo "$1 DIFERIT"; }
one dex crossling/graphs/dex.jsonl.gz ro
one ro_wikt crossling/graphs/ro_wiktionary.jsonl.gz ro
for l in it es pt cs el nl pl de ru fr; do one $l crossling/raw/$l/$l-extract.jsonl.gz $l; done
one simple crossling/raw/simple/simple-extract.jsonl.gz en
one en crossling/raw/en/raw-wiktextract-data.jsonl.gz en
echo RECOUNT_GATA
