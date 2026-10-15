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

C0 = the dictionary as it is; C1 = synonym tails removed ("…; arbore, pom"); C2 = C1 and definitions made only of synonyms treated as absent; C3 = C2 and every segment of at most two words between commas or semicolons removed (synonyms inside the definition).

| dictionary | synonym tail | only synonyms | short segments (C3) | MinSet/Kernel C0 → C1 → C2 → C3 | reciprocal pairs per 1,000 C0 → C1 → C2 → C3 |
|---|---|---|---|---|---|
| Romanian DEX | 12.1% | 4.0% | 36.9% | 28.5% → 22.3% → 21.4% → 16.2% | 128 → 74 → 68 → 33 |
| Romanian Wiktionary* | 12.7% | 9.7% | 23.7% | 26.6% → 17.2% → 16.4% → 12.8% | 87 → 28 → 25 → 12 |
| Italian | 0.2% | 3.1% | 23.5% | 10.5% → 10.4% → 10.4% → 11.0% | 15 → 15 → 15 → 15 |
| Spanish | 0.1% | 3.9% | 12.8% | 10.7% → 10.7% → 10.6% → 10.1% | 12 → 12 → 12 → 10 |
| Portuguese | 3.1% | 8.4% | 21.2% | 15.1% → 14.0% → 13.7% → 13.5% | 27 → 22 → 21 → 16 |
| French | 0.3% | 3.8% | 12.4% | 14.0% → 13.9% → 13.8% → 13.2% | 10 → 9 → 9 → 8 |
| English Wiktionary | 3.0% | 3.4% | 17.5% | 16.7% → 15.8% → 15.5% → 14.2% | 8 → 7 → 7 → 5 |
| Simple English | 0.3% | 0.2% | 7.8% | 15.1% → 15.0% → 15.0% → 15.1% | 26 → 25 → 25 → 22 |
| German | 0.4% | 1.6% | 40.2% | 11.1% → 11.0% → 11.0% → 10.6% | 9 → 8 → 8 → 7 |
| Dutch | 0.1% | 4.3% | 12.3% | 14.5% → 14.5% → 14.5% → 14.8% | 14 → 14 → 14 → 12 |
| Polish | 0.3% | 4.1% | 40.9% | 11.2% → 11.2% → 11.1% → 10.1% | 9 → 9 → 9 → 6 |
| Czech | 0.3% | 8.0% | 31.2% | 10.7% → 10.6% → 10.4% → 9.4% | 8 → 8 → 8 → 7 |
| Russian | 1.7% | 0.5% | 31.1% | 11.8% → 10.9% → 10.8% → 9.5% | 6 → 5 → 5 → 3 |
| Greek | 0.0% | 7.3% | 22.2% | 13.6% → 13.6% → 13.4% → 12.2% | 14 → 14 → 14 → 10 |

*The Romanian Wiktionary copies 70% of its first definitions from the DEX.

Removing synonym material in every position (C3 touches 37% of the DEX definitions and 8%–41% of the others) lowers the DEX ratio from 28.5% to 16.2% (-12.3 points), while the other dictionaries change by -2.6 to +0.6 points (10.5%–16.7% at C0, 9.4%–15.1% at C3). The DEX moves from 7.2 to 2.0 standard deviations above the mean of the others (n = 12 at C0, 12 at C3): synonym definition, in any position, accounts for most of the Romanian surplus, and what remains places the DEX just above the most circular of the other dictionaries.

### Are the removed segments synonyms? A check against the dexonline synonym relations

The dexonline editors record synonym relations when they structure entries (113,334 pairs of single-word lemmas). For the 34,064 DEX headwords with at least one recorded synonym, the share of definition material whose lemma is a recorded synonym of the headword:

| material | segments | segments with a recorded synonym | tokens that are recorded synonyms |
|---|---|---|---|
| synonym tails (removed by C1; reference) | 9,793 | 95.4% | 95.1% |
| segments of 1–2 words (removed by C3) | 29,086 | 58.7% | 51.3% |
| longer segments (kept) | 58,284 | 25.2% | 6.7% |

