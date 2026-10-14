#!/usr/bin/env python3
"""Completeaza paper_template.tex cu cifrele din results/results.json si compileaza PDF-ul.

  cd paper && python3 build_paper.py
"""
import json, os, re, shutil, subprocess

R = json.load(open("../results/results.json", encoding="utf8"))
N = R["data"]["headwords"]


def pct(x, d=1):
    return f"{100 * x:.{d}f}\\%"


def num(n):
    return f"{n:,}"


ai, fr, al = R["regimes"]["ai"], R["regimes"]["freq"], R["regimes"]["all"]
lb = lambda r: r.get("minset_lb_ilp", r["minset_lb"])
G, S = R["graur"], R["swadesh"]


def row(name, r):
    return (f"{name} & {num(r['kernel'])} ({pct(r['kernel']/N)}) & {num(r['core'])} ({pct(r['core']/N)}) & "
            f"{num(lb(r))}–{num(r['minset_ub'])} ({100*lb(r)/N:.1f}–{pct(r['minset_ub']/N)}) & {num(r['mutual_pairs'])}\\\\")


def inv(name, d):
    return (f"{name} & {num(d['Kernel']['n'])} & {pct(d['Kernel']['rate'])} & {pct(d['MinSet']['rate'])} & "
            f"{pct(d['Satellites']['rate'])}\\\\")


# glose englezesti pentru toate cuvintele romanesti generate automat (regula ConsILR: original (traducere))
GLOSS = {"arbore": "tree", "copac": "tree", "pom": "(fruit) tree", "lemn": "wood", "femeie": "woman", "nevastă": "wife",
         "muiere": "woman (popular)", "cioban": "shepherd", "păcurar": "shepherd (regional)", "doagă": "barrel stave",
         "săgeată": "arrow", "lumânare": "candle", "concert": "concert", "axiomă": "axiom",
         "amabil": "kind", "binevoitor": "benevolent", "primejdie": "danger", "risc": "risk", "balenă": "whale",
         "chit": "whale (learned)", "capelă": "chapel", "paraclis": "chapel (Orthodox)",
         "arici": "hedgehog", "mânz": "foal", "murg": "bay (horse)", "țap": "billy goat", "țarc": "pen, fold",
         "teasc": "wine press", "topor": "axe", "prag": "threshold", "ginere": "son-in-law", "socru": "father-in-law",
         "vișin": "sour-cherry tree", "fag": "beech",
         "acțiune": "action", "rezultat": "result", "persoană": "person", "formă": "form", "mare": "large",
         "plantă": "plant", "obiect": "object", "diminutiv": "diminutive", "mic": "small", "animal": "animal",
         "doi": "two", "corp": "body", "apă": "water", "substanță": "substance", "material": "material",
         "stare": "state", "culoare": "colour", "nume": "name", "servi": "serve", "față": "face", "timp": "time",
         "floare": "flower", "ajutor": "help", "boală": "illness", "caracter": "character", "cuvânt": "word",
         "element": "element", "sub": "under", "produs": "product", "lung": "long"}


def gl(w):
    if w not in GLOSS: raise SystemExit(f"lipseste glosa pentru: {w}")
    return GLOSS[w]


def pair(a, b):
    return (f"\\ro{{{a}}}--\\ro{{{b}}} (both `{gl(a)}')" if gl(a) == gl(b) else
            f"\\ro{{{a}}}--\\ro{{{b}}} (`{gl(a)}'--`{gl(b)}')")


ex = [pair(a, b) for a, b in R["pairs"]["examples"][:5]]
outk = [w for w in ["arici", "mânz", "murg", "țap", "țarc", "teasc", "topor", "prag", "ginere", "socru", "vișin", "fag"]
        if w in G["outside_kernel"]]
