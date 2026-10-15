# Verificarea limitelor MinSet: raport

MinSet este cardinalul minim al unei mulțimi de cuvinte S pentru care graful dicționarului (arc u → v dacă u apare în
definiția lui v) rămâne fără cicluri după eliminarea lui S. Problema este NP-dificilă, de aceea fiecare valoare este
un interval [limita inferioară, limita superioară], calculat prin programare liniară în numere întregi (HiGHS), cu
generarea treptată a ciclurilor.

Fiecare limită a fost verificată independent de programul care a calculat-o:

- **limita superioară**: mulțimea S raportată a fost eliminată din graf, iar sortarea topologică (algoritmul lui Kahn)
  a parcurs toate vârfurile rămase, deci graful rămas nu are cicluri;
- **limita inferioară, re-rezolvare independentă**: s-a verificat că fiecare constrângere a programului corespunde
  unui ciclu real al grafului, apoi programul a fost rezolvat din nou de la zero (cel mult 30 de minute pe
  graf). Programul conține doar o parte din ciclurile grafului, deci optimul lui este o limită inferioară validă;
- **limita inferioară fără solver**: ciclurile primesc ponderi întregi y ≥ 0 astfel încât fiecare cuvânt se află pe
  cicluri cu pondere totală cel mult M. Orice mulțime care intersectează toate ciclurile are atunci cel puțin
  ⌈Σy / M⌉ cuvinte. Verificarea se reduce la adunări cu numere întregi.

Limita inferioară confirmată este cea mai mare dintre cele două limite stabilite independent.

Toate verificările au trecut.

| graf | limita superioară | limita inferioară (rularea) | re-rezolvare independentă | fără solver | **limita inferioară confirmată** | diferență | verificări |
|---|---|---|---|---|---|---|---|
| DEX, dezambiguizare LLM (lucrarea ConsILR) | 6,318 | 6,195 | 6,195 | 6,138 | **6,195** | 1.95% | da |
| WordNet (engleză) | 1,703 | 1,609 | 1,609 | 1,589 | **1,609** | 5.52% | da |
| DEX, aceeași procedură ca Wiktionary | 5,560 | 5,442 | 5,442 | 5,393 | **5,442** | 2.12% | da |
| Wiktionary românesc | 4,500 | 4,483 | 4,482 | 4,448 | **4,482** | 0.40% | da |
| Wiktionary italian | 887 | 842 | 842 | 840 | **842** | 5.07% | da |
| Wiktionary spaniol | 1,336 | 1,216 | 1,216 | 1,210 | **1,216** | 8.98% | da |
| Wiktionary portughez | 1,576 | 1,563 | 1,563 | 1,551 | **1,563** | 0.82% | da |
| Wiktionary francez | 2,312 | 2,195 | 2,194 | 2,186 | **2,194** | 5.10% | da |
| Wiktionary englez | 4,138 | 3,778 | 3,778 | 3,767 | **3,778** | 8.70% | da |
| Simple English Wiktionary | 422 | 422 | 422 | 418 | **422** | exact | da |
| Wiktionary german | 1,354 | 1,291 | 1,291 | 1,288 | **1,291** | 4.65% | da |
| Wiktionary olandez | 1,826 | 1,801 | 1,801 | 1,792 | **1,801** | 1.37% | da |
| Wiktionary polonez | 1,005 | 973 | 973 | 972 | **973** | 3.18% | da |
| Wiktionary ceh | 421 | 421 | 421 | 416 | **421** | exact | da |
| Wiktionary rus | 2,573 | 2,443 | 2,443 | 2,437 | **2,443** | 5.05% | da |
| Wiktionary grec | 1,311 | 1,289 | 1,289 | 1,284 | **1,289** | 1.68% | da |

Pentru DEX-ul din lucrarea ConsILR, intervalul publicat a fost 6.193–6.325. Mulțimea de 6.325 de cuvinte analizată în
lucrare rămâne o mulțime de feedback validă, iar limita inferioară confirmată arată cât de aproape este de optim.

Fișierele: `q1/exact/<cod>.json` (mulțimea S și limitele), `<cod>_cycles.json.gz` (ciclurile certificatului),
`<cod>.lp` (programul re-rezolvat), `<cod>_packing.json.gz` (ponderile); scripturile de verificare în
`q1/verificare/` (`verify.py` nu folosește nimic din codul proiectului). Rezultatele în format JSON:
`q1/verificare/verificare.json`.
