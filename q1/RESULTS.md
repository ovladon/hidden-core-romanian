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

## 5. Basic vocabulary in the Kernel, in every language

Swadesh list (207 meanings) of each language, from the English Wiktionary appendices; dictionaries processed with the same procedure (regime: most frequent candidate).

| dictionary | Swadesh headwords | in Kernel | expected | in MinSet | expected | p (Kernel) |
|---|---|---|---|---|---|---|
| Romanian DEX | 158 | 96.8% | 32.2% | 67.7% | 9.6% | 4e-68 |
| Romanian Wiktionary* | 157 | 92.4% | 25.6% | 40.1% | 7.0% | 1e-70 |
| Italian | 197 | 88.3% | 14.7% | 28.4% | 1.7% | 4e-118 |
| Spanish | 206 | 92.2% | 12.0% | 44.2% | 1.5% | 1e-153 |
| Portuguese | 238 | 87.0% | 14.5% | 27.7% | 2.3% | 3e-138 |
| French | 190 | 94.7% | 6.4% | 47.4% | 1.0% | 8e-200 |
| English Wiktionary | 192 | 98.4% | 4.4% | 71.9% | 0.8% | 1e-250 |
| Simple English | 180 | 94.4% | 14.4% | 33.9% | 2.2% | 3e-130 |
| English WordNet | 186 | 95.7% | 15.2% | 42.5% | 2.2% | 5e-134 |
| German | 225 | 83.6% | 7.8% | 24.9% | 1.0% | 3e-168 |
| Dutch | 200 | 93.0% | 7.5% | 34.5% | 1.2% | 2e-189 |
| Polish | 247 | 79.8% | 9.3% | 22.7% | 1.2% | 9e-154 |
| Czech | 247 | 68.0% | 9.7% | 15.8% | 1.2% | 1e-109 |
| Russian | 297 | 86.5% | 5.0% | 35.7% | 0.7% | 2e-286 |
| Greek | 194 | 90.2% | 10.2% | 25.8% | 1.5% | 1e-149 |

## 6. Frequency

Lemma frequency = sum of the OpenSubtitles frequencies of all forms of the lemma (FrequencyWords, 50k list). AUC = probability that a random word of the first set is more frequent than a random word of the second.

| dictionary | in 50k list: MinSet | Core | Satellites | Rest | AUC Kernel > Rest | AUC MinSet > rest of Kernel |
|---|---|---|---|---|---|---|
| Romanian DEX | 41% | 49% | 15% | 10% | 0.65 | 0.53 |
| Romanian Wiktionary* | 33% | 56% | 23% | 10% | 0.65 | 0.47 |
| Italian | 77% | 75% | 53% | 26% | 0.77 | 0.62 |
| Spanish | 75% | 71% | 45% | 13% | 0.80 | 0.63 |
| Portuguese | 63% | 75% | 52% | 17% | 0.78 | 0.51 |
| French | 55% | 66% | 33% | 7% | 0.76 | 0.54 |
| English Wiktionary | 59% | 67% | 28% | 4% | 0.78 | 0.58 |
| Simple English | 96% | 99% | 92% | 67% | 0.85 | 0.60 |
| English WordNet | 68% | 82% | 51% | 27% | 0.77 | 0.55 |
| German | 64% | 65% | 44% | 14% | 0.75 | 0.58 |
| Dutch | 44% | 69% | 47% | 12% | 0.75 | 0.45 |
| Polish | 68% | 66% | 43% | 9% | 0.77 | 0.59 |
| Czech | 77% | 78% | 66% | 24% | 0.79 | 0.57 |
| Russian | 49% | 44% | 21% | 3% | 0.69 | 0.58 |
| Greek | 60% | 69% | 43% | 10% | 0.76 | 0.55 |

## 7. Age of acquisition and concreteness

Norms from NoRaRe / Concepticon in the language of each dictionary (Romanian has none). AUC > 0.5 means that Kernel words are acquired earlier (AoA) or are more concrete (concreteness) than words outside the Kernel.

