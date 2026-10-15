#!/usr/bin/env python3
"""Rewrites <prefix>.lp as the model on which the solver proved the reported lower bound.

exact_minset.py only appends cycles, and a resumed run keeps the previous cycles in the same order, so the model of any
iteration is a prefix of <prefix>_cycles.json.gz. The logs give, for every iteration, the number of cycles in the model
and the lower bound; the proving model is the first one at which the final lower bound appears. Re-solving that model
(rather than the larger final one) is what reproduces the bound. The number of cycles is stored as "lb_cycles".

  python3 q1/verificare/lb_model.py <code> [<code> ...]       # uses q1/exact/<code>.log and q1/exact/<code>_round2.log
"""
import gzip, json, os, re, sys

LINE = re.compile(r"^iter \d+: .*limita inferioara=(\d+) .*cicluri=(\d+) ")


def proving_size(code, lb):
    for log in (f"q1/exact/{code}.log", f"q1/exact/{code}_round2.log"):
        if not os.path.exists(log): continue
        for line in open(log, encoding="utf8"):
            m = LINE.match(line)
            if m and int(m.group(1)) == lb: return int(m.group(2))
    return None


def main(code):
    prefix = f"q1/exact/{code}"
    res = json.load(open(prefix + ".json", encoding="utf8"))
    cycles = json.load(gzip.open(prefix + "_cycles.json.gz", "rt", encoding="utf8"))
    names = [l.rstrip("\n") for l in open(prefix + "_names.txt", encoding="utf8")]
    idx = {v: i for i, v in enumerate(names)}
    n = proving_size(code, res["lower_bound"]) or len(cycles)
    with open(prefix + ".lp", "w", encoding="utf8") as f:
        f.write("\\ min sum x_v  s.t.  sum_{v in c} x_v >= 1 for the first %d cycles of %s_cycles.json.gz;  x binary\n"
                % (n, os.path.basename(prefix)))
        f.write("\\ variable x<i> = word on line i+1 of " + os.path.basename(prefix) + "_names.txt\n")
        f.write("Minimize\n obj: " + " + ".join(f"x{i}" for i in range(len(names))) + "\nSubject To\n")
        for r, cyc in enumerate(cycles[:n]):
            f.write(f" c{r}: " + " + ".join(f"x{idx[v]}" for v in cyc) + " >= 1\n")
        f.write("Binary\n " + " ".join(f"x{i}" for i in range(len(names))) + "\nEnd\n")
    res["lb_cycles"] = n
    json.dump(res, open(prefix + ".json", "w", encoding="utf8"), ensure_ascii=False)
    print(f"{code}: lower bound {res['lower_bound']} proved on the first {n} of {len(cycles)} cycles")


if __name__ == "__main__":
    for c in sys.argv[1:]: main(c)