Two variants of C3 on the DEX separate the effect: C3syn removes only the short segments that contain a recorded synonym of the headword; C3non removes only the short segments of headwords with recorded synonyms that contain none.

| DEX | C2 | C3syn | C3non | C3 |
|---|---|---|---|---|
| MinSet/Kernel | 21.4% | 16.5% | 21.7% | 16.2% |

Removing only the recorded synonyms reproduces almost the whole effect of C3 (16.5% vs 16.2%); removing the other short segments does not lower the ratio (21.7% vs 21.4% at C2). The drop is therefore caused by synonyms, not by the removal of short material as such.

### Reciprocal pairs left after C2, by type (per 1,000 headwords)

| dictionary | all | synonym inside the definition | derivational | in parentheses | analytic |
|---|---|---|---|---|---|
| dex | 68.0 | 35.1 | 11.9 | 2.1 | 19.0 |
| ro_wikt | 24.7 | 15.2 | 3.2 | 0.4 | 5.9 |
| it | 14.6 | 1.6 | 3.5 | 0.6 | 8.9 |
| es | 12.3 | 2.0 | 1.9 | 0.5 | 7.8 |
| pt | 21.0 | 6.3 | 4.1 | 0.8 | 9.7 |
| fr | 9.3 | 1.7 | 2.1 | 0.8 | 4.8 |
| de | 8.3 | 1.5 | 1.5 | 0.9 | 4.4 |
| nl | 13.7 | 1.8 | 6.9 | 0.4 | 4.5 |
| pl | 8.7 | 3.2 | 2.4 | 0.3 | 2.9 |
| cs | 8.3 | 2.0 | 1.7 | 0.3 | 4.3 |
| ru | 4.9 | 1.6 | 1.5 | 0.3 | 1.4 |
| el | 13.7 | 3.8 | 2.3 | 1.5 | 6.1 |
| en | 7.1 | 2.2 | 1.5 | 0.5 | 3.0 |

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

## 4. Basic vocabulary in the Kernel, in every language

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

## 5. Frequency

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

## 6. Age of acquisition and concreteness

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


## 7. Human lemma links in every language

Wiktionary editors link the words of their definitions to lemma pages. These links are recovered from the extract (English) or from the wikitext dump of each edition (line matching, similarity ≥ 0.8), and used (i) to score the most-frequent-candidate rule on ambiguous forms and (ii) to build a third, "human" regime in which every linked ambiguous form takes the editors' lemma. For the Romanian DEX the same comparison is made in section 1 (language model and rule against the Romanian Wiktionary links).

| dictionary | entries with links | rule accuracy, deliberate links (n) | lenient† | rule accuracy, plain links (n) | MinSet/Kernel: most frequent / human / all candidates |
|---|---|---|---|---|---|
| Romanian DEX (via Romanian Wiktionary) | 42,980 | 55.3% (8,629); language model 81.3% | – | 62.9% (34,271) | 28.3% / – / 28.7% |
| Czech | 39,987 of 42,044 | 84.5% (4,895) | 93.3% | 80.7% (11,292) | 10.7% / 10.6% / 10.7% |
| German | 80,339 of 151,529 | 55.6% (2,916) | 89.0% | 79.8% (46,733) | 11.1% / 11.1% / 11.1% |
| Greek | 80,070 of 91,612 | 64.3% (5,342) | 74.4% | 63.7% (16,935) | 14.0% / 13.8% / 13.3% |
| English Wiktionary | 551,385 of 576,090 | 84.8% (7,756) | 96.4% | 62.8% (117,271) | 16.7% / 16.2% / 16.8% |
| Spanish | 41,197 of 104,017 | 84.2% (4,167) | 90.1% | 72.7% (21,965) | 10.6% / 10.5% / 10.8% |
| French | 269,048 of 300,014 | 68.3% (15,425) | 84.5% | 58.8% (239,080) | 13.6% / 13.2% / 14.3% |
| Italian | 46,864 of 62,091 | 66.2% (910) | 79.9% | 69.0% (36,604) | 10.3% / 10.0% / 10.6% |
| Dutch | 46,685 of 168,185 | 64.2% (109) | 84.4% | 78.8% (19,838) | 14.9% / 14.8% / 14.0% |
| Polish | 81,898 of 97,716 | 43.9% (28,889) | 90.9% | 77.0% (26,903) | 11.4% / 11.2% / 11.0% |
| Portuguese | 65,945 of 81,604 | 79.5% (2,970) | 89.9% | 75.5% (25,967) | 15.3% / 15.5% / 14.9% |
| Russian | 143,093 of 407,234 | 76.5% (5,561) | 88.7% | 59.8% (22,521) | 12.3% / 12.2% / 11.2% |

