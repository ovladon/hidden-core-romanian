#!/usr/bin/env python3
"""Latent structure of any dictionary graph: Kernel, Core, Satellites and bounds on the MinSet.

Input is a list of arcs (plain or .gz), one per line, "definer<TAB>defined": the word on the left occurs in the
definition of the headword on the right (the format of out/graph_*.tsv in this repository).
Self-loops are ignored. Optionally, --headwords gives the full list of headwords (one per line), so
that percentages are computed over the whole dictionary and not only over the words that occur in arcs.

Definitions follow Vincent-Lamarre et al. (2016), "The Latent Structure of Dictionaries":
  Kernel     what remains after repeatedly deleting words that occur in no remaining definition
  Core       the largest strongly connected component of the Kernel
  Satellites the other strongly connected components of the Kernel
  MinSet     a minimum feedback vertex set (NP-hard); reported as an interval [lower, upper]:
             upper = greedy feedback vertex set with redundant vertices removed,
             lower = packing of vertex-disjoint cycles, or, with --ilp, an integer program
             with lazily generated cycle constraints (HiGHS through SciPy).

Examples:
  python3 latent_structure.py out/graph_src12_freq_noexpr_first_ai.tsv
  python3 latent_structure.py my_arcs.tsv --headwords my_headwords.txt --ilp 600 --out layers.tsv --json summary.json
"""
import argparse, collections, gzip, json, sys, time