E = R["etymology"]
V = {
    "HW": num(N), "DEFS": num(R["data"]["definitions"]), "TOK": num(R.get("tokens", 773719)),
    "UNK": pct(ai["unk_rate"]), "AMB": pct(ai["ambig_rate"], 0),
    "AGREE_CONTENT": pct(R["validation"]["opus_random_content"]), "AGREE_FUNC": pct(R["validation"]["opus_random_function"]),
    "COST": f"{R['validation']['cost_usd']:.0f}",
    "K": num(ai["kernel"]), "K_PCT": pct(ai["kernel"] / N), "C": num(ai["core"]), "C_PCT": pct(ai["core"] / N),
    "M_LB": num(lb(ai)), "M_UB": num(ai["minset_ub"]), "M_LB_PCT": pct(lb(ai) / N), "M_UB_PCT": pct(ai["minset_ub"] / N),
    "GAP_PCT": pct((ai["minset_ub"] - lb(ai)) / ai["minset_ub"], 0), "GAP1": pct((ai["minset_ub"] - lb(ai)) / ai["minset_ub"]),
    "K_FREQ_PCT": pct(fr["kernel"] / N), "K_ALL_PCT": pct(al["kernel"] / N),
    "M_FREQ_LB_PCT": pct(lb(fr) / N), "M_ALL_UB_PCT": pct(al["minset_ub"] / N),
    "S_PCT": pct(R["layers"]["Satellites"]["share"]),
    "PAIRS": num(ai["mutual_pairs"]), "PAIRS_DERIV": pct(R["pairs"]["derivational"], 0),
    "PAIR_EXAMPLES": ", ".join(ex), "TWO_CYCLE_SHARE": pct(R.get("two_cycle_share", 0.98), 0),
    "SW_N": str(S["mapped"]), "SW_K": pct(S["layers"]["Kernel"]["rate"], 0), "SW_M": pct(S["layers"]["MinSet"]["rate"], 0),
    "G_LINKED": num(G["linked"]), "G_DISTINCT": num(G["distinct"]),
    "G_K": pct(G["all"]["Kernel"]["rate"]), "G_M": pct(G["all"]["MinSet"]["rate"]),
    "GC_M": pct(G["core"]["MinSet"]["rate"], 0), "GM_M": pct(G["middle"]["MinSet"]["rate"], 0),
    "GX_M": pct(G["maximal"]["MinSet"]["rate"], 0),
    "GC_K": pct(G["core"]["Kernel"]["rate"], 0), "GM_K": pct(G["middle"]["Kernel"]["rate"], 0),
    "GX_K": pct(G["maximal"]["Kernel"]["rate"], 0),
    "G_OUT": str(len(G["outside_kernel"])),
    "G_OUT_EXAMPLES": ", ".join(f"\\ro{{{w}}} `{gl(w)}'" for w in outk),
    "TOP_OVERLAP": f"{E['graur_in_top1419']} ({pct(E['graur_in_top1419'] / G['distinct'], 0)} of Graur's list)",
    "ET_G_LAT": pct(E["graur_list"].get("latin", 0), 0), "ET_G_SL": pct(E["graur_list"].get("slav", 0), 0),
    "ET_T_FR": pct(E["top1419_definers"].get("francez", 0), 0), "ET_T_LAT": pct(E["top1419_definers"].get("latin", 0), 0),
    "ET_T_SL": pct(E["top1419_definers"].get("slav", 0), 0),
    "AG_LAT": pct(E["classifier_agreement_with_graur"]["latin"]["agree"], 0),
    "AG_SL": pct(E["classifier_agreement_with_graur"]["slav"]["agree"], 0),
    "AG_MAG": pct(E["classifier_agreement_with_graur"]["maghiar"]["agree"], 0),
    "TABLE_REGIMES": "\n".join([row("Most frequent candidate", fr), row("Language model (main)", ai), row("All candidates", al)]),
    "TABLE_INVENTORIES": "\n".join([inv("Swadesh list", S["layers"]), inv("Graur: all", G["all"]),
                                    inv("Graur: most certain", G["core"]), inv("Graur: middle circle", G["middle"]),
                                    inv("Graur: maximal circle", G["maximal"])]),
}
WD = json.load(open("../slides/html_data.json", encoding="utf8"))["words"]
CATN = {"C": "most certain", "M": "middle circle", "X": "maximal circle", "": "not listed"}
LAYN = {"minset": "MinSet", "core": "Core (not MinSet)", "satellite": "Satellite", "rest": "outside Kernel"}
cases = [w for w in ["arbore", "copac", "pom", "lemn", "femeie", "nevastă", "muiere", "cioban", "păcurar", "doagă",
                     "săgeată", "lumânare", "concert", "axiomă"] if w in WD]
