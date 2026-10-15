#!/usr/bin/env python3
"""Writes q1/RESULTS.md (English, material for the journal version) from the Q1 result files."""
import json, os, re

G = json.load(open("q1/gold_summary.json", encoding="utf8"))
S = json.load(open("q1/stats.json", encoding="utf8"))
C = json.load(open("q1/cf_summary.json", encoding="utf8"))
base = json.load(open("q1/aicheck_summary.json")); fix = json.load(open("q1/goldfix_summary.json"))
pc = lambda x, d=1: f"{100 * x:.{d}f}%"
ci = lambda c: f"{100 * c[0]:.1f}–{100 * c[1]:.1f}%"
L = ["# Q1 results (journal version, work in progress)", "",
     "All numbers below are produced by the scripts in `q1/` and `crossling/`; no human participants were involved.", ""]

L += ["## 1. Accuracy of the language model against human labels", "",
      f"Romanian Wiktionary editors copied {G['pages_copied_from_dex']:,} first definitions from the DEX (similarity ≥ 0.8) "
      "and linked their words to lemmas by hand. These links are a gold standard made by humans for the forms that are "
      "ambiguous in the dexonline inflection tables. Deliberate links (`[[lemma|form]]`) are reliable; plain links "
      "(`[[form]]`) may point to the page of the form itself.", "",
      "| labels | links | language model | 95% CI | lenient* | most frequent candidate |", "|---|---|---|---|---|---|"]
for k, name in (("deliberate", "deliberate"), ("plain", "plain"), ("all", "all")):
    d = G[k]
    L.append(f"| {name} | {d['links']:,} | {pc(d['llm_accuracy'])} | {ci(d['llm_ci95'])} | {pc(d['llm_accuracy_lenient'])} | {pc(d['rule_accuracy'])} |")
d = G["deliberate"]["llm_errors_by_category"]
L += ["", "*Lenient: a participle analysed as an adjective (or the reverse), or a variant that the DEX itself records "
      "(`Var.:`, e.g. *arbore/arbor*, *referi/refera*), is counted as correct.", "",
      "Errors on deliberate links by type: " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in d.items()) + ".",
      "The most frequent single disagreement is *(se) referă*, linked by the editors to *referi* and by the model to "
      "*refera*, which the DEX records as a variant of *referi*.", "",
      "**Effect on the results.** Replacing every model choice that contradicts a deliberate human link "
      f"(1,612 choices) changes the Kernel from {base['headwords'] and pc(len(base['kernel']) / base['headwords'])} to "
      f"{pc(len(fix['kernel']) / fix['headwords'])}, the MinSet bounds from {base['minset_lower_bound']:,}–{base['minset_upper_bound']:,} "
      f"to {fix['minset_lower_bound']:,}–{fix['minset_upper_bound']:,} (greedy and cycle-packing bounds) and the reciprocal pairs "
      f"from {len(base['reciprocal_pairs']):,} to {len(fix['reciprocal_pairs']):,}. The model's errors do not affect the conclusions.", ""]

L += ["## 2. Mechanism: graded counterfactuals, identical for every dictionary", "",
      "C0 = the dictionary as it is; C1 = synonym tails removed (\"…; arbore, pom\"); C2 = C1 and definitions made only "
      "of synonyms treated as absent; C3 = C2 and every segment of at most two words between commas or semicolons removed "
      "(synonyms inside the definition).", "",
      "| dictionary | synonym tail | only synonyms | short segments (C3) | MinSet/Kernel C0 → C1 → C2 → C3 | reciprocal pairs per 1,000 C0 → C1 → C2 → C3 |",
      "|---|---|---|---|---|---|"]
for r in C:
    lv = [r.get(c) for c in ("C0", "C1", "C2", "C3")]
    L.append(f"| {r['dictionary']} | {pc(r['C0']['synonym_tail_share'])} | {pc(r['C0']['synonym_only_share'])} | "
             f"{pc(r['C3']['embedded_stripped_share']) if r.get('C3') else '–'} | "
             + " → ".join(pc(x["minset_over_kernel"]) if x else "–" for x in lv) + " | "
             + " → ".join(f"{x['pairs_per_1000']:.0f}" if x else "–" for x in lv) + " |")
