# Verificarea limitelor MinSet: raport

MinSet este cardinalul minim al unei mulțimi de cuvinte S pentru care graful dicționarului (arc u → v dacă u apare în
definiția lui v) rămâne fără cicluri după eliminarea lui S. Problema este NP-dificilă, de aceea fiecare valoare este
un interval [limita inferioară, limita superioară], calculat prin programare liniară în numere întregi (HiGHS), cu
generarea treptată a ciclurilor.

Fiecare limită a fost verificată independent de programul care a calculat-o:

- **limita superioară**: mulțimea S raportată a fost eliminată din graf, iar sortarea topologică (algoritmul lui Kahn)
  a parcurs toate vârfurile rămase, deci graful rămas nu are cicluri;
- **limita inferioară, re-rezolvare independentă**: s-a verificat că fiecare constrângere a programului corespunde
  unui ciclu real al grafului, apoi programul a fost rezolvat din nou de la zero (cel mult __SECUNDE__ de minute pe
  graf). Programul conține doar o parte din ciclurile grafului, deci optimul lui este o limită inferioară validă;
- **limita inferioară fără solver**: ciclurile primesc ponderi întregi y ≥ 0 astfel încât fiecare cuvânt se află pe
  cicluri cu pondere totală cel mult M. Orice mulțime care intersectează toate ciclurile are atunci cel puțin
  ⌈Σy / M⌉ cuvinte. Verificarea se reduce la adunări cu numere întregi.

Limita inferioară confirmată este cea mai mare dintre cele două limite stabilite independent.

__TOATE__

__TABEL__

Pentru DEX-ul din lucrarea ConsILR, intervalul publicat a fost 6.193–6.325. Mulțimea de 6.325 de cuvinte analizată în
lucrare rămâne o mulțime de feedback validă, iar limita inferioară confirmată arată cât de aproape este de optim.

Fișierele: `q1/exact/<cod>.json` (mulțimea S și limitele), `<cod>_cycles.json.gz` (ciclurile certificatului),
`<cod>.lp` (programul re-rezolvat), `<cod>_packing.json.gz` (ponderile); scripturile de verificare în
`q1/verificare/` (`verify.py` nu folosește nimic din codul proiectului). Rezultatele în format JSON:
`q1/verificare/verificare.json`.
