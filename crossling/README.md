# Cross-linguistic comparison (work in progress, for the journal version)

The question: is the large grounding kernel of the DEX a property of Romanian, of Romance languages, or of the
Romanian lexicographic tradition? Every dictionary below is processed with **the same procedure**
(`wiktionary_graph.py`; WordNet with `wordnet_graph.py`):

- vertices: single-word lemmas with a noun, verb, adjective, adverb or numeral entry;
- definition: the first sense of each content entry;
- function words ignored (as in Vincent-Lamarre et al. 2016);
- tokens mapped to lemmas with the dictionary's own inflection data;
- two regimes for ambiguous tokens: most frequent candidate (`freq`) and all candidates (`all`);
- Kernel, Core and MinSet bounds (greedy upper bound, cycle-packing lower bound) with `latent_structure.py`.

Controls:
- `dex_to_jsonl.py` runs the DEX itself through the Wiktionary procedure, which reproduces the main results
  (Kernel 32–38%, MinSet 8.6–11.6%);
- `dex_overlap.py` shows that 70% of the first definitions of the Romanian Wiktionary are near-copies of the DEX
  (similarity ≥ 0.8; median 0.95), so the Romanian Wiktionary is not independent evidence.

## Results (`summary.json`, `fig_crossling.png`)

| dictionary | headwords | Kernel (freq–all) | MinSet (freq–all) | MinSet / Kernel | reciprocal pairs per 1,000 |
|---|---|---|---|---|---|
| Romanian DEX | 59,272 | 32.2–38.1% | 8.6–11.6% | 28–29% | 128 |
| Romanian Wiktionary (70% from DEX) | 65,283 | 25.6–29.3% | 6.6–8.1% | 27% | 87 |
| Italian Wiktionary | 56,080 | 14.7–21.7% | 1.3–2.7% | 10–11% | 15 |
| Spanish Wiktionary | 96,018 | 12.0–16.3% | 1.1–2.1% | 11% | 12 |
| Portuguese Wiktionary | 69,586 | 14.5–18.5% | 2.1–2.9% | 15% | 27 |
| French Wiktionary | 250,887 | 6.4–10.5% | 0.8–1.7% | 14% | 10 |
| English WordNet 3.0 | 77,426 | 15.2–18.3% | 2.1–2.8% | 14% | 23 |
| Simple English Wiktionary | 20,638 | 14.4–18.0% | 1.9–3.1% | 14–16% | 26 |
| German Wiktionary | 147,947 | 7.8–10.8% | 0.8–1.4% | 11% | 9 |
| Dutch Wiktionary | 163,329 | 7.5–10.2% | 1.0–1.6% | 14–15% | 14 |
| Polish Wiktionary | 90,717 | 9.3–11.3% | 1.0–1.4% | 11% | 9 |
| Czech Wiktionary | 40,324 | 9.7–12.0% | 0.9–1.5% | 11% | 8 |
| Russian Wiktionary | 395,871 | 5.0–6.4% | 0.6–0.8% | 11–12% | 6 |
| Greek Wiktionary | 90,089 | 10.2–12.7% | 1.3–1.9% | 13–14% | 14 |

The share of the Kernel occupied by the MinSet does not depend on the size of the dictionary. It is 10–16% in
every dictionary except the Romanian ones (27–29%). The density of reciprocally defined pairs is 5–20 times higher in
the DEX than elsewhere. Other Romance languages (Italian, Spanish, Portuguese, French) behave like Germanic and
Slavic ones, so the result is not a Romance property.

## Still to do

- English Wiktionary (download in progress) and tight MinSet bounds by integer programming for every dictionary;
- a second Romanian dictionary independent of the DEX (public-domain dictionaries on dexonline: Șăineanu 1929,
  Candrea 1931, Scriban 1939; full text to be requested from dexonline);
- use the hand-made lemma links of the Romanian Wiktionary (`[[avea|având]]`) as a human gold standard for the
  disambiguation of the DEX definitions that it copies.

Data: Wiktionary extracts from [kaikki.org](https://kaikki.org) (wiktextract, CC BY-SA) and the ro.wiktionary dump
(Wikimedia, CC BY-SA); they are downloaded by `download.sh` and are not part of the repository.
