#!/usr/bin/env python3
"""Compozitia etimologica a straturilor (Rest/Satelit/Core/MinSet), din etimologiile DEX '98.
Conventie DEX: "Lat. X" = mostenit; "Din lat. X" = imprumut savant; "+ suf." = formatie interna."""
import json, re, sys, collections
import pandas as pd

def norm(s): return (s or "").lower().replace("ş","ș").replace("ţ","ț").strip()
# DEX '98 nu separa consecvent mostenit / savant ("Din lat. homo", "Lat. canis"), deci latinul e o clasa
LANG = [("latin", r"^(lat|lat\. pop|lat\. med|lat\. sav)\b"),
        ("slav", r"^(sl|v\. ?sl|bg|scr|rus|ucr|pol|ceh|slavon|sb)\b"),
        ("francez", r"^fr\b"), ("italian", r"^it\b"), ("german", r"^(germ|sas)\b"),
        ("maghiar", r"^magh\b"), ("turc", r"^tc\b"), ("grecesc", r"^(ngr|gr|mgr)\b"),
        ("englez", r"^engl\b"), ("albanez/substrat", r"^(alb|cuv\. autoh)\b"),
        ("necunoscut", r"^(et\. nec|probabil|onomat)")]

def etym(rep):
    s = (rep or "").replace("\n", " ")
    m = re.search(r"\]?\s[-–]\s(.*)$", s)
    if not m: return "nedeterminat"
    t = norm(re.sub(r"[@#$%]", "", m.group(1)))
    t = re.sub(r"\^\d", "", t)
    if " + " in t or t.startswith("de la ") or re.match(r"^[a-zăâîșț]+- \+", t):
        return "formație internă"
    t = re.sub(r"^((din|cf\.|după|cuv\.|comp\.|refăcut după|var\. a lui)\s+)+", "", t)
    for name, pat in LANG:
        if re.search(pat, t): return name
    return "altele"

def main(path):
    k = json.load(open(path, encoding="utf8"))
    K, C, M = set(k["kernel"]), set(k["core"]), set(k["minset"])
    import kernel; D = kernel.load_defs((1, 2))
    e = {}
    for lex, rep in zip(D.lexicon, D.internalRep):
        h = norm(lex)
        if h not in e or e[h] in ("nedeterminat", "altele"): e[h] = etym(rep)
    H = set(e)
    layers = {"MinSet": M, "Core": C, "Kernel": K, "Rest": H - K, "Tot dicț.": H}
    cats = ["latin", "slav", "francez", "formație internă", "grecesc", "turc", "maghiar", "german",
            "italian", "englez", "albanez/substrat", "necunoscut", "altele", "nedeterminat"]
    print(f"{'categorie':<18}" + "".join(f"{n:>10}" for n in layers))
    for c in cats:
        row = []
        for n, s in layers.items():
            s = s & H; row.append(sum(1 for w in s if e[w] == c) / max(1, len(s)))
        print(f"{c:<18}" + "".join(f"{x:>10.1%}" for x in row))
    print("\nGraur 1954 (publicat, 1419 cuvinte): latin ~60%, slav 21.49%, internațional 5.85%, necunoscut 4.65%")

if __name__ == "__main__":
    main(sys.argv[1])