V["TABLE_CASES"] = "\n".join(f"\\ro{{{w}}} & `{gl(w)}' & {CATN[WD[w]['g']]} & {LAYN[WD[w]['l']]} & {WD[w]['o']:,} headwords\\\\"
                             for w in cases)
V["ARB_O"], V["COP_O"], V["FEM_O"] = (f"{WD[w]['o']:,}" for w in ("arbore", "copac", "femeie"))
import collections
STOP = {"de", "care", "și", "în", "un", "cu", "sau", "la", "se", "al", "el", "din", "fi", "avea", "pe", "despre", "pentru",
        "prin", "mai", "ei", "ca", "să", "după", "nu", "acest", "o", "a", "ce", "cel", "lui", "sine", "ea", "acela", "fel",
        "fără", "între", "spre", "până", "dintre", "foarte", "cineva", "ceva", "orice", "unul", "alt", "anumit", "rar", "face",
        "putea", "mult", "cât", "tot", "său", "iar", "dar", "decât", "cum", "unde", "când", "ori", "aici", "acolo", "chiar",
        "loc", "fapt", "parte", "lucru", "privitor", "aparține", "folosit", "adesea", "obicei", "sens", "fig", "pop", "reg"}
outdeg = collections.Counter()
for line in open("../out/graph_src12_freq_noexpr_first_ai.tsv", encoding="utf8"):
    u, v = line.rstrip("\n").split("\t"); outdeg[u] += 1
glemset = {r["lemma"] for r in json.load(open("../gold/graur1954/graur1954_lemmas.json", encoding="utf8")) if r["lemma"]}
top = [(w, n) for w, n in outdeg.most_common(400) if w not in STOP and len(w) > 2][:30]
cells = [f"\\ro{{{w}}}{'$^{G}$' if w in glemset else ''} `{gl(w)}' & {n:,}" for w, n in top]
V["TABLE_TOP"] = "\n".join(" & ".join(cells[i::10][:3]) + "\\\\" for i in range(10))
gap = (ai["minset_ub"] - lb(ai)) / ai["minset_ub"]
if ai.get("minset_exact") and ai["minset_exact"] == ai["minset_ub"]:
    V["MINSET_SENTENCE"] = ("The integer program closes the interval: the lower and upper bounds coincide, so this is the "
                            "exact size of a minimum grounding set.")
    V["MINSET_LIMITATION"] = ("The size of the MinSet is exact, but a dictionary has many MinSets of that size; the set we "
                              "analyse is one of them.")
else:
    V["MINSET_SENTENCE"] = (f"The interval is narrow: the integer program raises the lower bound well above the cycle "
                            f"packing, and the gap between the two bounds is {pct(gap)} of the upper one.")
    V["MINSET_LIMITATION"] = (f"The MinSet is bounded rather than computed exactly, although the gap between the bounds is "
                              f"only {pct(gap)}; moreover, a dictionary has many grounding sets of minimum size, and the "
                              f"one we analyse is the smallest we found.")
import sys as _s; _s.path.insert(0, "..")
from calib import calib, times_en, EN
CB = calib(R)
V.update({"WN_K": f"{CB['wn_k'][0]:.1f}--{CB['wn_k'][1]:.1f}\\%", "WN_M": f"{CB['wn_m'][0]:.1f}--{CB['wn_m'][1]:.1f}\\%",
          "VL_WN_K": f"{CB['vl_k']:.1f}\\%", "VL_WN_M": f"{CB['vl_m']:.1f}\\%", "WN_HW": num(CB["wn_headwords"]),
          "RK_TIMES": times_en(CB["rk"]), "RM_TIMES": times_en(CB["rm"]), "RK_N": EN[CB["rk"]], "RM_N": EN[CB["rm"]],
          "FW_N": str(CB["fw"]), "CO_K": f"{CB['co_k']:.1f}\\%", "CO_M": f"{CB['co_m'][0]:.1f}--{CB['co_m'][1]:.1f}\\%"})
