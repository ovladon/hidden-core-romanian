#!/usr/bin/env python3
"""Structura latenta a DEX '98 (metoda Vincent-Lamarre, Harnad et al. 2016), la nivel de lemă.

Graful: muchie u -> v daca lema u apare in definitia lui v ("u il defineste pe v").
  Kernel  = ce ramane dupa eliminarea repetata a cuvintelor care nu definesc nimic
  Core    = cea mai mare componenta tare conexa a Kernel-ului
  MinSet  = o multime minima de cuvinte din care se pot defini toate celelalte
            (minimum feedback vertex set; aici aproximare greedy cu reduceri)

Versiunea de fata e pasul 1, fara AI: lematizare prin tabelul de forme flexionare dexonline,
iar la ambiguitate (o forma -> mai multe leme) alegem lema cea mai frecventa. Pasul 2 inlocuieste
alegerea asta cu legarea la sens facuta de model.

  python3 kernel.py [--source 1] [--ambig freq|all]
"""
import argparse, collections, json, re, sys, unicodedata
import pandas as pd
import networkx as nx

LETTERS = "a-zăâîșțáéíóúàèìòù"


def norm(s):
    return (s or "").lower().replace("ş", "ș").replace("ţ", "ț").replace("Ş", "ș").replace("Ţ", "ț")


MODE = {"no_expr": False, "first_sense": False}
ETYM_TAIL = re.compile(r"#|%|@|\+|\bDin\b|\bLat\b|\bCf\b|Et\. nec|Onomat|Formație|Probabil|Contaminare|"
                       r"\bVar\b|\bComp\b|\bPref\b|Refăcut|\bDupă\b|\bCuv\b|\bTc\b|\bSl\b")


def clean(rep):
    """Pastreaza doar textul definitoriu: fara cuvantul-titlu, exemple, abrevieri, etimologie."""
    s = rep or ""
    # etimologia: ultima bucata dupa " - ", daca arata ca o etimologie (Din fr., Lat., @baza@ + suf., %cuvant strain%)
    seps = list(re.finditer(r"\s[-–]\s", s))
    if seps:
        tail = s[seps[-1].end():]
        if ETYM_TAIL.search(tail) and not re.search(r"@\d+\.@", tail):
            s = s[:seps[-1].start()]
    if MODE["first_sense"]:
        m = re.search(r"@2\.@|@B\.@|@II\.@", s)
        if m: s = s[:m.start()]
    if MODE["no_expr"]:
        # in DEX '98: "* " = expresie/locutiune (◊ in tipar), "** " = subsens (♦); taiem expresiile
        s = re.sub(r"(?<!\*)\*(?!\*).*?(?=@\d+\.@|@[A-Z]+\.@|(?<!\*)\*\*(?!\*)|$)", " ", s, flags=re.S)
    s = re.sub(r"\[[^\]]*\]", " ", s)                # note gramaticale / pronuntie
    s = re.sub(r"@[^@]*@", " ", s)                   # bold: titlu, expresii
    s = re.sub(r"\$[^$]*\$", " ", s)                 # italic: exemple, forme
    s = re.sub(r"#[^#]*#", " ", s)                   # abrevieri marcate
    s = re.sub(r"(?<![\wăâîșț])(?:I|II|III|IV)\.(?=\s|$)", " ", s)   # clasa de conjugare: vb. I.
    s = re.sub(r"\s[–-]\s(?:Din|Lat|Cf|Et\. nec|Formație|Comp|Pref|Sl|Tc|Fr|Ngr|Magh|Germ|It|Bg|Rus|Ucr|Engl|Onomat|Contaminare|Probabil|Din lat)\b.*$", " ", s, flags=re.S)
    s = re.sub(r"[◊♦▶►]", " ", s)
    return s


