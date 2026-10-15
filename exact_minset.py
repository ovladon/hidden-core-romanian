#!/usr/bin/env python3
"""MinSet exact (minimum feedback vertex set) pe Kernel, prin programare liniara in numere intregi.

Formulare: x_v = 1 daca v e in MinSet; pentru fiecare ciclu c: sum_{v in c} x_v >= 1; minimizam sum x_v.
Ciclurile sunt prea multe ca sa le scriem pe toate, asa ca le generam pe parcurs: rezolvam cu
ciclurile cunoscute (initial toate 2-ciclurile), verificam daca graful ramas e aciclic, iar daca nu,
adaugam cicluri noi si rezolvam din nou. Optimul fiecarei iteratii e o limita inferioara valida;
cand solutia lasa graful aciclic, ea este optimul exact.

Reduceri inainte (pastreaza optimul): se lucreaza doar pe componentele tari netriviale.

  python3 exact_minset.py out/graph_<tag>.tsv out/kernel_<tag>.json [--time 600]
  ... --resume q1/exact/it          # porneste de la ciclurile si solutia unei rulari anterioare (cu --certificate)
  ... --start-set <fisier.json>     # o multime de feedback cunoscuta (cheia minset_best), folosita daca e valida
"""
import argparse, collections, json, sys, time
import numpy as np
import networkx as nx
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix


