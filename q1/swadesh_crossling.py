#!/usr/bin/env python3
"""Q1, cross-linguistic: does the Kernel contain the basic vocabulary in every language?

The Swadesh list (207 meanings) of each language is read from the English Wiktionary appendices
(q1/raw/swadesh/<Language>_html.json, CC BY-SA). For every dictionary processed with the same procedure
(crossling/graphs/<code>_{freq,all}.json, crossling/wordnet_*.json), we compute the share of the Swadesh headwords
that lie in the Kernel and in the MinSet (smallest grounding set found), the share expected by chance and a
hypergeometric p-value.

  python3 -I q1/swadesh_crossling.py        # writes q1/swadesh_crossling.json
"""
import json, re, sys, unicodedata
from scipy.stats import hypergeom

LANG = {"dex": "Romanian", "ro_wikt": "Romanian", "it": "Italian", "es": "Spanish", "pt": "Portuguese", "fr": "French",
        "en": "English", "simple": "English", "wordnet": "English", "de": "German", "nl": "Dutch", "pl": "Polish",
        "cs": "Czech", "ru": "Russian", "el": "Greek"}
STRESS = re.compile("[̀́]")


def nf(s):
    return STRESS.sub("", unicodedata.normalize("NFC", s)).lower().strip()


def swadesh(language):
    h = json.load(open(f"q1/raw/swadesh/{language}_html.json", encoding="utf8"))["parse"]["text"]
    words = set()
    for row in re.findall(r"<tr>(.*?)</tr>", h, re.S)[1:]:
        cells = [re.sub(r"<[^>]+>", " ", c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if len(cells) < 3: continue
        cell = re.sub(r"\([^)]*\)", " ", cells[2])
        for item in re.split(r"[,;/]|\bor\b", cell):
            w = nf(re.sub(r"&#\d+;|&\w+;", " ", item))
            if w and re.fullmatch(r"[^\W\d_]+(?:-[^\W\d_]+)?", w): words.add(w)
    return words


def files(code, reg):
    if code == "wordnet": return f"crossling/wordnet_{reg}.json", "crossling/wordnet_headwords.txt"
    return f"crossling/graphs/{code}_{reg}.json", f"crossling/graphs/{code}_headwords.txt"


out = {}
for code, language in LANG.items():
    sw = swadesh(language)
    res = {"language": language, "swadesh_words": len(sw)}
    for reg in ("freq", "all"):
        jf, hf = files(code, reg)
        try:
            d = json.load(open(jf, encoding="utf8"))
        except FileNotFoundError:
            continue
        H = {l.strip() for l in open(hf, encoding="utf8") if l.strip()}
        K, M, N = set(d["kernel"]), set(d["minset_upper_bound_set"]), len(H)
        S = sw & H
        r = {"headwords": N, "swadesh_in_dictionary": len(S)}
        for name, layer in (("kernel", K), ("minset", M)):
            k = len(S & layer)
            r[name] = {"share": k / len(S), "expected": len(layer) / N, "enrichment": (k / len(S)) / (len(layer) / N),
                       "p": float(hypergeom.sf(k - 1, N, len(layer), len(S)))}
        res[reg] = r
    out[code] = res
json.dump(out, open("q1/swadesh_crossling.json", "w"), indent=1, ensure_ascii=False)
pc = lambda x: f"{100 * x:5.1f}%"
print(f"{'dictionary':10s} {'list':>5s} {'found':>5s} | {'Kernel (chance)':>18s} | {'MinSet (chance)':>18s} | p (Kernel)")
for code, r in out.items():
    f = r.get("freq")
    if not f: continue
    print(f"{code:10s} {r['swadesh_words']:5d} {f['swadesh_in_dictionary']:5d} | {pc(f['kernel']['share'])} ({pc(f['kernel']['expected'])}) | "
          f"{pc(f['minset']['share'])} ({pc(f['minset']['expected'])}) | {f['kernel']['p']:.1e}")
