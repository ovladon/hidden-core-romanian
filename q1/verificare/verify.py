#!/usr/bin/env python3
"""Independent check of the MinSet bounds (does not use any code of the project).

For one dictionary:
  upper bound   the reported grounding set S is a feedback vertex set: after removing S, the graph has no directed
                cycle (Kahn's topological sort removes every vertex).
  lower bound   every constraint of the certificate is a real directed cycle of the graph; then the optimum of the
                integer program in <prefix>.lp (minimum number of vertices meeting all listed cycles) is a valid lower
                bound for the MinSet, because the full problem has these constraints and more. Solve the .lp with any
                MIP solver (e.g. `highs <prefix>.lp`, `glpsol --lp <prefix>.lp`, Gurobi, CPLEX) and compare with
                lower_bound in <prefix>.json.
  packing       optional, without a solver: integer weights on the certificate's cycles (<prefix>_packing.json.gz);
                if every vertex carries total weight at most M, every feedback vertex set has at least sum / M
                vertices (exact integer arithmetic).

  python3 verify.py <graph.tsv> <prefix>        e.g. python3 verify.py ../../crossling/graphs/it_freq.tsv ../exact/it
"""
import collections, gzip, json, sys


def main(graph, prefix):
    out = collections.defaultdict(set)
    for line in open(graph, encoding="utf8"):
        u, v = line.rstrip("\n").split("\t")[:2]
        if u != v: out[u].add(v); out[v]
    res = json.load(open(prefix + ".json", encoding="utf8"))
    S = set(res["minset_best"])
    # 1. G - S aciclic (Kahn)
    nodes = set(out) - S
    indeg = {n: 0 for n in nodes}
    for u in nodes:
        for v in out[u]:
            if v in nodes: indeg[v] += 1
    q = collections.deque(n for n, d in indeg.items() if d == 0); seen = 0
    while q:
        u = q.popleft(); seen += 1
        for v in out[u]:
            if v in nodes:
                indeg[v] -= 1
                if indeg[v] == 0: q.append(v)
    acyclic = seen == len(nodes)
    # 2. fiecare constrangere a certificatului e un ciclu real
    cycles = json.load(gzip.open(prefix + "_cycles.json.gz", "rt", encoding="utf8"))
    def is_cycle(c):
        fwd = all(c[i + 1] in out[c[i]] for i in range(len(c) - 1)) and c[0] in out[c[-1]]
        bwd = all(c[i] in out[c[i + 1]] for i in range(len(c) - 1)) and c[-1] in out[c[0]]
        return len(set(c)) == len(c) and (fwd or bwd)
    bad = sum(1 for c in cycles if not is_cycle(c))
    print(f"{prefix}: |S| = {len(S)} (upper bound {res['upper_bound']}) -> G - S acyclic: {acyclic}")
    print(f"   certificate: {len(cycles)} cycles, invalid: {bad}; reported lower bound {res['lower_bound']} "
          f"(solve {prefix}.lp to confirm that its optimum is >= this value)")
    # 3. limita din impachetarea fractionara (fara solver): ponderi intregi y_c >= 0 pe cicluri; daca fiecare varf are
    #    incarcarea cel mult M, orice multime de feedback are cel putin sum(y) / M varfuri
    try:
        y = json.load(gzip.open(prefix + "_packing.json.gz", "rt"))
    except FileNotFoundError:
        y = None
    if y is not None:
        ok = len(y) == len(cycles) and all(isinstance(w, int) and w >= 0 for w in y)
        load = collections.Counter()
        for c, w in zip(cycles, y):
            for v in c: load[v] += w
        M = max(load.values()) if load else 1
        lb = -(-sum(y) // M) if ok else 0
        print(f"   packing: valid weights: {ok}; lower bound without a solver: {lb} "
              f"({'within' if lb <= len(S) else 'ABOVE'} the upper bound)")
        ok_pack = ok and lb <= len(S)
    else:
        ok_pack = True
    return acyclic and bad == 0 and ok_pack


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1], sys.argv[2]) else 1)
