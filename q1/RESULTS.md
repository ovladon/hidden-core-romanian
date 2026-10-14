# Q1 results (journal version, work in progress)

All numbers below are produced by the scripts in `q1/` and `crossling/`; no human participants were involved.

## 1. Accuracy of the language model against human labels

Romanian Wiktionary editors copied 42,980 first definitions from the DEX (similarity ≥ 0.8) and linked their words to lemmas by hand. These links are a gold standard made by humans for the forms that are ambiguous in the dexonline inflection tables. Deliberate links (`[[lemma|form]]`) are reliable; plain links (`[[form]]`) may point to the page of the form itself.

| labels | links | language model | 95% CI | lenient* | most frequent candidate |
|---|---|---|---|---|---|
| deliberate | 8,629 | 81.3% | 80.5–82.1% | 87.6% | 55.3% |
| plain | 34,271 | 86.8% | 86.4–87.1% | 95.4% | 62.9% |
| all | 42,900 | 85.7% | 85.3–86.0% | 93.8% | 61.4% |

*Lenient: a participle analysed as an adjective (or the reverse), or a variant that the DEX itself records (`Var.:`, e.g. *arbore/arbor*, *referi/refera*), is counted as correct.

Errors on deliberate links by type: lemma variant 534, noun vs verb 341, two nouns 295, noun vs adjective 241, other 128, function vs content 56, no choice 7, two verbs 6, participle vs adjective 4.
The most frequent single disagreement is *(se) referă*, linked by the editors to *referi* and by the model to *refera*, which the DEX records as a variant of *referi*.

**Effect on the results.** Replacing every model choice that contradicts a deliberate human link (1,612 choices) changes the Kernel from 33.2% to 33.3%, the MinSet bounds from 5,835–6,441 to 5,832–6,442 (greedy and cycle-packing bounds) and the reciprocal pairs from 8,761 to 8,743. The model's errors do not affect the conclusions.

## 2. Mechanism: graded counterfactuals, identical for every dictionary

C0 = the dictionary as it is; C1 = synonym tails removed ("…; arbore, pom"); C2 = C1 and definitions made only of synonyms treated as absent.

| dictionary | definitions with a synonym tail | made only of synonyms | MinSet/Kernel C0 → C1 → C2 | reciprocal pairs per 1,000 C0 → C1 → C2 |
|---|---|---|---|---|
| Romanian DEX | 12.1% | 4.0% | 28.5% → 22.3% → 21.4% | 128 → 74 → 68 |
| Romanian Wiktionary* | 12.7% | 9.7% | 26.6% → 17.2% → 16.4% | 87 → 28 → 25 |
| Italian | 0.2% | 3.1% | 10.5% → 10.4% → 10.4% | 15 → 15 → 15 |
| Spanish | 0.1% | 3.9% | 10.7% → 10.7% → 10.6% | 12 → 12 → 12 |
| Portuguese | 3.1% | 8.4% | 15.1% → 14.0% → 13.7% | 27 → 22 → 21 |
| French | 0.3% | 3.8% | 14.0% → 13.9% → 13.8% | 10 → 9 → 9 |
| English Wiktionary | 3.0% | 3.4% | 16.7% → 15.8% → 15.5% | 8 → 7 → 7 |
| Simple English | 0.3% | 0.2% | 15.1% → 15.0% → 15.0% | 26 → 25 → 25 |
| German | 0.4% | 1.6% | 11.1% → 11.0% → 11.0% | 9 → 8 → 8 |
| Dutch | 0.1% | 4.3% | 14.5% → 14.5% → 14.5% | 14 → 14 → 14 |
| Polish | 0.3% | 4.1% | 11.2% → 11.2% → 11.1% | 9 → 9 → 9 |
| Czech | 0.3% | 8.0% | 10.7% → 10.6% → 10.4% | 8 → 8 → 8 |
| Russian | 1.7% | 0.5% | 11.8% → 10.9% → 10.8% | 6 → 5 → 5 |
| Greek | 0.0% | 7.3% | 13.6% → 13.6% → 13.4% | 14 → 14 → 14 |

*The Romanian Wiktionary copies 70% of its first definitions from the DEX.

## 3. Statistics

- MinSet/Kernel: DEX 28.5%; other languages mean 13.0% (SD 2.1%, range 10.5%–16.7%); the DEX lies 7.4 standard deviations above the mean.
- MinSet/Kernel does not depend on dictionary size: Spearman ρ = 0.004 (n = 15); without the Romanian dictionaries ρ = 0.22 (p = 0.4706).
- Density of reciprocal pairs vs MinSet/Kernel: ρ = 0.532 (p = 0.0412) over all dictionaries, but only ρ = 0.28 (p = 0.3538) without the Romanian ones: the association is carried by the two Romanian dictionaries.

Reference inventories (Wilson 95% intervals):

| inventory | in Kernel | in MinSet |
|---|---|---|
| Swadesh | 97.7% (94.3–99.1%) | 61.7% (54.3–68.6%) |
| Graur all | 94.5% (93.2–95.6%) | 42.4% (39.8–45.0%) |
| Graur most certain | 96.6% (95.3–97.6%) | 48.9% (45.7–52.1%) |
| Graur middle | 91.2% (86.7–94.3%) | 25.5% (20.1–31.7%) |
| Graur maximal | 89.0% (84.4–92.4%) | 31.8% (26.2–38.0%) |

Graur's certainty groups (Fisher exact tests):

- Graur most certain vs Graur middle (Kernel): 96.6% vs 91.2%, odds ratio 2.76, p = 0.0013
- Graur most certain vs Graur middle (MinSet): 48.9% vs 25.5%, odds ratio 2.8, p = 2.1e-10
- Graur most certain vs Graur maximal (Kernel): 96.6% vs 89.0%, odds ratio 3.55, p = 1e-05
- Graur most certain vs Graur maximal (MinSet): 48.9% vs 31.8%, odds ratio 2.05, p = 1.9e-06
- Graur middle vs Graur maximal (Kernel): 91.2% vs 89.0%, odds ratio 1.28, p = 0.53
- Graur middle vs Graur maximal (MinSet): 25.5% vs 31.8%, odds ratio 0.73, p = 0.15

## 4. Reproducibility

Ties in the most-frequent-candidate rule are now broken alphabetically, so every run gives the same graph. Before the fix, two runs differed by about 10 vertices in the Kernel (0.05%); the main graph differed by 6 arcs out of 600,473. The main graph and its MinSet bounds have been recomputed with the deterministic rule.

