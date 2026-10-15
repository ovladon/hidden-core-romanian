# Reproducerea verificării limitelor MinSet

Verificarea a fost deja făcută; rezultatele sunt în `RAPORT_ro.md`. Pachetul permite oricui (de exemplu unui
recenzent) să o refacă independent de codul proiectului, pentru cele 16 grafuri (DEX în două variante, 13
Wiktionary-uri în 12 limbi și WordNet). Pasul 1 durează câteva minute, pasul 2 câteva ore.

## Ce se verifică

Graful unui dicționar are un arc u → v dacă u apare în definiția lui v. MinSet este cardinalul minim al unei mulțimi
de vârfuri S pentru care G − S nu mai are cicluri orientate (minimum feedback vertex set). Problema este NP-dificilă,
de aceea raportăm un interval:

- **limita superioară** este cardinalul unei mulțimi concrete S (fișierul `exact/<cod>.json`, câmpul `minset_best`).
  Este corectă dacă G − S este aciclic.
- **limita inferioară** provine din programul liniar în numere întregi
  min Σ x_v, cu Σ_{v∈c} x_v ≥ 1 pentru fiecare ciclu c din listă, x_v ∈ {0, 1}.
  Lista conține doar o parte din ciclurile grafului (generate iterativ), deci problema este o relaxare a celei complete
  și orice limită inferioară a ei este și limită inferioară pentru MinSet. Este corectă dacă (a) fiecare constrângere
  corespunde unui ciclu real al grafului și (b) optimul programului din `exact/<cod>.lp` este cel puțin valoarea
  raportată. Fișierul `.lp` conține exact modelul pe care solverul a demonstrat limita (primele `lb_cycles` cicluri
  din certificat; ciclurile adăugate după aceea nu au mai ridicat-o).
- **limita fără solver** este puțin mai slabă, dar se verifică doar prin adunări: ciclurile certificatului primesc
  ponderi întregi y_c ≥ 0 (`exact/<cod>_packing.json.gz`). Dacă fiecare vârf se află pe cicluri cu pondere totală cel
  mult M, orice mulțime de feedback S intersectează fiecare ciclu, deci |S| · M ≥ Σ_c y_c și |S| ≥ ⌈Σ_c y_c / M⌉.
  Ponderile provin din relaxarea liniară; `verify.py` recalculează M și limita în aritmetică întreagă exactă.

## Pașii

Este nevoie de Python 3. Pentru pasul 2, și de numpy și scipy (`pip install scipy`).

```bash
tar xzf pachet_verificare_minset.tar.gz
cd pachet_verificare_minset
bash verifica_tot.sh          # pasul 1: G − S aciclic, ciclurile certificatului, limita fără solver
bash verifica_tot.sh 1800     # pasul 1 și pasul 2: rezolvă fiecare .lp (cel mult 30 de minute per graf)
```

Rezultatul așteptat pentru fiecare dicționar:

- pasul 1: `G - S acyclic: True`, `invalid: 0` și `valid weights: True`, cu limita fără solver egală cu cea din
  tabelul de mai jos;
- pasul 2: `OK`. Dacă apare `NOT CONFIRMED`, solverul nu a ajuns în timpul dat la limita raportată; se repetă cu mai
  mult timp (de exemplu `python3 solve_lp.py exact/it 7200`).

Pasul 2 folosește implicit HiGHS din scipy, motorul cu care am obținut limitele. Ramificarea (branch and bound) diferă
între versiunile solverului, așa că o altă versiune poate avea nevoie de mai mult timp pentru aceeași limită: pe modelul
DEX, HiGHS 1.15 (`--highspy`) a ajuns în 30 de minute la 6.193, iar HiGHS din scipy la 6.194 în 15 minute. Fișierele
`.lp` sunt în format CPLEX LP, deci pot fi rezolvate și cu alt solver (Gurobi, CPLEX, `glpsol --lp`). Variabila `x<i>`
corespunde cuvântului de pe linia i + 1 din `exact/<cod>_names.txt`.

`verify.py` (aproximativ 50 de linii) folosește doar biblioteca standard și nu importă nimic din proiect; merită
citit înainte de rulare.

## Conținutul pachetului

| fișier | conținut |
|---|---|
| `graphs/<cod>.tsv.gz` | arcele grafului, câte unul pe linie: cuvântul definitor, tab, cuvântul definit |
| `exact/<cod>.json` | mulțimea S (limita superioară), limita inferioară, numărul de vârfuri aflate pe cicluri |
| `exact/<cod>_cycles.json.gz` | ciclurile folosite în programul relaxat |
| `exact/<cod>.lp.gz` | programul relaxat, în format LP |
| `exact/<cod>_packing.json.gz` | ponderile întregi ale ciclurilor (limita fără solver) |
| `exact/<cod>_names.txt` | corespondența variabilă–cuvânt |

## Rezultatele care trebuie confirmate

| cod | dicționar | cuvinte pe cicluri | limita inferioară (ILP) | limita fără solver | limita superioară | diferență | cicluri în certificat |
|---|---|---|---|---|---|---|---|
| dex_llm | DEX, dezambiguizare LLM (lucrarea ConsILR) | 19,769 | 6,195 | 6,138 | 6,318 | 1.95% | 50,877 |
| wordnet | WordNet (engleză) | 9,541 | 1,609 | 1,589 | 1,703 | 5.52% | 43,955 |
| dex | DEX, aceeași procedură ca Wiktionary | 17,822 | 5,442 | 5,393 | 5,560 | 2.12% | 46,038 |
| ro_wikt | Wiktionary românesc | 14,353 | 4,483 | 4,448 | 4,500 | 0.38% | 27,644 |
| it | Wiktionary italian | 7,162 | 842 | 840 | 887 | 5.07% | 27,288 |
| es | Wiktionary spaniol | 10,534 | 1,216 | 1,210 | 1,336 | 8.98% | 53,208 |
| pt | Wiktionary portughez | 8,579 | 1,563 | 1,551 | 1,576 | 0.82% | 16,546 |
| fr | Wiktionary francez | 13,743 | 2,195 | 2,186 | 2,312 | 5.06% | 33,871 |
| en | Wiktionary englez | 20,547 | 3,778 | 3,767 | 4,138 | 8.70% | 24,304 |
| simple | Simple English Wiktionary | 2,521 | 422 | 418 | 422 | exact | 2,986 |
| de | Wiktionary german | 9,652 | 1,291 | 1,288 | 1,354 | 4.65% | 25,730 |
| nl | Wiktionary olandez | 9,332 | 1,801 | 1,792 | 1,826 | 1.37% | 19,960 |
| pl | Wiktionary polonez | 7,055 | 973 | 972 | 1,005 | 3.18% | 19,878 |
| cs | Wiktionary ceh | 3,425 | 421 | 416 | 421 | exact | 7,104 |
| ru | Wiktionary rus | 17,195 | 2,443 | 2,437 | 2,573 | 5.05% | 40,062 |
| el | Wiktionary grec | 7,440 | 1,289 | 1,284 | 1,311 | 1.68% | 22,495 |

„Diferență” este (limita superioară − limita inferioară) / limita superioară. Calculul s-a oprit la diferență
de 0,2% sau după o oră de rezolvare per graf. Valoarea MinSet/Kernel folosită în comparația dintre limbi este
mijlocul intervalului raportat la mărimea Kernelului; la diferențe de acest ordin, concluziile nu depind de
poziția valorii exacte în interval.
