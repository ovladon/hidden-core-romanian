#!/usr/bin/env python3
"""Solves the relaxed problem of a certificate (<prefix>.lp) with HiGHS and compares its lower bound with the one we
report in <prefix>.json.

The solver's dual bound (or the optimum, if it finishes) is a valid lower bound for the MinSet of the whole graph,
because the .lp contains only some of the cycle constraints of the full problem. The check passes if this bound is at
least the reported lower_bound. Branch and bound is not reproducible across solver versions within a time limit, so a
bound slightly below the reported one means "not confirmed in this time", not "wrong".

Two engines: scipy.optimize.milp (default; the HiGHS version bundled with scipy, which produced our bounds) or highspy
(`--highspy`, `pip install highspy`). Any other MIP solver that reads the CPLEX LP format can be used instead.

  python3 solve_lp.py <prefix> [seconds] [--highspy]        e.g. python3 solve_lp.py exact/it 1800
"""
import json, re, sys


def solve_scipy(path, seconds):
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import csr_matrix
    rows, cols, nvar, r = [], [], 0, 0
    for line in open(path, encoding="utf8"):
        if line.startswith(" obj:"):
            nvar = len(re.findall(r"x\d+", line))
        elif re.match(r"\s*c\d+:", line):
            for v in re.findall(r"x(\d+)", line.split(":", 1)[1]):
                rows.append(r); cols.append(int(v))
            r += 1
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(r, nvar))
    res = milp(c=np.ones(nvar), constraints=LinearConstraint(A, lb=1, ub=np.inf), integrality=np.ones(nvar),
               bounds=Bounds(0, 1), options={"time_limit": seconds, "disp": False})
    dual = getattr(res, "mip_dual_bound", None)
    if dual is None: dual = res.fun
    return res.message[:40], dual, res.fun


def solve_highspy(path, seconds):
    import highspy
    h = highspy.Highs(); h.setOptionValue("output_flag", False); h.setOptionValue("time_limit", float(seconds))
    h.readModel(path); h.run(); info = h.getInfo()
    return h.modelStatusToString(h.getModelStatus()), info.mip_dual_bound, info.objective_function_value


def main(prefix, seconds=1800.0, engine="scipy"):
    rep = json.load(open(prefix + ".json", encoding="utf8"))["lower_bound"]
    status, dual, primal = (solve_highspy if engine == "highspy" else solve_scipy)(prefix + ".lp", seconds)
    lb = int(-(-(dual - 1e-6) // 1))                       # ceil, tolerant to rounding
    ok = lb >= rep
    print(f"{prefix}: {engine} | {status} | optimum of the relaxed problem in [{dual:.2f}, {primal:.0f}] -> lower bound "
          f"{lb} | reported {rep} | {'OK' if ok else 'NOT CONFIRMED in this time'}")
    return ok


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    sys.exit(0 if main(a[0], float(a[1]) if len(a) > 1 else 1800.0, "highspy" if "--highspy" in sys.argv else "scipy") else 1)