def shortest_cycles(out, alive, limit=4000):
    """Cel mai scurt ciclu prin fiecare nod viu (BFS), pana la `limit` cicluri distincte."""
    found, seen = [], set()
    for s in sorted(alive, key=lambda x: (len(out[x] & alive), x)):
        par = {s: None}; q = collections.deque([s]); hit = None
        while q and hit is None:
            x = q.popleft()
            for y in out[x]:
                if y not in alive: continue
                if y == s: hit = x; break
                if y not in par: par[y] = x; q.append(y)
        if hit is not None:
            cyc = []; x = hit
            while x is not None: cyc.append(x); x = par[x]
            key = frozenset(cyc)
            if key not in seen:
                seen.add(key); found.append(cyc)
                if len(found) >= limit: break
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("graph"); ap.add_argument("kernel")
    ap.add_argument("--time", type=float, default=900, help="secunde per rezolvare")
    ap.add_argument("--iters", type=int, default=60)
    ap.add_argument("--budget", type=float, default=3600, help="secunde in total; apoi ne oprim cu limitele obtinute")
    ap.add_argument("--gap", type=float, default=0.002, help="oprire cand (UB-LB)/UB scade sub acest prag")
    ap.add_argument("--out", help="prefixul fisierelor de iesire (implicit out/minset_exact_<tag>)")
    ap.add_argument("--certificate", action="store_true",
                    help="scrie si certificatul: ciclurile folosite si problema relaxata in format .lp (pentru verificare)")
    ap.add_argument("--resume", help="prefixul unei rulari anterioare: ciclurile ei si limitele ei sunt punctul de plecare")
    ap.add_argument("--start-set", action="append", default=[], help="json cu o multime de feedback cunoscuta (minset_best)")
    args = ap.parse_args()
    k = json.load(open(args.kernel, encoding="utf8")); K = set(k["kernel"])
    G = nx.DiGraph()
    for line in open(args.graph, encoding="utf8"):
        u, v = line.rstrip("\n").split("\t")
        if u in K and v in K: G.add_edge(u, v)
    nodes = set().union(*[c for c in nx.strongly_connected_components(G) if len(c) > 1])
    G = G.subgraph(nodes).copy()
    out = {n: set(G.successors(n)) for n in G}
    idx = {n: i for i, n in enumerate(sorted(G))}; names = sorted(G)
    print(f"noduri pe cicluri: {len(nodes)} | muchii: {G.number_of_edges()}", flush=True)

    def repair(S):
        """Completeaza S pana devine multime de feedback (greedy pe ce ramane), apoi scoate nodurile redundante."""
        S = set(S)
        while True:
            rest = G.subgraph(set(names) - S)
            comps = [c for c in nx.strongly_connected_components(rest) if len(c) > 1]
            if not comps: break
            for c in comps:
                sub = rest.subgraph(c)
                S.add(max(sub, key=lambda x: sub.in_degree(x) * sub.out_degree(x)))
        for v in sorted(S, key=lambda x: (G.in_degree(x) * G.out_degree(x), x)):
            T = S - {v}
            preds = set(G.predecessors(v)) - T
            if not preds: S = T; continue
            seen, stack, cyc = set(), [w for w in G.successors(v) if w not in T], False
            while stack and not cyc:
                x = stack.pop()
                if x in seen: continue
                seen.add(x)
                if x in preds or x == v: cyc = True; break
                stack.extend(y for y in G.successors(x) if y not in T and y not in seen)
            if not cyc: S = T
        return S

    cycles = [[u, v] for u in G for v in out[u] if u < v and u in out[v]]
    best_ub, best_set, t_start = None, None, time.time()
    print(f"2-cicluri: {len(cycles)}", flush=True)
    best_lb, sol = 0, None
    starts = list(args.start_set) + ([args.resume + ".json"] if args.resume else [])
    if args.resume:
        import gzip
        is_cyc = lambda c: len(set(c)) == len(c) and all(v in out for v in c) and (
            all(c[(i + 1) % len(c)] in out[c[i]] for i in range(len(c))) or
            all(c[i] in out[c[(i + 1) % len(c)]] for i in range(len(c))))
        have = {frozenset(c) for c in cycles}
        old = json.load(gzip.open(args.resume + "_cycles.json.gz", "rt", encoding="utf8"))
        valid = [c for c in old if is_cyc(c)]
        for c in valid:
            if frozenset(c) not in have: have.add(frozenset(c)); cycles.append(c)
        prev = json.load(open(args.resume + ".json", encoding="utf8"))
        if prev.get("vertices_on_cycles") == len(names) and len(valid) == len(old):
            best_lb = prev["lower_bound"]      # acelasi graf si toate ciclurile anterioare: limita ramane valida
        print(f"reluare din {args.resume}: {len(cycles)} cicluri, limita inferioara {best_lb}", flush=True)
    for p in starts:
        S0 = set(json.load(open(p, encoding="utf8"))["minset_best"]) & set(names)
        if nx.is_directed_acyclic_graph(G.subgraph(set(names) - S0)) and (best_ub is None or len(S0) < best_ub):
            best_ub, best_set = len(S0), S0
            print(f"multime de pornire din {p}: {len(S0)} (valida)", flush=True)
    for it in range(1, args.iters + 1):
        A = lil_matrix((len(cycles), len(names)))
        for r, cyc in enumerate(cycles):
            for v in cyc: A[r, idx[v]] = 1
        t0 = time.time()
        res = milp(c=np.ones(len(names)), constraints=LinearConstraint(A.tocsr(), lb=1, ub=np.inf),
                   integrality=np.ones(len(names)), bounds=Bounds(0, 1),
                   options={"time_limit": args.time, "disp": False})
        if res.x is None:
            print("solverul nu a gasit solutie", res.message); break
        S = {names[i] for i in np.flatnonzero(res.x > 0.5)}
        lb = getattr(res, "mip_dual_bound", None) or res.fun
        best_lb = max(best_lb, int(np.ceil(lb - 1e-6)))
        rest = set(names) - S
        acyclic = nx.is_directed_acyclic_graph(G.subgraph(rest))
        R_ = S if acyclic else repair(S)
        if best_ub is None or len(R_) < best_ub: best_ub, best_set = len(R_), R_
        print(f"iter {it}: |S|={len(S)} | limita inferioara={best_lb} | limita superioara (reparata)={best_ub} | "
              f"cicluri={len(cycles)} | aciclic={acyclic} | {time.time()-t0:.0f}s | {res.message[:40]}", flush=True)
        if best_ub - best_lb <= args.gap * best_ub or time.time() - t_start > args.budget:
            sol = best_set
            print(f"OPRIRE: limite {best_lb}–{best_ub} (diferenta {100*(best_ub-best_lb)/best_ub:.2f}%)", flush=True)
            break
        if acyclic:
            sol = S
            if res.status == 0:
                print(f"OPTIM EXACT: MinSet = {len(S)}"); break
            print(f"solutie fezabila {len(S)} (optimalitate nedemonstrata in limita de timp)"); break
        alive = set()
        for c in nx.strongly_connected_components(G.subgraph(rest)):
            if len(c) > 1: alive |= c
        new = shortest_cycles(out, alive)
        cycles.extend(new)
    if sol is not None:
        prefix = args.out or "out/minset_exact_" + args.kernel.split("kernel_")[-1].replace(".json", "")
        json.dump({"minset_best": sorted(sol), "upper_bound": len(sol), "lower_bound": best_lb,
                   "exact": len(sol) == best_lb, "vertices_on_cycles": len(names), "cycles_used": len(cycles)},
                  open(prefix + ".json", "w", encoding="utf8"), ensure_ascii=False)
        print(f"scris {prefix}.json")
        if args.certificate:
            # limita inferioara: optimul problemei cu aceste cicluri (o relaxare a problemei complete) e >= lower_bound
            import gzip
            json.dump(cycles, gzip.open(prefix + "_cycles.json.gz", "wt", encoding="utf8"), ensure_ascii=False)
            with open(prefix + ".lp", "w", encoding="utf8") as f:
                f.write("\\ min sum x_v  s.t.  sum_{v in c} x_v >= 1 for every listed cycle c;  x binary\n")
                f.write("\\ variable x<i> = word number i in " + prefix + "_names.txt\n")
                f.write("Minimize\n obj: " + " + ".join(f"x{i}" for i in range(len(names))) + "\nSubject To\n")
                for r, cyc in enumerate(cycles):
                    f.write(f" c{r}: " + " + ".join(f"x{idx[v]}" for v in cyc) + " >= 1\n")
                f.write("Binary\n " + " ".join(f"x{i}" for i in range(len(names))) + "\nEnd\n")
            open(prefix + "_names.txt", "w", encoding="utf8").write("\n".join(names) + "\n")
            print(f"certificat: {prefix}.lp, {prefix}_cycles.json.gz, {prefix}_names.txt")


if __name__ == "__main__":
    main()
