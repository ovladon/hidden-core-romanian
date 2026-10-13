#!/usr/bin/env python3
"""Abstractul pentru EasyChair (max. 300 de cuvinte), din results/results.json -> .md, .txt, .docx, .pdf."""
import json, re, subprocess

R = json.load(open("../results/results.json", encoding="utf8"))
N = R["data"]["headwords"]; ai = R["regimes"]["ai"]
lb = ai.get("minset_lb_ilp", ai["minset_lb"]); ub = ai["minset_ub"]
G, S = R["graur"], R["swadesh"]
p = lambda x, d=0: f"{100 * x:.{d}f}%"
body = f"""Dictionaries define words by other words, so every dictionary is circular: a reader who knows none of the defining words can learn nothing from it. Vincent-Lamarre et al. (2016) measured this circularity in English dictionaries by representing a dictionary as a directed graph in which each word is linked to the headwords in whose definitions it occurs. They computed two sets: the Kernel, the part of the dictionary from which all other headwords can be defined (7–12% of headwords), and the minimal grounding set (MinSet), the smallest set of words from which every other headword can be learned through definitions (about 1%).

We apply the method for the first time to Romanian, to the second edition of the DEX (Dicționarul explicativ al limbii române) digitised by dexonline ({N:,} headwords). Many word forms in definitions are ambiguous (are: avea 'have' or ara 'plough'). A large language model assigns each such form to a headword; on a random sample it agrees with a stronger model on {p(R['validation']['opus_random_content'])} of content-word decisions, and all results are repeated with two procedures that use no model.

The Kernel of the DEX contains {100 * ai['kernel'] / N:.1f}% of the headwords and the MinSet {100 * lb / N:.1f}–{100 * ub / N:.1f}%, three to five and about ten times, respectively, the proportions found in English. The main cause is reciprocal definition: {ai['mutual_pairs']:,} pairs of headwords occur in each other's definitions (arbore–copac, both 'tree'). The Kernel nevertheless contains the basic vocabulary: {p(S['layers']['Kernel']['rate'])} of the Romanian equivalents of the Swadesh list, a standard list of about 200 basic meanings used in comparative linguistics, and {p(G['all']['Kernel']['rate'], 1)} of the 1,419 words that Graur (1954) proposed as the fundamental lexical stock of Romanian, against {100 * ai['kernel'] / N:.1f}% expected by chance. The words used most often in definitions, by contrast, are mainly learned French loanwords. The data and code are publicly available."""
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