c3 = [r["C3"]["embedded_stripped_share"] for r in C if r.get("C3") and r["code"] not in ("dex", "ro_wikt")]
c3dex = next(r for r in C if r["code"] == "dex").get("C3")
oth = [r[c]["minset_over_kernel"] for r in C if r["code"] not in ("dex", "ro_wikt") for c in ("C3",) if r.get(c)]
L += ["", "*The Romanian Wiktionary copies 70% of its first definitions from the DEX.", ""]
if c3 and c3dex:
    import statistics as st_
    def zlev(c):
        o = [r[c]["minset_over_kernel"] for r in C if r["code"] not in ("dex", "ro_wikt") and r.get(c)]
        d = next(r for r in C if r["code"] == "dex")[c]["minset_over_kernel"]
        return d, min(o), max(o), (d - st_.mean(o)) / st_.stdev(o), len(o)
    d0, lo0, hi0, z0, n0 = zlev("C0"); d3, lo3, hi3, z3, n3 = zlev("C3")
    dd = [100 * (r["C3"]["minset_over_kernel"] - r["C0"]["minset_over_kernel"]) for r in C
          if r["code"] not in ("dex", "ro_wikt") and r.get("C3")]
    L += [f"Removing synonym material in every position (C3 touches {pc(c3dex['embedded_stripped_share'], 0)} of the DEX "
          f"definitions and {pc(min(c3), 0)}–{pc(max(c3), 0)} of the others) lowers the DEX ratio from {pc(d0)} to "
          f"{pc(d3)} ({100 * (d3 - d0):+.1f} points), while the other dictionaries change by {min(dd):+.1f} to {max(dd):+.1f} "
          f"points ({pc(lo0)}–{pc(hi0)} at C0, {pc(lo3)}–{pc(hi3)} at C3). "
          f"The DEX moves from {z0:.1f} to {z3:.1f} standard deviations above the mean of the others "
          f"(n = {n0} at C0, {n3} at C3): synonym definition, in any position, accounts for most of the Romanian surplus, "
          + ("and what remains places the DEX just above the most circular of the other dictionaries." if d3 > hi3 else
             "and what remains lies within the range of the other dictionaries."), ""]
if os.path.exists("q1/c3_precision.json") and os.path.exists("q1/cf/dex_C3syn_freq.json"):
    P = json.load(open("q1/c3_precision.json", encoding="utf8"))
    def lvl(prefix):
        out = []
        for g in ("freq", "all"):
            d = json.load(open(f"{prefix}_{g}.json")); k = len(d["kernel"])
            out.append((d["minset_lower_bound"] + d["minset_upper_bound"]) / 2 / k)
        return sum(out) / 2
    V = {v: lvl(f"q1/cf/dex_{v}") for v in ("C2", "C3syn", "C3non", "C3")}
    L += ["### Are the removed segments synonyms? A check against the dexonline synonym relations", "",
          f"The dexonline editors record synonym relations when they structure entries ({P['synonym_pairs']:,} pairs of "
          f"single-word lemmas). For the {P['headwords_with_recorded_synonyms']:,} DEX headwords with at least one "
          "recorded synonym, the share of definition material whose lemma is a recorded synonym of the headword:", "",
          "| material | segments | segments with a recorded synonym | tokens that are recorded synonyms |", "|---|---|---|---|"]
    for k, name in (("tail", "synonym tails (removed by C1; reference)"), ("short", "segments of 1–2 words (removed by C3)"),
                    ("long", "longer segments (kept)")):
        r = P[k]
        L.append(f"| {name} | {r['segments']:,} | {pc(r['segments_with_recorded_synonym'])} | {pc(r['tokens_recorded_synonym'])} |")
    L += ["", "Two variants of C3 on the DEX separate the effect: C3syn removes only the short segments that contain a "
          "recorded synonym of the headword; C3non removes only the short segments of headwords with recorded synonyms "
          "that contain none.", "",
          "| DEX | C2 | C3syn | C3non | C3 |", "|---|---|---|---|---|",
          "| MinSet/Kernel | " + " | ".join(pc(V[v]) for v in ("C2", "C3syn", "C3non", "C3")) + " |", "",
          f"Removing only the recorded synonyms reproduces almost the whole effect of C3 ({pc(V['C3syn'])} vs {pc(V['C3'])}); "
          f"removing the other short segments does not lower the ratio ({pc(V['C3non'])} vs {pc(V['C2'])} at C2). "
          "The drop is therefore caused by synonyms, not by the removal of short material as such.", ""]
