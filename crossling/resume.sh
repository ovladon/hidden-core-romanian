#!/usr/bin/env bash
# Reia descarcarile mari intrerupte (continua de unde au ramas), cu pana la 30 de incercari fiecare.
cd "$(dirname "$0")/raw"
res() {  # res <dosar> <url>
  f="$1/$(basename "$2")"
  [ -s "$f" ] && { echo "exista: $f"; return; }
  for i in $(seq 1 30); do
    curl -sS -L -C - --connect-timeout 30 --speed-limit 1000 --speed-time 120 -o "$f.part" "$2" && { mv "$f.part" "$f"; echo "ok: $f $(du -h "$f" | cut -f1)"; return; }
    echo "incercarea $i esuata pentru $f ($(du -h "$f.part" | cut -f1) pana acum)"; sleep 20
  done
  echo "EROARE definitiva: $2"
}
res fr https://kaikki.org/dictionary/downloads/fr/fr-extract.jsonl.gz
res en https://kaikki.org/dictionary/raw-wiktextract-data.jsonl.gz
echo GATA
