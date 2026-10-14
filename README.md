# The Hidden Core of Romanian

Code and data for the paper

> Vlad Belciug and Elena Pelican. 2026. *The Hidden Core of Romanian: A Graph-Theoretic Analysis of Dictionary Definitions.* Submitted to ConsILR 2026 (Conference on Linguistic Resources and Tools for
> Processing Romanian), “Ovidius” University of Constanța, Faculty of Mathematics and Informatics.

The study represents the Romanian explanatory dictionary DEX (2nd edition, as digitised by
[dexonline](https://dexonline.ro)) as a directed graph, with an arc from a word to every headword in whose
definition it occurs. Following Vincent-Lamarre et al. (2016, *Topics in Cognitive Science* 8(3), 625–659), it
computes:

| set | definition |
|---|---|
| **Kernel** | what remains after repeatedly deleting the words that occur in no remaining definition; every other headword can be defined from it |
| **Core** | the largest strongly connected component of the Kernel |
| **Satellites** | the other strongly connected components of the Kernel |
| **MinSet** | a minimum grounding set: a smallest set of words from which every other headword can be learned through definitions alone (a minimum feedback vertex set; NP-hard, so it is given as an interval between proven bounds) |

A large language model (Claude Haiku 4.5) assigns each ambiguous word form in a definition to its headword. Every
result is also computed with two rules that use no model: the most frequent candidate, and all candidates.

## Main results (63,843 headwords)

| regime | Kernel | Core | MinSet (lower–upper bound) | reciprocal pairs |
|---|---|---|---|---|
| language model | 21,216 (33.2%) | 13,979 (21.9%) | 6,193–6,325 (9.7–9.9%) | 8,761 |
| most frequent candidate | 18,576 (29.1%) | 12,644 (19.8%) | 4,770–5,352 (7.5–8.4%) | 7,158 |
| all candidates | 23,207 (36.4%) | 15,704 (24.6%) | 6,230–6,978 (9.8–10.9%) | 9,897 |

The Kernel contains 97.7% of the Romanian Swadesh list (175 headwords) and 94.5% of the 1,401 headwords of
Graur's (1954) fundamental lexical stock, against 33.2% expected by chance. All numbers are in
[`release/results.json`](release/results.json).

## Calibration against English (`crossling/`)

The figures for English published by Vincent-Lamarre et al. were obtained with a different procedure. To compare like
with like, `crossling/wordnet_graph.py` applies our procedure to Princeton WordNet 3.0 (one of their four dictionaries;
single-word lemmas, first sense of each part of speech, no function words), and `crossling/content_only.py` recomputes
the DEX without its 557 function words, which they also excluded.

| dictionary, same procedure | Kernel | MinSet (bounds) |
|---|---|---|
| WordNet 3.0, most frequent candidate | 15.2% | 2.1–2.2% |
| WordNet 3.0, all candidates | 18.3% | 2.5–2.8% |
| DEX without function words (language model) | 33.3% | 9.1–10.1% (greedy / cycle packing) |

Under identical processing the Kernel of the DEX is about twice as large as that of WordNet and its MinSet about four
times as large (Vincent-Lamarre et al. report 11.5% and 1.3% for WordNet). A comparison over several Wiktionaries is
in progress.

## Released data (`release/`)

| file | content |
|---|---|
| `headwords.txt` | the 63,843 headwords (DEX '98, completed with DEX '96 for G, H and part of I) |
| `arcs_llm.tsv.gz` | the dictionary graph, one arc per line: `defining_word<TAB>defined_headword` (first senses; ambiguous forms resolved by the language model) |
| `arcs_most_frequent.tsv.gz`, `arcs_all_candidates.tsv.gz` | the same graph under the two regimes without a language model |
| `layers_<regime>.tsv` | for every headword: `core`, `satellite` or `outside_kernel`, and whether it belongs to the MinSet found |
| `minset_<regime>.txt` | the smallest grounding set found (for the language-model regime: 6,325 words, completed from the integer program) |
| `reciprocal_pairs_llm.tsv` | the 8,761 pairs of headwords that occur in each other's definitions; `shared_stem` = 1 for derivational pairs |
| `llm_choices.tsv` | the language model's choice for every ambiguous word form: `defined_headword<TAB>word_form<TAB>chosen_headwords` (`-` = none) |
| `results.json` | every number reported in the paper |

Graur's list (Alexandru Graur, *Încercare asupra fondului principal lexical al limbii romîne*, 1954) is protected by
copyright, so our transcription is **not** included; the repository contains only statistics derived from it.

## Using the code

Requirements: Python 3.10+, `numpy`, `scipy` (≥ 1.9, for `milp`), `networkx`, `pandas`; for the documents also
`matplotlib`, `python-docx`, `python-pptx`, LibreOffice and a LaTeX distribution.

### Analyse the released graph, or any other dictionary

`latent_structure.py` is self-contained and works on any list of arcs, so it can be applied to other Romanian
dictionaries (later DEX editions, the DLR) or to other languages:

```bash
python3 latent_structure.py release/arcs_llm.tsv.gz --headwords release/headwords.txt
python3 latent_structure.py my_arcs.tsv --headwords my_headwords.txt --ilp 600 --out layers.tsv --json summary.json
```

The input file has one arc per line, `defining_word<TAB>defined_headword`. The script prints the sizes of the Kernel,
Core and Satellites, the MinSet interval (greedy upper bound, cycle-packing lower bound; `--ilp SECONDS` tightens
both by integer programming) and the number of reciprocal pairs, and can write the layer of every headword.

### Reproduce the paper from the dexonline dump

```bash
wget https://dexonline.ro/static/download/dex-database.sql.gz -P data/
python3 extract.py                                              # dump -> data/*.pkl
python3 kernel.py --sources 1,2 --no-expr --first-sense --ambig freq   # regime: most frequent candidate
python3 kernel.py --sources 1,2 --no-expr --first-sense --ambig all    # regime: all candidates
python3 kernel.py --sources 1,2 --no-expr --first-sense --choices ai/choices_haiku12.json   # regime: language model
python3 exact_minset.py out/graph_src12_freq_noexpr_first_ai.tsv out/kernel_src12_freq_noexpr_first_ai.json \
        --time 300 --budget 3600                                # MinSet bounds by integer programming (about 1 h)
python3 pairs.py out/graph_src12_freq_noexpr_first_ai.tsv out/kernel_src12_freq_noexpr_first_ai.json   # reciprocal pairs
./make_all.sh      # results.json -> figures -> paper, abstract, slides, release/ (needs our Graur transcription, see below)
```

The language model's choices are included (`ai/choices_haiku12.json`), so no API key is needed. To recompute them
(about 20 US dollars):

```bash
export ANTHROPIC_API_KEY=...
python3 disambig.py --sources 1,2 --tag haiku12
```

`graur.py` and the parts of `collect_results.py` that compare with Graur's list need our transcription, which is
not distributed. The paper in the official ConsILR Word format is built by `paper/build_docx.py` from
`paper/paper_template.tex`; it needs the conference template `Instructions for ConsILR-2026.docx`
(from <https://conferences.info.uaic.ro/consilr/2026>) in `paper/template2026/`.

## Repository layout

| path | content |
|---|---|
| `extract.py`, `kernel.py` | reading the dexonline dump; building the graph; Kernel, Core, greedy MinSet |
| `disambig.py`, `llm.py`, `agree.py` | resolution of ambiguous forms with a language model; agreement with a second model |
| `bounds.py`, `exact_minset.py` | MinSet lower bound by cycle packing; bounds by integer programming (HiGHS through SciPy) |
| `latent_structure.py` | stand-alone analysis of any dictionary graph |
| `pairs.py`, `layers.py`, `etym.py`, `graur.py`, `compare_regimes.py` | analyses reported in the paper |
| `collect_results.py`, `make_figures.py`, `release_data.py`, `make_all.sh` | results, figures, released data |
| `paper/`, `abstract/`, `slides/` | the paper (LaTeX source and Word builder), the abstract and the presentation |
| `NOTE_ro.md` | working notes in Romanian |

Comments inside the analysis scripts are in Romanian.

## Licence

GNU General Public License v3.0 (see `LICENSE`), the licence of the dexonline data from which the graph is derived.
The DEX text belongs to its authors (Academia Română, Institutul de Lingvistică „Iorgu Iordan – Al. Rosetti”);
the digitisation is by the dexonline volunteers. The Romanian Swadesh list (`gold/swadesh_ro_raw.json`) comes from
Wiktionary (CC BY-SA).
