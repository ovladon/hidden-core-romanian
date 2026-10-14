#!/usr/bin/env python3
"""Abstractul pentru EasyChair (max. 300 de cuvinte), din results/results.json -> .md, .txt, .docx, .pdf."""
import json, re, subprocess

R = json.load(open("../results/results.json", encoding="utf8"))
N = R["data"]["headwords"]; ai = R["regimes"]["ai"]
lb = ai.get("minset_lb_ilp", ai["minset_lb"]); ub = ai["minset_ub"]
G, S = R["graur"], R["swadesh"]
p = lambda x, d=0: f"{100 * x:.{d}f}%"
import sys as _s; _s.path.insert(0, "..")
from calib import calib, EN
CB = calib(R)
# comparatia translingvistica (crossling/summary.json): aceeasi procedura pe dictionarele altor limbi
XS = json.load(open("../crossling/summary.json", encoding="utf8"))
XO = [r for r in XS if r["language"] != "Romanian"]
NUMW = {5: "five", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 15: "fifteen", 20: "twenty", 25: "twenty-five"}
x_lang = NUMW[len({r["language"] for r in XO})]
x_lo = min(100 * r["freq"]["minset_lb"] for r in XO); x_hi = max(100 * r["all"]["minset_ub"] for r in XO)
_d = next(r for r in XS if r["code"] == "dex")["reciprocal_pairs_per_1000"]
_pp = [r["reciprocal_pairs_per_1000"] for r in XO]
x_rlo, x_rhi = NUMW[max(5, round(_d / max(_pp) / 5) * 5)], NUMW[round(_d / min(_pp) / 5) * 5]
body = f"""Dictionary definitions are inherently circular, as words are defined through other words. Consequently, a dictionary can only support lexical acquisition if part of its vocabulary is already known. Previous studies have shown that a dictionary represented as a directed graph contains a Kernel, from which all other words can be defined, and one or more minimal grounding sets (MinSets), the smallest sets of words that provide the lexical basis of the entire dictionary (Vincent-Lamarre et al., 2016).

We construct and analyse a graph representation of the second edition of the Dicționarul explicativ al limbii române ('Explanatory Dictionary of the Romanian Language', DEX), comprising {N:,} headwords and {ai['edges']:,} definitional relations. Because Romanian exhibits extensive inflection and lexical ambiguity, automatic lemmatisation and headword assignment were required; these were performed using a large language model and evaluated against a stronger language model and two model-free baselines. Across all methods, the resulting graph structure proved highly stable.

Our analysis reveals that the DEX Kernel contains {ai['kernel']:,} words ({100 * ai['kernel'] / N:.1f}% of all headwords), while its MinSets comprise between {lb:,} and {ub:,} words ({100 * lb / N:.1f}–{100 * ub / N:.1f}%). These proportions are substantially larger than those obtained with the same procedure for dictionaries of {x_lang} other languages (MinSets of {x_lo:.1f}–{x_hi:.1f}%). We show that this difference is primarily attributable to reciprocal definitional relations, particularly prevalent in the lexicographic practice of the DEX. Despite its graph-theoretic derivation, the Kernel exhibits a close correspondence with independently established notions of fundamental vocabulary: it contains {p(S['layers']['Kernel']['rate'])} of the Romanian equivalents of the Swadesh list, a standard list of about 200 basic meanings, and {p(G['all']['Kernel']['rate'], 1)} of the fundamental lexical stock proposed by Graur (1954).

These findings suggest that the latent structure of dictionary definitions captures a linguistically meaningful lexical core. More broadly, the results show that graph-theoretic approaches can uncover fundamental vocabulary layers in morphologically rich languages."""
words = len(body.split())
title = "The Hidden Core of Romanian: A Graph-Theoretic Analysis of Dictionary Definitions"
kw = "lexicography, dictionary graphs, symbol grounding, minimal grounding set, fundamental lexical stock, Romanian, DEX, large language models"
md = f"""# {title}

**Vlad Belciug, Elena Pelican**
“Ovidius” University of Constanța, Faculty of Mathematics and Informatics, Bd. Mamaia 124, Constanța, Romania
vlad.belciug@365.univ-ovidius.ro, epelican@univ-ovidius.ro

## Abstract

<!-- BODY-START -->
{body}
<!-- BODY-END -->

**Keywords:** {kw}
"""
open("ABSTRACT_v5.md", "w", encoding="utf8").write(md)
open("ABSTRACT_easychair.txt", "w", encoding="utf8").write(body + "\n")
it = body
it = it.replace("Dicționarul explicativ al limbii române", "*Dicționarul explicativ al limbii române*")
doc = f"""**{title}**

**Vlad Belciug, Elena Pelican**

*“Ovidius” University of Constanța, Faculty of Mathematics and Informatics, Bd. Mamaia 124, Constanța, Romania*

vlad.belciug@365.univ-ovidius.ro, epelican@univ-ovidius.ro

**Abstract**

{it}

**Keywords:** {kw}
"""
out = "ABSTRACT - The Hidden Core of Romanian"
# acelasi sablon si aceleasi stiluri ca lucrarea (Times New Roman, stilurile din instructiunile ConsILR-2026)
import os, sys
sys.path.insert(0, "../paper")
import build_docx as B
d = B.docx.Document(os.path.join("../paper", B.TEMPLATE))
B.clear_body(d); B.setup_styles(d)
B.para(d, "ArticleTitle", [(title.replace("'", "’"), {})])
d.add_paragraph(style="Authors")
B.para(d, "Authors", [("Vlad Belciug, Elena Pelican", {})])
d.add_paragraph(style="Authors")
for line in B.AFFIL: B.para(d, "Affiliation", [(line, {})])
B.para(d, "AffiliationEmail", [(B.EMAILS, {})])
B.para(d, "AbstractTitle", [("Abstract", {})])
# cuvintele romanesti (cu contextul lor, ca sa nu fie atinse cuvinte englezesti identice, ex. "are")
ITAL = [(" ", "Dicționarul explicativ al limbii române", " (")]
for par in body.split("\n\n"):
    par = re.sub(r"(?<!\w)'([^']+)'", r"‘\1’", par).replace("'", "’")      # ghilimele tipografice, ca in lucrare
    segs = [(par, {})]
    for pre, w, post in ITAL:
        nxt = []
        for t, f in segs:
            k = t.find(pre + w + post) if not f else -1
            if k < 0: nxt.append((t, f)); continue
            k += len(pre)
            nxt += [(t[:k], {}), (w, {"i": True, "lang": "ro-RO"}), (t[k + len(w):], {})]
        segs = [x for x in nxt if x[0]]
    B.para(d, "AbstractText", segs)
B.para(d, "Keywords", [("Keywords: ", {"b": True}), (kw, {})])
d.save(out + ".docx")
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", out + ".docx"], capture_output=True)
print(f"abstract: {words} cuvinte (limita 300) | scris ABSTRACT_v5.md, ABSTRACT_easychair.txt, {out}.docx/.pdf")
