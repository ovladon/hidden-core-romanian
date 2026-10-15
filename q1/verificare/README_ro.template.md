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

__TABEL__

„Diferență” este (limita superioară − limita inferioară) / limita superioară. Calculul s-a oprit la diferență
de 0,2% sau după o oră de rezolvare per graf. Valoarea MinSet/Kernel folosită în comparația dintre limbi este
mijlocul intervalului raportat la mărimea Kernelului; la diferențe de acest ordin, concluziile nu depind de
poziția valorii exacte în interval.
