#!/usr/bin/env bash
# Descarca dictionarele Wiktionary (CC BY-SA): extrasele kaikki.org (wiktextract) si dump-ul ro.wiktionary.
# Fiecare fisier in propriul dosar (date nesigure; scripturile de analiza stau in crossling/, nu aici).
set -u
cd "$(dirname "$0")/raw"
get() {  # get <dosar> <url>
  mkdir -p "$1"
  f="$1/$(basename "$2")"
  if [ -s "$f" ]; then echo "exista: $f"; return; fi
  curl -sSL --fail --retry 3 -o "$f.part" "$2" && mv "$f.part" "$f" && echo "ok: $f $(du -h "$f" | cut -f1)" || echo "EROARE: $2"
}
get ro https://dumps.wikimedia.org/rowiktionary/latest/rowiktionary-latest-pages-articles.xml.bz2
for l in simple it pt es cs el nl pl de ru fr; do
  get "$l" "https://kaikki.org/dictionary/downloads/$l/$l-extract.jsonl.gz"
done
get en https://kaikki.org/dictionary/raw-wiktextract-data.jsonl.gz
echo GATA
