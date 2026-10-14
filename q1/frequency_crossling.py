#!/usr/bin/env python3
"""Q1, cross-linguistic: are the inner layers made of more frequent words in every language?

Word frequencies: FrequencyWords, OpenSubtitles 2018, 50,000 most frequent forms per language (q1/raw/freq/, CC BY-SA).
The frequency of a headword is the sum of the frequencies of all its forms (citation form and inflected forms, from the
dictionary's own inflection data, q1/forms/<code>.json.gz); a form that can belong to several headwords is shared
equally among them. Headwords with no form in the list get frequency 0.
For each dictionary (regime freq): median frequency per million and share of headwords in the 50k list, by layer
(MinSet; Core outside the MinSet; Satellites outside the MinSet; outside the Kernel), and the probability that a
random Kernel word is more frequent than a random word outside the Kernel (AUC, ties counted as 1/2).

  python3 -I q1/frequency_crossling.py        # writes q1/frequency_crossling.json
"""
import gzip, json, re, unicodedata
import numpy as np
from scipy.stats import rankdata

FORMS = {"wordnet": "en"}   # WordNet: formele din Wiktionary-ul englez
FREQ = {"dex": "ro", "ro_wikt": "ro", "it": "it", "es": "es", "pt": "pt", "fr": "fr", "en": "en", "simple": "en",
        "wordnet": "en", "de": "de", "nl": "nl", "pl": "pl", "cs": "cs", "ru": "ru", "el": "el"}
STRESS = re.compile("[̀́]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s)).lower().strip()


def load_freq(lang):
    f = {}
    for line in open(f"q1/raw/freq/{lang}_50k.txt", encoding="utf8"):
        parts = line.split()
        if len(parts) == 2 and parts[1].isdigit(): f[nf(parts[0])] = f.get(nf(parts[0]), 0) + int(parts[1])
    total = sum(f.values())
    return {w: 1e6 * c / total for w, c in f.items()}


def auc(a, b):
    r = rankdata(np.concatenate([a, b]))
    return (r[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b))


out = {}
for code, lang in FREQ.items():
    jf = "crossling/wordnet_freq.json" if code == "wordnet" else f"crossling/graphs/{code}_freq.json"
    hf = "crossling/wordnet_headwords.txt" if code == "wordnet" else f"crossling/graphs/{code}_headwords.txt"
    d = json.load(open(jf, encoding="utf8"))
    H = [l.strip() for l in open(hf, encoding="utf8") if l.strip()]
    raw = load_freq(lang)
    fmap = json.load(gzip.open(f"q1/forms/{FORMS.get(code, code)}.json.gz", "rt", encoding="utf8"))
    Hs = set(H); F = {}
    for form, fr in raw.items():
        cands = (set(fmap.get(form, ())) | ({form} if form in Hs else set())) & Hs
        for l in cands: F[l] = F.get(l, 0.0) + fr / len(cands)
    K, C, M = set(d["kernel"]), set(d["core"]), set(d["minset_upper_bound_set"])
    layers = {"MinSet": [w for w in H if w in M], "Core": [w for w in H if w in C and w not in M],
              "Satellites": [w for w in H if w in K and w not in C and w not in M], "Rest": [w for w in H if w not in K]}
    res = {"language": lang, "headwords": len(H), "layers": {}}
    for name, ws in layers.items():
        v = np.array([F.get(w, 0.0) for w in ws])
        res["layers"][name] = {"n": len(ws), "median_per_million": float(np.median(v)) if len(v) else None,
                               "share_in_50k": float((v > 0).mean()) if len(v) else None}
    kv = np.array([F.get(w, 0.0) for w in H if w in K]); rv = np.array([F.get(w, 0.0) for w in H if w not in K])
    res["auc_kernel_vs_rest"] = float(auc(kv, rv))
    mv = np.array([F.get(w, 0.0) for w in H if w in M]); ov = np.array([F.get(w, 0.0) for w in H if w in K and w not in M])
    res["auc_minset_vs_rest_of_kernel"] = float(auc(mv, ov))
    out[code] = res
json.dump(out, open("q1/frequency_crossling.json", "w"), indent=1, ensure_ascii=False)
print(f"{'dictionary':10s} | {'median freq/million: MinSet  Core  Satellites  Rest':>52s} | {'in 50k list: MinSet/Rest':>24s} | AUC K>R  AUC M>K")
for code, r in out.items():
    L = r["layers"]
    med = "  ".join(f"{L[n]['median_per_million']:7.2f}" for n in ("MinSet", "Core", "Satellites", "Rest"))
    print(f"{code:10s} | {med:>52s} | {100 * L['MinSet']['share_in_50k']:9.0f}% / {100 * L['Rest']['share_in_50k']:4.0f}%      | "
          f"{r['auc_kernel_vs_rest']:.2f}     {r['auc_minset_vs_rest_of_kernel']:.2f}")