| dictionary | norm | normed headwords | mean by layer: MinSet / Core / Satellites / Rest | AUC Kernel vs Rest | AUC MinSet vs rest of Kernel |
|---|---|---|---|---|---|
| English Wiktionary | aoa:Kuperman-2012-AoA | 2546 | 6.18 / 7.18 / 8.31 / 8.22 | 0.65 | 0.63 |
| English Wiktionary | aoa_299:Luniewska-2016-299 | 278 | 3.64 / 4.09 / 4.76 / 4.55 | 0.65 | 0.63 |
| English Wiktionary | concreteness:Brysbaert-2014a-Concreteness | 2518 | 3.77 / 3.91 / 4.29 / 4.24 | 0.39 | 0.45 |
| Simple English | aoa:Kuperman-2012-AoA | 2338 | 5.41 / 6.02 / 6.42 / 7.6 | 0.71 | 0.61 |
| Simple English | aoa_299:Luniewska-2016-299 | 276 | 3.75 / 3.64 / 3.92 / 4.22 | 0.65 | 0.50 |
| Simple English | concreteness:Brysbaert-2014a-Concreteness | 2322 | 3.79 / 3.71 / 4.16 / 4.01 | 0.43 | 0.50 |
| English WordNet | aoa:Kuperman-2012-AoA | 2529 | 5.96 / 6.59 / 7.47 / 7.93 | 0.65 | 0.60 |
| English WordNet | aoa_299:Luniewska-2016-299 | 276 | 3.63 / 3.9 / 3.93 / 4.2 | 0.60 | 0.57 |
| English WordNet | concreteness:Brysbaert-2014a-Concreteness | 2502 | 3.74 / 3.76 / 4.29 / 4.16 | 0.41 | 0.47 |
| Dutch | aoa:Brysbaert-2014-AoA | 248 | 6.1 / 6.72 / 7.86 / 7.74 | 0.64 | 0.64 |
| Dutch | aoa_299:Luniewska-2016-299 | 289 | 3.37 / 3.45 / 3.78 / 4.43 | 0.71 | 0.57 |
| Dutch | concreteness:Brysbaert-2014b-Concreteness | 789 | 3.63 / 3.78 / 4.2 / 3.97 | 0.46 | 0.43 |
| Spanish | aoa:Alonso-2015-AoA | 1193 | 4.96 / 5.26 / 5.37 / 5.63 | 0.58 | 0.55 |
| Spanish | aoa_299:Luniewska-2016-299 | 265 | 3.8 / 4.3 / 4.8 / 4.66 | 0.61 | 0.61 |
| Spanish | concreteness:Guasch-2016-AffectiveRatings | 329 | 5.15 / 5.31 / 5.61 / 5.78 | 0.39 | 0.47 |
| Italian | aoa:Montefinese-2019-AoA | 1011 | 5.07 / 5.58 / 5.63 / 6.31 | 0.62 | 0.59 |
| Italian | aoa_299:Luniewska-2016-299 | 265 | 3.23 / 3.54 / 4.06 / 4.09 | 0.64 | 0.62 |
| Italian | concreteness:Montefinese-2014-AffectiveRatings | 555 | 6.96 / 6.62 / 6.91 / 6.74 | 0.51 | 0.56 |
| Portuguese | aoa:Cameirao-2010-AoA | 227 | 3.2 / 3.66 / 3.66 / 4.33 | 0.66 | 0.59 |
| Portuguese | concreteness:Cameirao-2010-AoA | 22 | 5.62 / 4.57 / 6.6 / 4.57 | 0.54 | 0.59 |
| Polish | aoa:Imbir-2021-Ratings | 741 | 7.32 / 7.3 / 7.33 / 7.72 | 0.61 | 0.51 |
| Polish | aoa_299:Luniewska-2016-299 | 227 | 3.56 / 3.58 / 3.64 / 3.93 | 0.62 | 0.54 |
| Polish | concreteness:Imbir-2021-Ratings | 741 | 3.73 / 3.61 / 2.68 / 3.06 | 0.61 | 0.55 |
| French | concreteness:Bonin-2018-Concreteness | 686 | 3.71 / 3.85 / 4.52 / 4.08 | 0.42 | 0.44 |
| German | aoa:Schroeder-2012-824 | 722 | 2.71 / 3.07 / 3.48 / 4.4 | 0.75 | 0.62 |
| German | aoa_299:Luniewska-2016-299 | 292 | 2.89 / 3.17 / 3.29 / 3.87 | 0.68 | 0.61 |
| Russian | aoa:Miklashevsky-2018-506 | 486 | 5.3 / 5.65 / 4.65 / 6.31 | 0.64 | 0.54 |
| Russian | aoa_299:Luniewska-2016-299 | 265 | 3.0 / 3.18 / 2.98 / 3.72 | 0.67 | 0.59 |
| Greek | aoa_299:Luniewska-2016-299 | 128 | 3.27 / 3.58 / 3.83 / 4.02 | 0.66 | 0.62 |
| Czech | aoa_299:Luniewska-2019-299 | 246 | 2.62 / 3.38 / 3.17 / 3.73 | 0.65 | 0.75 |

In every language with norms, Kernel words are acquired earlier than the rest of the dictionary, and MinSet words earlier than the rest of the Kernel; the Satellites are more concrete than the Core in English, Dutch, Spanish, Italian and French, as Vincent-Lamarre et al. (2016) found for English.


## 8. Reproducibility

Ties in the most-frequent-candidate rule are now broken alphabetically, so every run gives the same graph. Before the fix, two runs differed by about 10 vertices in the Kernel (0.05%); the main graph differed by 6 arcs out of 600,473. The main graph and its MinSet bounds have been recomputed with the deterministic rule.

