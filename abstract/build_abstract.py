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
body = f"""Dictionaries define words by other words, so a dictionary can teach new words only to a reader who already knows part of its vocabulary. Representing a dictionary as a directed graph, in which each word points to the headwords in whose definitions it occurs, makes this part measurable (Vincent-Lamarre et al., 2016). The Kernel is the part from which all other headwords can be defined; a minimal grounding set (MinSet) is a smallest set of words from which every other headword can be learned through definitions alone.

We analyse this graph for the second edition of the DEX (Dicționarul explicativ al limbii române), digitised by dexonline: {N:,} headwords and {ai['edges']:,} definitional links. Because Romanian is richly inflected, many word forms in definitions are ambiguous (are: avea 'have' or ara 'plough'). A large language model assigns each to a headword; all results are repeated without the model, and integer linear programming bounds the MinSet.

The Kernel of the DEX contains {100 * ai['kernel'] / N:.1f}% of the headwords and the MinSet {100 * lb / N:.1f}–{100 * ub / N:.1f}%. Processed in the same way, dictionaries of {x_lang} other languages have MinSets of {x_lo:.1f}–{x_hi:.1f}%. The difference comes mainly from reciprocal definition, {x_rlo} to {x_rhi} times more frequent in the DEX: {ai['mutual_pairs']:,} pairs of headwords occur in each other's definitions (arbore–copac, both 'tree'). Although derived only from definitions, the Kernel contains {p(S['layers']['Kernel']['rate'])} of the Romanian equivalents of the Swadesh list, a standard list of about 200 basic meanings used in comparative linguistics, and {p(G['all']['Kernel']['rate'], 1)} of the 1,419 words that Graur (1954) proposed as the fundamental lexical stock of Romanian, against {100 * ai['kernel'] / N:.1f}% expected by chance. The words most used in definitions, in contrast, are mainly learned French loanwords. Dictionary definitions thus preserve a linguistically meaningful lexical core, and the graph gives lexicographers a map of circularity. Data and code are public."""
words = len(body.split())
title = "The Hidden Core of Romanian: The Words That Define All Others"
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
for w in ("arbore–copac", "Dicționarul explicativ al limbii române", "are:", "avea", "ara "):
    it = it.replace(w, f"*{w.rstrip(' :')}*" + (":" if w.endswith(":") else " " if w.endswith(" ") else ""))
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
ITAL = [("(", "Dicționarul explicativ al limbii române", ")"), ("(", "are", ":"), (" ", "avea", " "), (" ", "ara", " "),
        ("(", "arbore–copac", ",")]
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
