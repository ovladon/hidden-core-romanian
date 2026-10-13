# P12 — Nucleul ascuns al limbii române

**ConsILR 2026** (site actual: conferences.info.uaic.ro/consilr/2026). Rezumat 16 oct. (max 300 cuvinte, PDF, engleză
britanică, EasyChair `consilr2026`) · lucrare 30 oct. (6–12 pagini, număr par) · conferință 9–11 dec., Galați + online.

## Livrabile — `LIVRABILE/`

| fișier | ce e |
|---|---|
| `PAPER - The Hidden Core of Romanian.docx/.pdf` | lucrarea, 10 pagini, formatul Word oficial ConsILR-2026 (sursa: `paper/paper_template.tex` → `build_paper.py` + `build_docx.py`) |
| `ABSTRACT - …pdf/.docx`, `ABSTRACT_easychair.txt` | rezumatul de 296 de cuvinte pentru EasyChair |
| `HiddenCore_ConsILR2026.pptx/.pdf` | prezentarea, 14 slide-uri, cu note de vorbitor în română |
| `HiddenCore_ConsILR2026.html` | prezentarea interactivă (un singur fișier, merge offline; ← →, RO/EN) |
| `graur1954_transcriere.txt` | lista lui Graur (1954), transcrisă din carte — doar pentru cercetare |

Totul se regenerează din rezultate cu `./make_all.sh` (fără apeluri API).

## Date

- dexonline (GPL): **DEX ed. a II-a = DEX '98 (sursa 1) completat cu DEX '96 (sursa 2) pentru G, H și o parte din I**,
  care lipsesc din DEX '98 în dump. 65.452 definiții, 63.843 cuvinte-titlu. Câteva intrări lipsesc (ex. *umbră*, *ager*).
- Graur 1954, pp. 48–55: 1.419 intrări transcrise; validare: total exact, pondere slavă 21,49% exactă; cercurile
  966/216/237 față de 964/217/238 publicate (2 cruci nesigure).
- Swadesh (Wiktionary, CC BY-SA): 175 de cuvinte-titlu.

## Pași (în ordine)

    python3 extract.py                                    # dump -> data/*.pkl
    python3 kernel.py --no-expr --first-sense --ambig freq|all
    export ANTHROPIC_API_KEY=...   # cheia nu se scrie in fisiere
    python3 disambig.py --sources 1,2 --reuse ai/choices_haiku.json --tag haiku12   # Haiku, refolosește alegerile vechi
    python3 kernel.py --no-expr --first-sense --choices ai/choices_haiku12.json
    python3 exact_minset.py out/graph_<tag>.tsv out/kernel_<tag>.json              # ILP, limită inferioară exactă
    python3 graur.py out/kernel_<tag>.json; python3 pairs.py …; python3 layers.py …; python3 etym.py …
    ./make_all.sh                                         # results.json -> figuri -> lucrare -> abstract -> prezentări

## Capcane deja plătite

1. **DEX '98 din dump nu are G, H, o parte din I** → completat cu DEX '96 (aceeași ediție).
2. **Lema „a” lipsește**; modelul are voie să răspundă „niciuna”.
3. **Cifra romană a conjugării** („vb. I.”) devenea cuvântul *i*.
4. **Parserul răspunsurilor** pierdea fiecare a doua linie (`\s` înghițea newline-ul).
5. **Expresiile cu aldine** („* Compuse: @…@ = …”) nu erau tăiate → 9% text în plus; reparat.
6. **Etimologia** scăpa filtrului când abrevierea era marcată (#Cf.#) → tăiere robustă pe ultima bucată după „ - ”.
7. **Cheia Anthropic**: trebuie creată *în* workspace (altfel cere antetul `anthropic-workspace-id`).
8. **Validarea**: pilotul alfabetic dădea 89,7%; eșantionul aleator dă **86,9%** — se raportează cel aleator.
9. `pkill -f exact_minset` omoară și shell-ul propriu (textul comenzii conține tiparul); folosește `ps | grep "[e]xact…"`.