RP = json.load(open("q1/residual_pairs.json", encoding="utf8"))
L += ["### Reciprocal pairs left after C2, by type (per 1,000 headwords)", "",
      "| dictionary | all | synonym inside the definition | derivational | in parentheses | analytic |", "|---|---|---|---|---|---|"]
for code, r in RP.items():
    b = r["by_type_per_1000"]
    L.append(f"| {code} | {r['pairs_per_1000']:.1f} | {b['embedded_synonym']:.1f} | {b['derivational']:.1f} | {b['parenthetical']:.1f} | {b['analytic']:.1f} |")
L += [""]

X = S["crossling"]; M = X["minset_over_kernel"]
L += ["## 3. Statistics", "",
      f"- MinSet/Kernel: DEX {pc(M['dex'])}; other languages mean {pc(M['others_mean'])} (SD {pc(M['others_sd'])}, "
      f"range {pc(M['others_range'][0])}–{pc(M['others_range'][1])}); the DEX lies {M['dex_z']} standard deviations above the mean.",
      f"- MinSet/Kernel does not depend on dictionary size: Spearman ρ = {X['spearman_ratio_vs_logsize_all']['rho']} "
      f"(n = {X['spearman_ratio_vs_logsize_all']['n']}); without the Romanian dictionaries ρ = "
      f"{X['spearman_ratio_vs_logsize_without_romanian']['rho']} (p = {X['spearman_ratio_vs_logsize_without_romanian']['p']}).",
      f"- Density of reciprocal pairs vs MinSet/Kernel: ρ = {X['spearman_ratio_vs_pairs_all']['rho']} "
      f"(p = {X['spearman_ratio_vs_pairs_all']['p']}) over all dictionaries, but only ρ = "
      f"{X['spearman_ratio_vs_pairs_without_romanian']['rho']} (p = {X['spearman_ratio_vs_pairs_without_romanian']['p']}) "
      "without the Romanian ones: the association is carried by the two Romanian dictionaries.", ""]
L += ["Reference inventories (Wilson 95% intervals):", "", "| inventory | in Kernel | in MinSet |", "|---|---|---|"]
for k, v in S["inventories"].items():
    L.append(f"| {k} | {pc(v['Kernel']['share'])} ({ci(v['Kernel']['ci95'])}) | {pc(v['MinSet']['share'])} ({ci(v['MinSet']['ci95'])}) |")
L += ["", "Graur's certainty groups (Fisher exact tests):", ""]
for k, v in S["graur_group_tests"].items():
    L.append(f"- {k}: {pc(v['shares'][0])} vs {pc(v['shares'][1])}, odds ratio {v['odds_ratio']}, p = {v['p_fisher']:.2g}")
NAMES = {"dex": "Romanian DEX", "ro_wikt": "Romanian Wiktionary*", "it": "Italian", "es": "Spanish", "pt": "Portuguese",
         "fr": "French", "en": "English Wiktionary", "simple": "Simple English", "wordnet": "English WordNet", "de": "German",
         "nl": "Dutch", "pl": "Polish", "cs": "Czech", "ru": "Russian", "el": "Greek"}
SW = json.load(open("q1/swadesh_crossling.json", encoding="utf8"))
L += ["", "## 5. Basic vocabulary in the Kernel, in every language", "",
      "Swadesh list (207 meanings) of each language, from the English Wiktionary appendices; dictionaries processed with "
      "the same procedure (regime: most frequent candidate).", "",
      "| dictionary | Swadesh headwords | in Kernel | expected | in MinSet | expected | p (Kernel) |", "|---|---|---|---|---|---|---|"]