def load_defs(sources=(1, 2)):
    """DEX ed. a II-a asa cum e in dexonline: DEX '98 (sursa 1) completat cu DEX '96 (sursa 2).
    In dump, DEX '98 nu are literele G, H si o parte din I; DEX '96 (aceeasi editie, tiparul din 1996)
    le acopera. Prima sursa are prioritate; urmatoarele adauga doar lemele care lipsesc."""
    D = pd.read_pickle("data/Definition.pkl")
    D = D[D.status == 0]
    parts, seen = [], set()
    for src in sources:
        d = D[D.sourceId == src]
        keys = d.lexicon.map(lambda x: norm(x or "").strip())
        d = d[~keys.isin(seen)]
        seen |= set(keys)
        parts.append(d)
    return pd.concat(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="1,2", help="1 = DEX '98, 2 = DEX '96 (completeaza G-I)")
    ap.add_argument("--ambig", default="freq", choices=("freq", "all"))
    ap.add_argument("--out", default="out")
    ap.add_argument("--no-expr", action="store_true")
    ap.add_argument("--first-sense", action="store_true")
    ap.add_argument("--choices", help="alegerile modelului (ai/choices_*.json); altfel regula frecventei")
    args = ap.parse_args()
    MODE["no_expr"], MODE["first_sense"] = args.no_expr, args.first_sense

    sources = tuple(int(x) for x in args.sources.split(","))
    D = load_defs(sources)
    L = pd.read_pickle("data/Lexeme.pkl")
    F = pd.read_pickle("data/InflectedForm.pkl")
    print(f"definitii (surse {sources}): {len(D)}", flush=True)

    heads = collections.defaultdict(list)            # lema -> texte de definitie
    for lex, rep in zip(D.lexicon, D.internalRep):
        h = norm(lex).strip()
        if h and re.fullmatch(f"[{LETTERS}-]+", h):
            heads[h].append(rep)
    H = set(heads)
    print(f"cuvinte-titlu (leme distincte): {len(H)}")

    lexform = dict(zip(L.id, (norm(x) for x in L.formNoAccent)))
    freq = collections.defaultdict(float)
    for f_, fr in zip(L.formNoAccent, L.frequency):
        freq[norm(f_)] = max(freq[norm(f_)], fr or 0.0)
    form2lem = collections.defaultdict(set)
    for form, lid in zip(F.formNoAccent, F.lexemeId):
        lem = lexform.get(lid)
        if lem in H:
            form2lem[norm(form)].add(lem)
    for h in H:                                      # lema insasi e mereu o forma a ei
        form2lem[h].add(h)

    choices = json.load(open(args.choices, encoding="utf8")) if args.choices else {}
    nai = 0
    tokre = re.compile(f"[{LETTERS}]+(?:-[{LETTERS}]+)*")
    G = nx.DiGraph(); G.add_nodes_from(H)
    ntok = nunk = nambig = 0
    for v, reps in heads.items():
        defn = set()
        for rep in reps:
            for t in tokre.findall(norm(clean(rep))):
                ntok += 1
                c = form2lem.get(t)
                if not c:
                    nunk += 1; continue
                if len(c) > 1:
                    nambig += 1
                    pick = choices.get(f"{v}\t{t}")
                    if pick is not None:
                        nai += 1; c = set(pick)                 # [] = niciuna: tokenul se elimina
                    else:
                        c = c if args.ambig == "all" else {max(c, key=lambda x: (freq[x], x == t))}
                defn |= c
        for u in defn:
            if u != v:
                G.add_edge(u, v)
    print(f"tokeni in definitii: {ntok} | nelematizabili: {nunk/ntok:.1%} | ambigui: {nambig/ntok:.1%}"
          + (f" | rezolvati de model: {nai/max(1,nambig):.1%}" if choices else ""))
    print(f"graf: {G.number_of_nodes()} noduri, {G.number_of_edges()} muchii")

    # --- grafuri ca dict de multimi: networkx e prea lent pentru curatarea MinSet-ului
    out = {n: set(G.successors(n)) for n in G}
    inn = {n: set(G.predecessors(n)) for n in G}

    # Kernel: elimina repetat nodurile fara muchii de iesire (nu definesc nimic)
    alive = set(G); odeg = {n: len(out[n]) for n in G}
    q = collections.deque(n for n in G if odeg[n] == 0)
    while q:
        n = q.popleft()
        if n not in alive: continue
        alive.discard(n)
        for u in inn[n]:
            if u in alive:
                odeg[u] -= 1
                if odeg[u] == 0: q.append(u)
    K = G.subgraph(alive).copy()
    sccs = sorted(nx.strongly_connected_components(K), key=len, reverse=True)
    core = sccs[0] if sccs else set()
    print(f"Kernel: {len(alive)} ({len(alive)/len(H):.1%} din dictionar)", flush=True)
    print(f"Core:   {len(core)} ({len(core)/max(1,len(alive)):.1%} din Kernel) | "
          f"alte componente tari: {len(sccs)-1}", flush=True)

    # MinSet aproximativ: greedy cu reduceri IN0/OUT0, pe fiecare componenta tare
    def greedy_fvs(nodes):
        o = {n: out[n] & nodes for n in nodes}
        i = {n: inn[n] & nodes for n in nodes}
        S = set()
        def drop(n):
            for v in o.pop(n): i[v].discard(n)
            for u in i.pop(n): o[u].discard(n)
        while o:
            changed = True
            while changed:
                rm = [n for n in o if not o[n] or not i[n]]
                changed = bool(rm)
                for n in rm: drop(n)
            if not o: break
            n = max(o, key=lambda x: len(o[x]) * len(i[x]))
            S.add(n); drop(n)
        return S
    fvs = set()
    for comp in sccs:
        if len(comp) > 1:
            fvs |= greedy_fvs(set(comp))
    print(f"MinSet greedy brut: {len(fvs)}", flush=True)

    # curatare: un nod din S e redundant daca, readaugat, nu inchide niciun ciclu
    rest = alive - fvs
    for s in sorted(fvs, key=lambda x: len(out[x] & alive) * len(inn[x] & alive)):
        preds = inn[s] & rest
        if not preds: rest.add(s); fvs.discard(s); continue
        seen, stack, cyc = set(), [v for v in out[s] & rest], False
        while stack and not cyc:
            x = stack.pop()
            if x in seen: continue
            seen.add(x)
            if x in preds: cyc = True; break
            stack.extend(y for y in out[x] if y in rest and y not in seen)
        if not cyc:
            rest.add(s); fvs.discard(s)
    assert nx.is_directed_acyclic_graph(K.subgraph(alive - fvs))
    print(f"MinSet (aprox. greedy, curatat): {len(fvs)} ({len(fvs)/len(H):.2%} din dictionar, "
          f"{len(fvs)/max(1,len(alive)):.1%} din Kernel)", flush=True)

    import os; os.makedirs(args.out, exist_ok=True)
    tag = f"src{''.join(map(str, sources))}_{args.ambig}" + ("_noexpr" if args.no_expr else "") + ("_first" if args.first_sense else "") + ("_ai" if args.choices else "")
    json.dump({"heads": len(H), "kernel": sorted(alive), "core": sorted(core), "minset": sorted(fvs),
               "edges": G.number_of_edges(), "unk_rate": nunk / ntok, "ambig_rate": nambig / ntok,
               "tokens": ntok},
              open(f"{args.out}/kernel_{tag}.json", "w"), ensure_ascii=False)
    nx.write_edgelist(G, f"{args.out}/graph_{tag}.tsv", delimiter="\t", data=False)
    print(f"scris {args.out}/kernel_{tag}.json")


if __name__ == "__main__":
    main()
