#!/usr/bin/env python3
"""Q1, cross-linguistic: are Kernel words acquired earlier, and are they more concrete, in every language with norms?

Norms come from NoRaRe and Concepticon (q1/raw/norare/; the subsets of each published norm that are linked to
Concepticon concepts): age of acquisition (AoA) and concreteness, in the language of each dictionary. Romanian has no
published norms of this kind. For each dictionary (regime freq) and norm: number of normed headwords, mean value by
layer, and AUC = probability that a random Kernel word has a lower AoA (or a higher concreteness) than a random word
outside the Kernel; the same for the MinSet against the rest of the Kernel.

  python3 -I q1/norms_crossling.py        # writes q1/norms_crossling.json
"""
import csv, json, re, unicodedata
import numpy as np
from scipy.stats import rankdata

STRESS = re.compile("[̀́]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower().strip()
# (fisier, coloana cuvant, coloana valoare, tip)
NORMS = {
    "en": [("Kuperman-2012-AoA", "ENGLISH", "ENGLISH_AOA_MEAN", "aoa"), ("Luniewska-2016-299", "ENGLISH", "ENGLISH_AOA", "aoa_299"),
           ("Brysbaert-2014a-Concreteness", "ENGLISH", "ENGLISH_CONCRETENESS_MEAN", "concreteness")],
    "nl": [("Brysbaert-2014-AoA", "DUTCH", "DUTCH_AoA_MEAN", "aoa"), ("Luniewska-2016-299", "DUTCH", "DUTCH_AOA", "aoa_299"),
           ("Brysbaert-2014b-Concreteness", "DUTCH", "DUTCH_CONCRETENESS_MEAN", "concreteness")],
    "es": [("Alonso-2015-AoA", "SPANISH", "SPANISH_AOA_MEAN", "aoa"), ("Luniewska-2016-299", "SPANISH", "SPANISH_AOA", "aoa_299"),
           ("Guasch-2016-AffectiveRatings", "SPANISH", "SPANISH_CONCRETENESS_MEAN", "concreteness")],
    "it": [("Montefinese-2019-AoA", "ITALIAN", "ITALIAN_AOA_MEAN", "aoa"), ("Luniewska-2016-299", "ITALIAN", "ITALIAN_AOA", "aoa_299"),
           ("Montefinese-2014-AffectiveRatings", "ITALIAN", "ITALIAN_CONCRETENESS_MEAN", "concreteness")],
    "pt": [("Cameirao-2010-AoA", "PORTUGUESE", "PORTUGUESE_AOA_MEAN", "aoa"),
           ("Cameirao-2010-AoA", "PORTUGUESE", "PORTUGUESE_CONCRETENESS_MEAN", "concreteness")],
    "pl": [("Imbir-2021-Ratings", "POLISH", "POLISH_AOA_MEAN", "aoa"), ("Luniewska-2016-299", "POLISH", "POLISH_AOA", "aoa_299"),
           ("Imbir-2021-Ratings", "POLISH", "POLISH_CONCRETENESS_MEAN", "concreteness")],
    "fr": [("Bonin-2018-Concreteness", "FRENCH", "FRENCH_CONCRETENESS_MEAN", "concreteness")],
    "de": [("Schroeder-2012-824", "GERMAN", "AOA_MEAN", "aoa"), ("Luniewska-2016-299", "GERMAN", "GERMAN_AOA", "aoa_299")],
    "ru": [("Miklashevsky-2018-506", "RUSSIAN", "AOA_MEAN", "aoa"), ("Luniewska-2016-299", "RUSSIAN", "RUSSIAN_AOA", "aoa_299")],
    "el": [("Luniewska-2016-299", "GREEK", "GREEK_AOA", "aoa_299")],
    "cs": [("Luniewska-2019-299", "CZECH", "CZECH_AOA", "aoa_299")],
}
DICTS = {"en": "en", "simple": "en", "wordnet": "en", "nl": "nl", "es": "es", "it": "it", "pt": "pt", "pl": "pl",
         "fr": "fr", "de": "de", "ru": "ru", "el": "el", "cs": "cs"}


def load(name, wcol, vcol):
    vals = {}
    for r in csv.DictReader(open(f"q1/raw/norare/{name}.tsv", encoding="utf8"), delimiter="\t"):
        w, v = nf(r.get(wcol)), (r.get(vcol) or "").replace(",", ".")
        try: v = float(v)
        except ValueError: continue
        if w and re.fullmatch(r"[^\W\d_]+", w): vals.setdefault(w, []).append(v)
    return {w: float(np.mean(v)) for w, v in vals.items()}


def auc(a, b):
    if len(a) == 0 or len(b) == 0: return None
    r = rankdata(np.concatenate([a, b]))
    return float((r[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b)))


out = {}
for code, lang in DICTS.items():
    jf = "crossling/wordnet_freq.json" if code == "wordnet" else f"crossling/graphs/{code}_freq.json"
    hf = "crossling/wordnet_headwords.txt" if code == "wordnet" else f"crossling/graphs/{code}_headwords.txt"
    d = json.load(open(jf, encoding="utf8")); H = {l.strip() for l in open(hf, encoding="utf8") if l.strip()}
    K, C, M = set(d["kernel"]), set(d["core"]), set(d["minset_upper_bound_set"])
    layer = lambda w: "MinSet" if w in M else "Core" if w in C else "Satellites" if w in K else "Rest"
    res = {}
    for name, wcol, vcol, kind in NORMS[lang]:
        V = {w: v for w, v in load(name, wcol, vcol).items() if w in H}
        sign = -1 if kind.startswith("aoa") else 1          # AoA mai mic = invatat mai devreme
        kin = np.array([sign * v for w, v in V.items() if w in K]); kout = np.array([sign * v for w, v in V.items() if w not in K])
        min_ = np.array([sign * v for w, v in V.items() if w in M]); kr = np.array([sign * v for w, v in V.items() if w in K and w not in M])
        by = {}
        for w, v in V.items(): by.setdefault(layer(w), []).append(v)
        res[f"{kind}:{name}"] = {"normed_headwords": len(V), "in_kernel": int(len(kin)),
                                 "mean_by_layer": {k: [round(float(np.mean(v)), 2), len(v)] for k, v in by.items()},
                                 "auc_kernel_vs_rest": auc(kin, kout), "auc_minset_vs_rest_of_kernel": auc(min_, kr)}
    out[code] = res
json.dump(out, open("q1/norms_crossling.json", "w"), indent=1, ensure_ascii=False)
print("AUC > 0.5: cuvintele din Kernel sunt invatate mai devreme (AoA) / sunt mai concrete (concreteness)")
for code, res in out.items():
    for k, r in res.items():
        a, b = r["auc_kernel_vs_rest"], r["auc_minset_vs_rest_of_kernel"]
        print(f"{code:8s} {k:45s} n={r['normed_headwords']:5d} (Kernel {r['in_kernel']:4d}) | AUC Kernel>Rest "
              f"{a if a is None else round(a, 2)} | AUC MinSet>Kernel {b if b is None else round(b, 2)}")
