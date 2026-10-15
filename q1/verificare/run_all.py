#!/usr/bin/env python3
"""Runs the whole verification of the MinSet bounds and writes the report q1/verificare/RAPORT_ro.md.

For every graph: (1) .lp rewritten as the model on which the solver proved the lower bound (lb_model.py); (2) the
solver-free packing bound (packing.py); (3) the independent checker verify.py (acyclicity of G - S, every certificate
constraint is a real cycle, packing weights); (4) an independent re-solve of the .lp (solve_lp.py, scipy/HiGHS).
The confirmed lower bound is the larger of the packing bound and the re-solved bound: both are established without
trusting the run that produced the certificate.

  python3 q1/verificare/run_all.py [seconds per re-solve, default 1800] [code ...]
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_package import GRAPHS, NAMES, HERE, packing_bound

PY = sys.executable


def check(c, seconds):
    out = subprocess.run([PY, f"{HERE}/verify.py", GRAPHS[c], f"q1/exact/{c}"], capture_output=True, text=True).stdout
    acyclic = "G - S acyclic: True" in out
    invalid = int(re.search(r"invalid: (\d+)", out).group(1))
    weights = "valid weights: True" in out
    sol = subprocess.run([PY, f"{HERE}/solve_lp.py", f"q1/exact/{c}", str(seconds)], capture_output=True, text=True).stdout
    m = re.search(r"-> lower bound (\d+)", sol)
    return {"acyclic": acyclic, "invalid_cycles": invalid, "packing_weights_valid": weights,
            "resolved_lb": int(m.group(1)) if m else None, "resolve_log": sol.strip()}


def main(seconds=1800, only=()):
    codes = [c for c in GRAPHS if os.path.exists(f"q1/exact/{c}_names.txt") and (not only or c in only)]
    subprocess.run([PY, f"{HERE}/lb_model.py", *codes], check=True)
    pack = {c: packing_bound(c) for c in codes}
    with ThreadPoolExecutor(6) as ex:
        res = dict(zip(codes, ex.map(lambda c: check(c, seconds), codes)))
    rows, summary = [], {}
    for c in codes:
        r = json.load(open(f"q1/exact/{c}.json", encoding="utf8")); v = res[c]
        lo, hi = r["lower_bound"], r["upper_bound"]
        conf = max(pack[c], v["resolved_lb"] or 0)
        ok = v["acyclic"] and v["invalid_cycles"] == 0 and v["packing_weights_valid"]
        summary[c] = {"upper_bound": hi, "lower_bound_run": lo, "lower_bound_packing": pack[c],
                      "lower_bound_resolved": v["resolved_lb"], "lower_bound_confirmed": conf, "checks_passed": ok}
        gap = "exact" if conf == hi else f"{100 * (hi - conf) / hi:.2f}%"
        rows.append(f"| {NAMES[c]} | {hi:,} | {lo:,} | {v['resolved_lb'] or 0:,} | {pack[c]:,} | **{conf:,}** | {gap} | "
                    f"{'da' if ok else 'NU'} |")
    json.dump(summary, open(f"{HERE}/verificare.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
    allok = all(s["checks_passed"] for s in summary.values())
    rep = open(f"{HERE}/RAPORT_ro.template.md", encoding="utf8").read()
    rep = rep.replace("__TABEL__", "\n".join(
        ["| graf | limita superioară | limita inferioară (rularea) | re-rezolvare independentă | fără solver | "
         "**limita inferioară confirmată** | diferență | verificări |", "|---|---|---|---|---|---|---|---|"] + rows))
    rep = rep.replace("__SECUNDE__", f"{seconds / 60:.0f}")
    rep = rep.replace("__TOATE__", "Toate verificările au trecut." if allok else
                      "ATENȚIE: cel puțin o verificare a eșuat (coloana „verificări”).")
    open(f"{HERE}/RAPORT_ro.md", "w", encoding="utf8").write(rep)
    print("\n".join(rows)); print("toate verificarile au trecut" if allok else "VERIFICARE ESUATA")


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 1800, sys.argv[2:])