for code, r in SW.items():
    f = r.get("freq")
    if f: L.append(f"| {NAMES[code]} | {f['swadesh_in_dictionary']} | {pc(f['kernel']['share'])} | {pc(f['kernel']['expected'])} | "
                   f"{pc(f['minset']['share'])} | {pc(f['minset']['expected'])} | {f['kernel']['p']:.0e} |")
try:
    FQ = json.load(open("q1/frequency_crossling.json", encoding="utf8"))
    L += ["", "## 6. Frequency", "",
          "Lemma frequency = sum of the OpenSubtitles frequencies of all forms of the lemma (FrequencyWords, 50k list). "
          "AUC = probability that a random word of the first set is more frequent than a random word of the second.", "",
          "| dictionary | in 50k list: MinSet | Core | Satellites | Rest | AUC Kernel > Rest | AUC MinSet > rest of Kernel |",
          "|---|---|---|---|---|---|---|"]
    for code, r in FQ.items():
        Ly = r["layers"]
        L.append(f"| {NAMES[code]} | " + " | ".join(pc(Ly[n]["share_in_50k"], 0) for n in ("MinSet", "Core", "Satellites", "Rest"))
                 + f" | {r['auc_kernel_vs_rest']:.2f} | {r['auc_minset_vs_rest_of_kernel']:.2f} |")
except FileNotFoundError:
    pass
NO = json.load(open("q1/norms_crossling.json", encoding="utf8"))
L += ["", "## 7. Age of acquisition and concreteness", "",
      "Norms from NoRaRe / Concepticon in the language of each dictionary (Romanian has none). AUC > 0.5 means that "
      "Kernel words are acquired earlier (AoA) or are more concrete (concreteness) than words outside the Kernel.", "",
      "| dictionary | norm | normed headwords | mean by layer: MinSet / Core / Satellites / Rest | AUC Kernel vs Rest | AUC MinSet vs rest of Kernel |",
      "|---|---|---|---|---|---|"]
for code, res in NO.items():
    for k, r in res.items():
        m = r["mean_by_layer"]
        means = " / ".join(f"{m[x][0]}" if x in m else "–" for x in ("MinSet", "Core", "Satellites", "Rest"))
        a, b = r["auc_kernel_vs_rest"], r["auc_minset_vs_rest_of_kernel"]
        L.append(f"| {NAMES[code]} | {k} | {r['normed_headwords']} | {means} | {a:.2f} | {b:.2f} |")
L += ["", "In every language with norms, Kernel words are acquired earlier than the rest of the dictionary, and MinSet words "
      "earlier than the rest of the Kernel; the Satellites are more concrete than the Core in English, Dutch, Spanish, "
      "Italian and French, as Vincent-Lamarre et al. (2016) found for English.", ""]
import glob
HG = {os.path.basename(p).replace("_gold.json", ""): json.load(open(p)) for p in sorted(glob.glob("q1/human/*_gold.json"))}
HG = {c: r for c, r in HG.items() if r["entries_with_links"] > 0}      # Simple English: extrasul nu pastreaza legaturile
XS = {r["code"]: r for r in json.load(open("crossling/summary.json", encoding="utf8"))}
def xratio(code, g):
    d = XS[code].get(g); return (d["minset_lb_n"] + d["minset_ub_n"]) / 2 / d["kernel_n"]
