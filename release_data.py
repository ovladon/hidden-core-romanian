#!/usr/bin/env python3
"""Writes the released data set (release/) from the analysis outputs, with self-explanatory file names.

All files are derived from the dexonline database (DEX, 2nd edition) and are distributed under the GNU GPL v3.
Graur's (1954) list is protected by copyright and is not included.

  python3 release_data.py
"""
import gzip, json, os, shutil

TAGS = {"llm": "src12_freq_noexpr_first_ai", "most_frequent": "src12_freq_noexpr_first", "all_candidates": "src12_all_noexpr_first"}
os.makedirs("release", exist_ok=True)
H = [w for w in open("out/headwords_src12.txt", encoding="utf8").read().split("\n") if w]
open("release/headwords.txt", "w", encoding="utf8").write("\n".join(H) + "\n")
for name, tag in TAGS.items():
    with open(f"out/graph_{tag}.tsv", encoding="utf8") as f, gzip.open(f"release/arcs_{name}.tsv.gz", "wt", encoding="utf8") as g:
        g.write("defining_word\tdefined_headword\n")
        shutil.copyfileobj(f, g)
    k = json.load(open(f"out/kernel_{tag}.json", encoding="utf8"))
    K, C, M = set(k["kernel"]), set(k["core"]), set(k["minset"])
    best = f"out/minset_exact_{tag}.json"
    if os.path.exists(best):
        e = json.load(open(best, encoding="utf8"))
        if len(e["minset_best"]) < len(M): M = set(e["minset_best"])
    with open(f"release/layers_{name}.tsv", "w", encoding="utf8") as g:
        g.write("headword\tlayer\tin_minset\n")
        for w in H:
            layer = "core" if w in C else "satellite" if w in K else "outside_kernel"
            g.write(f"{w}\t{layer}\t{int(w in M)}\n")
    open(f"release/minset_{name}.txt", "w", encoding="utf8").write("\n".join(sorted(M)) + "\n")
with open("out/pairs_src12_freq_noexpr_first_ai.tsv", encoding="utf8") as f, \
        open("release/reciprocal_pairs_llm.tsv", "w", encoding="utf8") as g:
    g.write("word_1\tword_2\tshared_stem\n")
    shutil.copyfileobj(f, g)
ch = json.load(open("ai/choices_haiku12.json", encoding="utf8"))
with open("release/llm_choices.tsv", "w", encoding="utf8") as g:
    g.write("defined_headword\tword_form\tchosen_headwords\n")
    for key in sorted(ch):
        v, t = key.split("\t")
        g.write(f"{v}\t{t}\t{','.join(ch[key]) if ch[key] else '-'}\n")
shutil.copy("results/results.json", "release/results.json")
print("scris release/:", ", ".join(sorted(os.listdir("release"))))
