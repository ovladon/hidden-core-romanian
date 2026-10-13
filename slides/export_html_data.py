#!/usr/bin/env python3
"""Datele pentru prezentarea HTML interactiva: definitii (primul sens), legaturi, straturi, perechi.
Definitiile provin din DEX ed. a II-a (dexonline, GNU GPL) si se afiseaza cu atribuire."""
import collections, json, random, re, sys
sys.path.insert(0, ".")
import kernel

TAG = "src12_freq_noexpr_first_ai"
kernel.MODE["first_sense"], kernel.MODE["no_expr"] = True, True
D = kernel.load_defs((1, 2))
defs = {}
for lex, rep in zip(D.lexicon, D.internalRep):
    h = kernel.norm(lex).strip()
    t = re.sub(r"\s+", " ", kernel.clean(rep)).strip(" ;,.*") + "."
    t = re.sub(r"\s+([,;.])", r"\1", t)
    t = re.sub(r"\*\*\s*", "♦ ", t)                       # subsens, ca in DEX-ul tiparit
    t = re.sub(r"♦\s*=\s*", "♦ ", t).replace("( )", "").replace("  ", " ")
    if h and h not in defs and len(t) > 3:
        defs[h] = t[:230]
k = json.load(open(f"out/kernel_{TAG}.json", encoding="utf8"))
K, C, M = set(k["kernel"]), set(k["core"]), set(k["minset"])
try:                                        # solutia ILP reparata, daca e mai mica decat cea greedy
    e = json.load(open(f"out/minset_exact_{TAG}.json", encoding="utf8"))["minset_best"]
    if len(e) < len(M): M = set(e)
except FileNotFoundError:
    pass
layer = lambda w: "minset" if w in M else "core" if w in C else "satellite" if w in K else "rest"
out = collections.defaultdict(set); inn = collections.defaultdict(set)
for line in open(f"out/graph_{TAG}.tsv", encoding="utf8"):
    u, v = line.rstrip("\n").split("\t"); out[u].add(v); inn[v].add(u)

seeds = ["copac", "arbore", "câine", "apă", "om", "casă", "frumos", "timp", "cuvânt", "limbă", "mamă", "pâine",
         "dicționar", "definiție", "sens", "gând", "inimă", "lumină", "foc", "drum", "carte", "școală", "iubi", "ști"]
keep, frontier = set(), [s for s in seeds if s in defs]
for depth in range(3):                      # cuvintele din definitiile cuvintelor (pana la 3 pasi)
    nxt = []
    for w in frontier:
        if w in keep: continue
        keep.add(w)
        nxt.extend(sorted(inn[w])[:40])
    frontier = nxt
keep = {w for w in keep if w in defs}
pairs = [l.rstrip("\n").split("\t") for l in open(f"out/pairs_{TAG}.tsv", encoding="utf8")]
random.seed(7)
nice = [p for p in pairs if p[2] == "0" and len(p[0]) > 3 and len(p[1]) > 3 and p[0] in defs and p[1] in defs]
pairsel = random.sample(nice, 160)
for a, b, _ in pairsel: keep |= {a, b}
G = json.load(open("gold/graur1954/graur1954_lemmas.json", encoding="utf8"))
glem = {r["lemma"]: r["cat"] for r in G if r["lemma"]}
gori = {r["lemma"]: r["origin"] for r in G if r["lemma"]}
# exemplele discutate chiar de Graur (1954, Introducere) si cateva perechi instructive
GRAUR_EX = ["doagă", "săgeată", "lumânare", "femeie", "nevastă", "soție", "muiere", "arbore", "copac", "pom", "lemn",
            "cioban", "păcurar", "concert", "axiomă", "produce", "negoț", "comerț", "artă", "vapor", "gură", "sta", "face",
            "leopard", "mamă", "pâine", "vită", "spinare", "spune"]
GRAUR_EX = [w for w in GRAUR_EX if w in defs]
keep |= set(GRAUR_EX)
words = {}
for w in sorted(keep):
    words[w] = {"d": defs[w], "l": layer(w), "n": sorted(x for x in inn[w] if x in defs)[:60], "o": len(out[w])}
    # lista lui Graur e protejata de drepturi de autor: se arata doar pentru cuvintele discutate chiar de el
    if w in GRAUR_EX: words[w].update({"g": glem.get(w, ""), "go": gori.get(w, "")})
data = {"words": words, "pairs": [[a, b] for a, b, _ in pairsel], "graurEx": GRAUR_EX}
json.dump(data, open("slides/html_data.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print(len(words), "cuvinte |", len(data["pairs"]), "perechi")