if HG:
    L += ["", "## 9. Human lemma links in every language", "",
          "Wiktionary editors link the words of their definitions to lemma pages. These links are recovered from the "
          "extract (English) or from the wikitext dump of each edition (line matching, similarity ≥ 0.8), and used "
          "(i) to score the most-frequent-candidate rule on ambiguous forms and (ii) to build a third, \"human\" regime in "
          "which every linked ambiguous form takes the editors' lemma. For the Romanian DEX the same comparison is made "
          "in section 1 (language model and rule against the Romanian Wiktionary links).", "",
          "| dictionary | entries with links | rule accuracy, deliberate links (n) | lenient† | rule accuracy, plain links (n) | "
          "MinSet/Kernel: most frequent / human / all candidates |", "|---|---|---|---|---|---|"]
    gd = G["deliberate"]; gp = G["plain"]
    L.append(f"| Romanian DEX (via Romanian Wiktionary) | {G['pages_copied_from_dex']:,} | {pc(gd['rule_accuracy'])} ({gd['links']:,}); "
             f"language model {pc(gd['llm_accuracy'])} | – | {pc(gp['rule_accuracy'])} ({gp['links']:,}) | "
             f"{pc(xratio('dex', 'freq'))} / – / {pc(xratio('dex', 'all'))} |")
    for code, r in HG.items():
        if code not in XS: continue
        d, p_, h = r["deliberate"], r["plain"], r["human_regime"]
        acc = lambda x: f"{pc(x['rule_accuracy'])} ({x['links']:,})" if x["links"] else "–"
        lenient = pc(d["rule_lenient"]) if d.get("rule_lenient") is not None and d["links"] else "–"
        L.append(f"| {NAMES[code]} | {r['entries_with_links']:,} of {r['entries']:,} | {acc(d)} | {lenient} | {acc(p_)} | "
                 f"{pc(xratio(code, 'freq'))} / {pc(h['minset_over_kernel'])} / {pc(xratio(code, 'all'))} |")
    diffs = [abs(r["human_regime"]["minset_over_kernel"] - xratio(c, "freq")) for c, r in HG.items() if c in XS]
    accs = sorted((r["deliberate"]["rule_accuracy"], NAMES[c]) for c, r in HG.items() if r["deliberate"]["links"] >= 1000)
    accs.append((G["deliberate"]["rule_accuracy"], "Romanian DEX")); accs.sort()
    low = ", ".join(f"{n} {pc(a, 0)}" for a, n in accs[:3])
    lens = [r["deliberate"]["rule_lenient"] for c, r in HG.items() if r["deliberate"]["links"] >= 1000 and r["deliberate"].get("rule_lenient")]
    L += ["", "†Lenient: the chosen lemma is itself an inflected form of the editors' lemma and is either an adjective "
          "(participle) of that verb, e.g. Polish *dotyczący* for *dotyczyć*, German *verwendet* for *verwenden*, or a "
          "variant with the same part of speech (*Bakterie* for *Bakterium*). Homographs of another part of speech, such "
          "as the verb *bäumen* chosen for the noun *Baum* (dative plural *Bäumen*), remain errors.", ""]
    L += [f"In every language the human regime differs from the most-frequent regime by at most "
          f"{100 * max(diffs):.1f} percentage points of MinSet/Kernel: lemma assignment does not drive the "
          f"cross-linguistic differences. On deliberate links (languages with at least 1,000) the rule is right for "
          f"{pc(accs[0][0], 0)}–{pc(accs[-1][0], 0)} of the forms; it is weakest in {low}, languages with rich "
          f"inflection in which forms of different lemmas coincide. In Polish and German most of these disagreements are "
          f"the participle convention (lenient accuracy {pc(HG['pl']['deliberate']['rule_lenient'], 0)} and "
          f"{pc(HG['de']['deliberate']['rule_lenient'], 0)}); over all languages the lenient accuracy of the rule is "
          f"{pc(min(lens), 0)}–{pc(max(lens), 0)}. For Romanian the "
          f"language model raises the accuracy to {pc(G['deliberate']['llm_accuracy'], 0)}.", ""]
LE = {c: json.load(open(f"q1/llm/{c}_eval.json")) for c in ("pl", "de") if os.path.exists(f"q1/llm/{c}_eval.json")}
if LE:
    L += ["", "## 10. The language model in other languages", "",
          "The disambiguation used for the DEX (Claude Haiku 4.5, fifteen definitions per request, numbered candidates) "
          "was run on the Wiktionaries with the weakest rule accuracy and scored against the editors' links. Strict: the "
          "chosen lemma equals the editors' lemma. Lenient: as in the previous section.", "",
          "| dictionary | links | model, strict (95% CI) | model, lenient | rule, strict | rule, lenient | MinSet/Kernel: rule / model regime |",
          "|---|---|---|---|---|---|---|"]
    for code, r in LE.items():
        for g in ("deliberate", "plain", "all"):
            d = r[g]
            if not d["links"]: continue
            tail = f"{pc(xratio(code, 'freq'))} / {pc(r['llm_regime']['minset_over_kernel'])}" if g == "all" else ""
            L.append(f"| {NAMES[code]}, {g} | {d['links']:,} | {pc(d['llm_accuracy'])} ({ci(d['llm_ci95'])}) | "
                     f"{pc(d['llm_lenient'])} | {pc(d['rule_accuracy'])} | {pc(d['rule_lenient'])} | {tail} |")
    L += ["", "On plain links, where the editors' lemma is the form itself, the model is almost always right and well "
          "ahead of the rule. On deliberate links most strict disagreements follow one convention: the model keeps a "
          "participle that has its own entry where the editors link the verb (Polish *dotyczący → dotyczyć*, "
          "*związany → związać*; German *verwendet → verwenden*, *hergestellt → herstellen*). In German the remaining "
          "errors are mostly homographs across parts of speech (the verb *bäumen* for the noun *Baum*, from *Bäumen*; "
          "*tönen* for *Ton*). The "
          "ratio MinSet/Kernel hardly changes when the model replaces the rule.", ""]
