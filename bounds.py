#!/usr/bin/env python3
"""Limita inferioara pentru MinSet: impachetare greedy de cicluri disjuncte pe noduri.
Orice multime de feedback trebuie sa atinga fiecare ciclu, deci |MinSet| >= numarul de cicluri disjuncte."""
import json, sys, collections, random
from collections import deque

def main(graph, kern):
    k = json.load(open(kern, encoding="utf8")); K = set(k["kernel"])
    out = collections.defaultdict(set)
    for line in open(graph, encoding="utf8"):
        u, v = line.rstrip("\n").split("\t")
        if u in K and v in K: out[u].add(v)
    def pack(seed):
        rnd = random.Random(seed)
        order = sorted(K); rnd.shuffle(order) if seed else None
        alive = set(K); packed = 0; lens = collections.Counter()
        for u in order:                         # 2-cicluri intai (cele mai scurte)
            if u not in alive: continue
            for v in sorted(out[u]):
                if v in alive and v != u and u in out[v]:
                    alive -= {u, v}; packed += 1; lens[2] += 1; break
        changed = True
        while changed:                          # apoi cel mai scurt ciclu prin fiecare nod (BFS)
            changed = False
            for s in sorted(alive, key=lambda x: (len(out[x]), x)):
                if s not in alive: continue
                par = {s: None}; q = deque([s]); hit = None
                while q and hit is None:
                    x = q.popleft()
                    for y in sorted(out[x]):
                        if y not in alive: continue
                        if y == s: hit = x; break
                        if y not in par: par[y] = x; q.append(y)
                if hit is not None:
                    cyc = []; x = hit
                    while x is not None: cyc.append(x); x = par[x]
                    alive -= set(cyc); packed += 1; lens[len(cyc)] += 1; changed = True
        return packed, lens
    # orice impachetare e o limita valida; pastram cea mai buna din cateva ordini (determinist)
    packed, lens = max((pack(sd) for sd in range(6)), key=lambda r: r[0])
    print(f"cicluri disjuncte (limita inferioara MinSet): {packed} | lungimi: {dict(sorted(lens.items())[:6])}")
    print(f"MinSet greedy (limita superioara): {len(k['minset'])}")
    print(f"=> MinSet intre {packed} ({packed/k['heads']:.1%}) si {len(k['minset'])} ({len(k['minset'])/k['heads']:.1%}) din dictionar")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