# comparatia translingvistica (crossling/summary.json, crossling/ro_wikt_overlap.json)
XS = json.load(open("../crossling/summary.json", encoding="utf8"))
XO = [r for r in XS if r["language"] != "Romanian"]
XD = next(r for r in XS if r["code"] == "dex")
NUMW = {5: "five", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 15: "fifteen", 20: "twenty", 25: "twenty-five"}
def kratio(r, reg):
    d = r.get(reg, r["freq"]); return 100 * (d["minset_lb_n"] + d["minset_ub_n"]) / 2 / d["kernel_n"]
xr = [kratio(r, g) for r in XO for g in ("freq", "all")]
pp = [r["reciprocal_pairs_per_1000"] for r in XO]
V.update({"X_NLANG": NUMW[len({r["language"] for r in XO})],
          "X_M": f"{min(100 * r['freq']['minset_lb'] for r in XO):.1f}--{max(100 * r['all']['minset_ub'] for r in XO):.1f}\\%",
          "XD_K": f"{100 * XD['freq']['kernel']:.1f}--{100 * XD['all']['kernel']:.1f}\\%",
          "XD_M": f"{100 * XD['freq']['minset_lb']:.1f}--{100 * XD['all']['minset_ub']:.1f}\\%",
          "X_RATIO": f"{min(xr):.0f}\\% and {max(xr):.0f}\\%",
          "XD_RATIO": f"{min(kratio(XD, 'freq'), kratio(XD, 'all')):.0f}--{max(kratio(XD, 'freq'), kratio(XD, 'all')):.0f}\\%",
          "X_RLO": NUMW[max(5, round(XD["reciprocal_pairs_per_1000"] / max(pp) / 5) * 5)],
          "X_RHI": NUMW[round(XD["reciprocal_pairs_per_1000"] / min(pp) / 5) * 5],
          "RW_COPY": f"{100 * json.load(open('../crossling/ro_wikt_overlap.json'))['share_ge_0.8']:.0f}\\%"})
def xrow(r):
    f, a = r["freq"], r.get("all", r["freq"])
    k = sorted((kratio(r, "freq"), kratio(r, "all")))
    dic = {"DEX, 2nd ed. (dexonline)": "DEX", "Wiktionary (70% from DEX)": "Wiktionary$^{*}$",
           "Simple English Wiktionary": "Simple Wiktionary"}.get(r["dictionary"], r["dictionary"])
    kr = f"{k[0]:.0f}\\%" if round(k[0]) == round(k[1]) else f"{k[0]:.0f}--{k[1]:.0f}\\%"
    return (f"{r['language']} & {dic} & {num(r['headwords'])} & {100*f['kernel']:.1f}--{100*a['kernel']:.1f}\\% & "
            f"{100*f['minset_lb']:.1f}--{100*a['minset_ub']:.1f}\\% & {kr} & {r['reciprocal_pairs_per_1000']:.0f}\\\\")
V["TABLE_CROSSLING"] = "\n".join(xrow(r) for r in XS)
t = open("paper_template.tex", encoding="utf8").read()
missing = sorted(set(re.findall(r"<<(\w+)>>", t)) - set(V))
if missing: raise SystemExit(f"lipsesc valori pentru: {missing}")
for k, v in V.items():
    t = t.replace(f"<<{k}>>", v)
open("paper.tex", "w", encoding="utf8").write(t)
if not os.path.exists("figures"):
    os.symlink("../figures", "figures")
for cmd in (["pdflatex", "-interaction=nonstopmode", "paper.tex"], ["bibtex", "paper"],
            ["pdflatex", "-interaction=nonstopmode", "paper.tex"], ["pdflatex", "-interaction=nonstopmode", "paper.tex"]):
    subprocess.run(cmd, capture_output=True)
log = open("paper.log", encoding="utf8", errors="replace").read()
pages = re.findall(r"Output written on paper.pdf \((\d+) pages", log)
print("pagini:", pages[-1] if pages else "?", "| erori LaTeX:", len(re.findall(r"^! ", log, re.M)),
      "| referinte nedefinite:", len(re.findall(r"undefined", log)))
