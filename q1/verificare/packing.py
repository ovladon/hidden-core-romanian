#!/usr/bin/env python3
"""Second lower-bound certificate, checkable without a solver: a fractional packing of the certificate's cycles.

Integer weights y_c >= 0 are given to the cycles. If every vertex lies on cycles of total weight at most M, any
feedback vertex set S meets every cycle, so |S| * M >= sum_{v in S} load(v) >= sum_c y_c, hence |S| >= sum_c y_c / M.
The weights come from the linear relaxation (scipy/HiGHS), scaled to integers; verify.py recomputes M and the bound
with exact integer arithmetic.

  python3 q1/verificare/packing.py q1/exact/<code>        # writes q1/exact/<code>_packing.json.gz
"""
import gzip, json, sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix

SCALE = 10 ** 6


def main(prefix):
    cyc = json.load(gzip.open(prefix + "_cycles.json.gz", "rt", encoding="utf8"))
    names = sorted({v for c in cyc for v in c}); idx = {v: i for i, v in enumerate(names)}
    rows = [idx[v] for c in cyc for v in c]; cols = [j for j, c in enumerate(cyc) for _ in c]
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(names), len(cyc)))
    r = linprog(-np.ones(len(cyc)), A_ub=A, b_ub=np.ones(len(names)), bounds=(0, None), method="highs")
    y = [int(round(max(0.0, v) * SCALE)) for v in r.x]
    load = [0] * len(names)
    for c, w in zip(cyc, y):
        for v in c: load[idx[v]] += w
    M = max(load); lb = -(-sum(y) // M)
    json.dump(y, gzip.open(prefix + "_packing.json.gz", "wt"))
    print(f"{prefix}: packing bound {lb} (linear relaxation {-r.fun:.2f})")


if __name__ == "__main__":
    main(sys.argv[1])
