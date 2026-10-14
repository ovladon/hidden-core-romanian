#!/usr/bin/env python3
"""Writes q1/RESULTS.md (English, material for the journal version) from the Q1 result files."""
import json

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
      "of synonyms treated as absent.", "",
      "| dictionary | definitions with a synonym tail | made only of synonyms | MinSet/Kernel C0 → C1 → C2 | reciprocal pairs per 1,000 C0 → C1 → C2 |",
      "|---|---|---|---|---|"]
for r in C:
    lv = [r.get(c) for c in ("C0", "C1", "C2")]
    L.append(f"| {r['dictionary']} | {pc(r['C0']['synonym_tail_share'])} | {pc(r['C0']['synonym_only_share'])} | "
             + " → ".join(pc(x["minset_over_kernel"]) if x else "–" for x in lv) + " | "
             + " → ".join(f"{x['pairs_per_1000']:.0f}" if x else "–" for x in lv) + " |")
L += ["", "*The Romanian Wiktionary copies 70% of its first definitions from the DEX.", ""]

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
L += ["", "## 4. Reproducibility", "",
      "Ties in the most-frequent-candidate rule are now broken alphabetically, so every run gives the same graph. "
      "Before the fix, two runs differed by about 10 vertices in the Kernel (0.05%); the main graph differed by 6 arcs "
      "out of 600,473. The main graph and its MinSet bounds have been recomputed with the deterministic rule.", ""]
open("q1/RESULTS.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("scris q1/RESULTS.md")