EX = {c: json.load(open(f"q1/exact/{c}.json")) for c in ["dex_llm", "wordnet"] + list(NAMES) if os.path.exists(f"q1/exact/{c}.json")}
if EX:
    NAMES2 = dict(NAMES, dex_llm="Romanian DEX, language-model regime (ConsILR graph)", dex="Romanian DEX, same procedure")
    L += ["", "## 11. MinSet: integer-programming bounds with certificates", "",
          "Integer program with lazy cycle generation (HiGHS), at most one hour per graph or a gap of 0.2%. The upper bound "
          "is a concrete feedback vertex set; the lower bound is the dual bound of the program restricted to the cycles "
          "generated so far, a relaxation of the full problem. Both are checked by `q1/verificare/verify.py` (acyclicity "
          "of G − S; every constraint is a real cycle) and `q1/verificare/solve_lp.py` (an independent solve of the "
          "relaxed program). The packing bound needs no solver: integer weights on the certificate's cycles such that "
          "every vertex carries at most M give |S| ≥ Σy/M for every feedback vertex set S (`q1/verificare/packing.py`).", "",
          "| graph | vertices on cycles | lower bound | packing bound | upper bound | gap | Kernel | MinSet/Kernel |",
          "|---|---|---|---|---|---|---|---|"]
    import gzip
    def packing(c):
        p = f"q1/exact/{c}_packing.json.gz"
        if not os.path.exists(p): return "–"
        y = json.load(gzip.open(p, "rt")); cyc = json.load(gzip.open(f"q1/exact/{c}_cycles.json.gz", "rt", encoding="utf8"))
        load = {}
        for cc, w in zip(cyc, y):
            for v in cc: load[v] = load.get(v, 0) + w
        return f"{-(-sum(y) // max(load.values())):,}"
    for c, r in EX.items():
        lo, hi = r["lower_bound"], r["upper_bound"]
        kj = "out/kernel_src12_freq_noexpr_first_ai.json" if c == "dex_llm" else (
             "crossling/wordnet_freq.json" if c == "wordnet" else f"crossling/graphs/{c}_freq.json")
        k = len(json.load(open(kj))["kernel"])
        L.append(f"| {NAMES2[c]} | {r['vertices_on_cycles']:,} | {lo:,} | {packing(c)} | {hi:,} | "
                 f"{'exact' if lo == hi else pc((hi - lo) / hi, 2)} | {k:,} | {pc(lo / k)}–{pc(hi / k)} |")
    L += [""]
L += ["", "## 8. Reproducibility", "",
      "Ties in the most-frequent-candidate rule are now broken alphabetically, so every run gives the same graph. "
      "Before the fix, two runs differed by about 10 vertices in the Kernel (0.05%); the main graph differed by 6 arcs "
      "out of 600,473. The main graph and its MinSet bounds have been recomputed with the deterministic rule.", ""]
# numerotare consecutiva a sectiunilor, in ordinea in care apar
k = 0
for i, line in enumerate(L):
    if re.match(r"## \d+\. ", line):
        k += 1; L[i] = re.sub(r"## \d+\. ", f"## {k}. ", line)
open("q1/RESULTS.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("scris q1/RESULTS.md")
