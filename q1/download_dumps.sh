#!/usr/bin/env bash
# Dump-urile wikitext ale Wiktionary-urilor (Wikimedia, CC BY-SA), pentru legaturile manuale din definitii.
cd "$(dirname "$0")/../crossling/raw"
for l in cs it pt es el nl pl de ru fr; do
  mkdir -p "dump_$l"; f="dump_$l/${l}wiktionary-latest-pages-articles.xml.bz2"
  [ -s "$f" ] && { echo "exista: $f"; continue; }
  for i in $(seq 1 20); do
    curl -sS -L -C - --connect-timeout 30 --speed-limit 1000 --speed-time 120 -o "$f.part" \
      "https://dumps.wikimedia.org/${l}wiktionary/latest/${l}wiktionary-latest-pages-articles.xml.bz2" && { mv "$f.part" "$f"; echo "ok: $f"; break; }
    echo "reincercare $i: $f"; sleep 20
  done
done
echo DUMPURI_GATA