†Lenient: the chosen lemma is itself an inflected form of the editors' lemma and is either an adjective (participle) of that verb, e.g. Polish *dotyczący* for *dotyczyć*, German *verwendet* for *verwenden*, or a variant with the same part of speech (*Bakterie* for *Bakterium*). Homographs of another part of speech, such as the verb *bäumen* chosen for the noun *Baum* (dative plural *Bäumen*), remain errors.

In every language the human regime differs from the most-frequent regime by at most 0.5 percentage points of MinSet/Kernel: lemma assignment does not drive the cross-linguistic differences. On deliberate links (languages with at least 1,000) the rule is right for 44%–85% of the forms; it is weakest in Polish 44%, Romanian DEX 55%, German 56%, languages with rich inflection in which forms of different lemmas coincide. In Polish and German most of these disagreements are the participle convention (lenient accuracy 91% and 89%); over all languages the lenient accuracy of the rule is 74%–96%. For Romanian the language model raises the accuracy to 81%.


## 8. The language model in other languages

The disambiguation used for the DEX (Claude Haiku 4.5, fifteen definitions per request, numbered candidates) was run on the Wiktionaries with the weakest rule accuracy and scored against the editors' links. Strict: the chosen lemma equals the editors' lemma. Lenient: as in the previous section.

| dictionary | links | model, strict (95% CI) | model, lenient | rule, strict | rule, lenient | MinSet/Kernel: rule / model regime |
|---|---|---|---|---|---|---|
| Polish, deliberate | 28,510 | 48.3% (47.7–48.8%) | 93.6% | 43.7% | 90.9% |  |
| Polish, plain | 20,992 | 96.7% (96.5–97.0%) | 96.8% | 76.0% | 76.7% |  |
| Polish, all | 49,502 | 68.8% (68.4–69.2%) | 94.9% | 57.4% | 84.8% | 11.4% / 11.2% |
| German, deliberate | 2,874 | 58.7% (56.9–60.5%) | 88.8% | 55.5% | 88.9% |  |
| German, plain | 32,511 | 97.9% (97.7–98.0%) | 98.4% | 80.0% | 86.2% |  |
| German, all | 35,385 | 94.7% (94.5–94.9%) | 97.6% | 78.1% | 86.4% | 11.1% / 10.9% |

On plain links, where the editors' lemma is the form itself, the model is almost always right and well ahead of the rule. On deliberate links most strict disagreements follow one convention: the model keeps a participle that has its own entry where the editors link the verb (Polish *dotyczący → dotyczyć*, *związany → związać*; German *verwendet → verwenden*, *hergestellt → herstellen*). In German the remaining errors are mostly homographs across parts of speech (the verb *bäumen* for the noun *Baum*, from *Bäumen*; *tönen* for *Ton*). The ratio MinSet/Kernel hardly changes when the model replaces the rule.


## 9. MinSet: integer-programming bounds with certificates

