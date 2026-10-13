#!/usr/bin/env python3
"""Acordul dintre doua seturi de alegeri (ex. Haiku vs Opus) pe aceleasi definitii."""
import json, sys, collections
FUN = {"a", "o", "al", "ale", "ai", "lui", "cel", "cea", "cei", "ce", "de", "la", "pe", "în", "cu",
       "care", "se", "și", "sau", "un", "una", "unei", "unui", "fi", "este", "e", "nu", "mai", "să",
       "ca", "ei", "ea", "le", "li", "îi", "își", "lor"}
a, b = (json.load(open(p, encoding="utf8")) for p in sys.argv[1:3])
tot, ok = collections.Counter(), collections.Counter()
for k in a.keys() & b.keys():
    g = "cuvinte funcționale" if k.split("\t")[1] in FUN else "cuvinte de conținut"
    tot[g] += 1; ok[g] += a[k] == b[k]
for g in sorted(tot):
    print(f"{g:<22} acord: {ok[g]}/{tot[g]} = {ok[g]/tot[g]:.1%}")
print(f"{'total':<22} acord: {sum(ok.values())}/{sum(tot.values())} = {sum(ok.values())/sum(tot.values()):.1%}")
