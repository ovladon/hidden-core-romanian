#!/usr/bin/env bash
# Etalonul uman (legaturile editorilor) pentru toate Wiktionary-urile; asteapta dump-urile care inca se descarca.
cd "$(dirname "$0")/.."
for l in cs pt es el nl pl de ru fr; do
  dump="crossling/raw/dump_$l/${l}wiktionary-latest-pages-articles.xml.bz2"
  until [ -s "$dump" ]; do sleep 30; done
  python3 -I q1/link_records_dump.py crossling/raw/$l/$l-extract.jsonl.gz $l "$dump" q1/human/${l}_records.jsonl.gz
  python3 -I q1/links_gold.py q1/human/${l}_records.jsonl.gz $l > /dev/null && echo "$l gata"
done
python3 -I q1/link_records_kaikki.py crossling/raw/simple/simple-extract.jsonl.gz en q1/human/simple_records.jsonl.gz
python3 -I q1/links_gold.py q1/human/simple_records.jsonl.gz simple > /dev/null && echo "simple gata"
echo LEGATURI_GATA