Integer program with lazy cycle generation (HiGHS), at most one hour per graph or a gap of 0.2%. The upper bound is a concrete feedback vertex set; the lower bound is the dual bound of the program restricted to the cycles generated so far, a relaxation of the full problem. Both are checked by `q1/verificare/verify.py` (acyclicity of G − S; every constraint is a real cycle) and `q1/verificare/solve_lp.py` (an independent solve of the relaxed program). The packing bound needs no solver: integer weights on the certificate's cycles such that every vertex carries at most M give |S| ≥ Σy/M for every feedback vertex set S (`q1/verificare/packing.py`).

| graph | vertices on cycles | lower bound (run) | re-solved | packing bound | confirmed lower bound | upper bound | gap | Kernel | MinSet/Kernel |
|---|---|---|---|---|---|---|---|---|---|
| Romanian DEX, language-model regime (ConsILR graph) | 19,769 | 6,195 | 6,195 | 6,138 | 6,195 | 6,318 | 1.95% | 21,216 | 29.2%–29.8% |
| English WordNet | 9,541 | 1,609 | 1,609 | 1,589 | 1,609 | 1,703 | 5.52% | 11,752 | 13.7%–14.5% |
| Romanian DEX, same procedure | 17,822 | 5,442 | 5,442 | 5,393 | 5,442 | 5,560 | 2.12% | 19,088 | 28.5%–29.1% |
| Romanian Wiktionary* | 14,353 | 4,483 | 4,482 | 4,448 | 4,482 | 4,500 | 0.40% | 16,729 | 26.8%–26.9% |
| Italian | 7,162 | 842 | 842 | 840 | 842 | 887 | 5.07% | 8,240 | 10.2%–10.8% |
| Spanish | 10,534 | 1,216 | 1,216 | 1,210 | 1,216 | 1,336 | 8.98% | 11,528 | 10.5%–11.6% |
| Portuguese | 8,579 | 1,563 | 1,563 | 1,551 | 1,563 | 1,576 | 0.82% | 10,093 | 15.5%–15.6% |
| French | 13,743 | 2,195 | 2,194 | 2,186 | 2,194 | 2,312 | 5.10% | 16,129 | 13.6%–14.3% |
| English Wiktionary | 20,547 | 3,778 | 3,778 | 3,767 | 3,778 | 4,138 | 8.70% | 23,055 | 16.4%–17.9% |
| Simple English | 2,521 | 422 | 422 | 418 | 422 | 422 | exact | 2,979 | 14.2%–14.2% |
| German | 9,652 | 1,291 | 1,291 | 1,288 | 1,291 | 1,354 | 4.65% | 11,562 | 11.2%–11.7% |
| Dutch | 9,332 | 1,801 | 1,801 | 1,792 | 1,801 | 1,826 | 1.37% | 12,311 | 14.6%–14.8% |
| Polish | 7,055 | 973 | 973 | 972 | 973 | 1,005 | 3.18% | 8,466 | 11.5%–11.9% |
| Czech | 3,425 | 421 | 421 | 416 | 421 | 421 | exact | 3,913 | 10.8%–10.8% |
| Russian | 17,195 | 2,443 | 2,443 | 2,437 | 2,443 | 2,573 | 5.05% | 19,879 | 12.3%–12.9% |
| Greek | 7,440 | 1,289 | 1,289 | 1,284 | 1,289 | 1,311 | 1.68% | 9,209 | 14.0%–14.2% |

With these bounds the MinSet/Kernel intervals are narrow and do not overlap: 10.2%–17.9% for all dictionaries other than the Romanian ones, against 28–30% for the DEX. The confirmed lower bound is the larger of the re-solved and packing bounds, both established without trusting the run that produced the certificate (report: `q1/verificare/RAPORT_ro.md`).


## 10. Reproducibility

Ties in the most-frequent-candidate rule are now broken alphabetically, so every run gives the same graph. Before the fix, two runs differed by about 10 vertices in the Kernel (0.05%); the main graph differed by 6 arcs out of 600,473. The main graph and its MinSet bounds have been recomputed with the deterministic rule.