def load(path):
    out, inn = collections.defaultdict(set), collections.defaultdict(set)
    opener = gzip.open if path.endswith(".gz") else open
    for line in opener(path, "rt", encoding="utf8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 2 or parts[0] == parts[1] or parts[:2] == ["defining_word", "defined_headword"]: continue
        u, v = parts[0], parts[1]
        out[u].add(v); inn[v].add(u); out[v]; inn[u]
    return dict(out), dict(inn)


def kernel(out, inn):
    """Repeatedly delete vertices with no outgoing arc (words that define nothing that remains)."""
    alive, odeg = set(out), {n: len(out[n]) for n in out}
    q = collections.deque(n for n in out if odeg[n] == 0)
    while q:
        n = q.popleft()
        if n not in alive: continue
        alive.discard(n)
        for u in inn[n]:
            if u in alive:
                odeg[u] -= 1
                if odeg[u] == 0: q.append(u)
    return alive


def sccs(nodes, out):
    """Strongly connected components (iterative Tarjan), restricted to `nodes`."""
    index, low, on, stack, comps, k = {}, {}, set(), [], [], 0
    for root in nodes:
        if root in index: continue
        work = [(root, iter(sorted(out[root] & nodes)))]
        index[root] = low[root] = k; k += 1; stack.append(root); on.add(root)
        while work:
            v, it = work[-1]
            for w in it:
                if w not in index:
                    index[w] = low[w] = k; k += 1; stack.append(w); on.add(w)
                    work.append((w, iter(sorted(out[w] & nodes)))); break
                if w in on: low[v] = min(low[v], index[w])
            else:
                work.pop()
                if work: low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == index[v]:
                    comp = set()
                    while True:
                        w = stack.pop(); on.discard(w); comp.add(w)
                        if w == v: break
                    comps.append(comp)
    return sorted(comps, key=len, reverse=True)


def is_feedback(S, nodes, out):
    rest = nodes - S
    return all(len(c) == 1 for c in sccs(rest, {n: out[n] & rest for n in rest}))


def prune(S, nodes, out, inn):
    """Drop every vertex of S whose return to the graph closes no cycle."""
    S = set(S)
    for v in sorted(S, key=lambda x: (len(out[x] & nodes) * len(inn[x] & nodes), x)):
        T = S - {v}
        preds = (inn[v] & nodes) - T
        if not preds: S = T; continue
        seen, stack, cyc = set(), [w for w in out[v] & nodes if w not in T], False
        while stack and not cyc:
            x = stack.pop()
            if x in seen: continue
            seen.add(x)
            if x in preds or x == v: cyc = True; break
            stack.extend(y for y in out[x] & nodes if y not in T and y not in seen)
        if not cyc: S = T
    return S


def greedy_fvs(nodes, out, inn):
    """Delete vertices without in- or out-arcs (they lie on no cycle); add the vertex with the largest
    in-degree x out-degree to the set; repeat until no cycle is left. Then remove redundant vertices."""
    S = set()
    for comp in sccs(nodes, out):
        if len(comp) == 1: continue
        o = {n: out[n] & comp for n in comp}; i = {n: inn[n] & comp for n in comp}
        def drop(n):
            for v in o.pop(n): i[v].discard(n)
            for u in i.pop(n): o[u].discard(n)
        while o:
            rm = [n for n in o if not o[n] or not i[n]]
            while rm:
                for n in rm: drop(n)
                rm = [n for n in o if not o[n] or not i[n]]
            if not o: break
            n = max(o, key=lambda x: (len(o[x]) * len(i[x]), x)); S.add(n); drop(n)
    return prune(S, nodes, out, inn)


def shortest_cycle(s, out, alive):
    par, q = {s: None}, collections.deque([s])
    while q:
        x = q.popleft()
        for y in sorted(out[x] & alive):
            if y == s:
                cyc = []
                while x is not None: cyc.append(x); x = par[x]
                return cyc
            if y not in par: par[y] = x; q.append(y)
    return None


def cycle_packing(nodes, out):
    """Vertex-disjoint cycles, shortest first; their number is a lower bound on the MinSet."""
    alive, lens = set(nodes), collections.Counter()
    for u in sorted(nodes):
        if u not in alive: continue
        for v in sorted(out[u] & alive):
            if u in out[v]: alive -= {u, v}; lens[2] += 1; break
    changed = True
    while changed:
        changed = False
        for s in sorted(alive, key=lambda x: (len(out[x] & alive), x)):
            if s not in alive: continue
            c = shortest_cycle(s, out, alive)
            if c: alive -= set(c); lens[len(c)] += 1; changed = True
    return sum(lens.values()), dict(sorted(lens.items()))


def ilp_bounds(nodes, out, inn, budget, per_solve=300):
    """Integer program min sum x_v s.t. each known cycle is hit; cycles are added while the solution leaves
    some unbroken. Each solve gives a valid lower bound; each solution, repaired greedily, an upper bound."""
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import lil_matrix
    names = sorted(n for c in sccs(nodes, out) if len(c) > 1 for n in c)
    idx, V = {n: i for i, n in enumerate(names)}, set(names)
    cycles = [[u, v] for u in names for v in out[u] & V if u < v and u in out[v]]
    lb, best, t0 = 0, None, time.time()
    while time.time() - t0 < budget:
        A = lil_matrix((len(cycles), len(names)))
        for r, c in enumerate(cycles):
            for v in c: A[r, idx[v]] = 1
        res = milp(c=np.ones(len(names)), constraints=LinearConstraint(A.tocsr(), lb=1, ub=np.inf),
                   integrality=np.ones(len(names)), bounds=Bounds(0, 1),
                   options={"time_limit": min(per_solve, max(1, budget - (time.time() - t0)))})
        if res.x is None: break
        S = {names[i] for i in np.flatnonzero(res.x > 0.5)}
        lb = max(lb, int(np.ceil((getattr(res, "mip_dual_bound", None) or res.fun) - 1e-6)))
        rest = V - S
        left = [c for c in sccs(rest, {n: out[n] & rest for n in rest}) if len(c) > 1]
        R = S | greedy_fvs(set().union(*left), out, inn) if left else S
        R = prune(R, V, out, inn)
        if best is None or len(R) < len(best): best = R
        print(f"  ILP: lower {lb} | upper {len(best)} | cycles {len(cycles)} | {time.time() - t0:.0f}s", file=sys.stderr)
        if not left or len(best) == lb: break
        alive = set().union(*left)
        new = []
        for s in sorted(alive, key=lambda x: (len(out[x] & alive), x)):
            c = shortest_cycle(s, out, alive)
            if c and frozenset(c) not in {frozenset(x) for x in new[-50:]}: new.append(c)
            if len(new) >= 4000: break
        cycles += new
    return lb, best


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arcs", help="TSV file: definer<TAB>defined")
    ap.add_argument("--headwords", help="optional file with all headwords, one per line")
    ap.add_argument("--ilp", type=float, default=0, metavar="SECONDS", help="tighten the MinSet bounds by integer programming")
    ap.add_argument("--out", help="write the layer of every headword (TSV: word, layer, in_minset)")
    ap.add_argument("--json", help="write a summary with all sets as JSON")
    a = ap.parse_args()
    out, inn = load(a.arcs)
    H = set(out)
    if a.headwords:
        H |= {l.strip() for l in open(a.headwords, encoding="utf8") if l.strip()}
    K = kernel(out, inn)
    comps = sccs(K, out)
    core = comps[0] if comps else set()
    M = greedy_fvs(K, out, inn)
    assert is_feedback(M, K, out)
    lb, lens = cycle_packing(K, out)
    if a.ilp:
        lb2, M2 = ilp_bounds(K, out, inn, a.ilp)
        lb = max(lb, lb2)
        if M2 is not None and len(M2) < len(M) and is_feedback(M2, K, out): M = M2
    pairs = sorted({tuple(sorted((u, v))) for u in out for v in out[u] if u in out[v]})
    N = len(H); pc = lambda x: f"{100 * x / N:.1f}%"
    print(f"headwords: {N} | arcs: {sum(len(v) for v in out.values())}")
    print(f"Kernel:     {len(K)} ({pc(len(K))})")
    print(f"Core:       {len(core)} ({pc(len(core))}) | Satellites: {len(K) - len(core)} in {len(comps) - 1} components")
    print(f"MinSet:     between {lb} ({pc(lb)}) and {len(M)} ({pc(len(M))})")
    print(f"reciprocal pairs: {len(pairs)} | disjoint cycles by length: {lens}")
    layer = lambda w: "core" if w in core else "satellite" if w in K else "outside_kernel"
    if a.out:
        with open(a.out, "w", encoding="utf8") as f:
            f.write("word\tlayer\tin_minset\n")
            for w in sorted(H): f.write(f"{w}\t{layer(w)}\t{int(w in M)}\n")
    if a.json:
        json.dump({"headwords": N, "kernel": sorted(K), "core": sorted(core), "minset_upper_bound_set": sorted(M),
                   "minset_lower_bound": lb, "minset_upper_bound": len(M), "reciprocal_pairs": pairs},
                  open(a.json, "w", encoding="utf8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
