#!/usr/bin/env python3
"""Builds the verification package of the MinSet bounds: the table of q1/verificare/README_ro.md and the archive
q1/verificare/pachet_verificare_minset.tar.gz (graphs, solutions, certificates, the two checkers, the README).

  python3 q1/verificare/make_package.py
"""
import gzip, io, json, os, subprocess, sys, tarfile

GRAPHS = {"dex_llm": "out/graph_src12_freq_noexpr_first_ai.tsv", "wordnet": "crossling/wordnet_freq.tsv"}
for c in "dex ro_wikt it es pt fr en simple de nl pl cs ru el".split():
    GRAPHS[c] = f"crossling/graphs/{c}_freq.tsv"
NAMES = {"dex_llm": "DEX, dezambiguizare LLM (lucrarea ConsILR)", "wordnet": "WordNet (engleză)",
         "dex": "DEX, aceeași procedură ca Wiktionary", "ro_wikt": "Wiktionary românesc", "it": "Wiktionary italian",
         "es": "Wiktionary spaniol", "pt": "Wiktionary portughez", "fr": "Wiktionary francez",
         "en": "Wiktionary englez", "simple": "Simple English Wiktionary", "de": "Wiktionary german",
         "nl": "Wiktionary olandez", "pl": "Wiktionary polonez", "cs": "Wiktionary ceh", "ru": "Wiktionary rus",
         "el": "Wiktionary grec"}
HERE = "q1/verificare"


def packing_bound(c):
    """Limita din impachetarea fractionara (o calculeaza packing.py daca lipseste sau e mai veche decat ciclurile)."""
    p, cy = f"q1/exact/{c}_packing.json.gz", f"q1/exact/{c}_cycles.json.gz"
    if not os.path.exists(p) or os.path.getmtime(p) < os.path.getmtime(cy):
        subprocess.run([sys.executable, f"{HERE}/packing.py", f"q1/exact/{c}"], check=True, capture_output=True)
    y = json.load(gzip.open(p, "rt")); cyc = json.load(gzip.open(cy, "rt", encoding="utf8"))
    load = {}
    for cc, w in zip(cyc, y):
        for v in cc: load[v] = load.get(v, 0) + w
    return -(-sum(y) // max(load.values()))


def table():
    rows = ["| cod | dicționar | cuvinte pe cicluri | limita inferioară (ILP) | limita fără solver | limita superioară | diferență | cicluri în certificat |",
            "|---|---|---|---|---|---|---|---|"]
    done = []
    for c in GRAPHS:
        p = f"q1/exact/{c}.json"
        if not os.path.exists(p) or not os.path.exists(f"q1/exact/{c}_names.txt"): continue
        r = json.load(open(p, encoding="utf8")); done.append(c)
        lo, hi = r["lower_bound"], r["upper_bound"]
        gap = "exact" if lo == hi else f"{100 * (hi - lo) / hi:.2f}%"
        rows.append(f"| {c} | {NAMES[c]} | {r['vertices_on_cycles']:,} | {lo:,} | {packing_bound(c):,} | {hi:,} | {gap} | "
                    f"{r['cycles_used']:,} |")
    return "\n".join(rows), done


def main():
    # .lp = modelul pe care solverul a demonstrat limita inferioara (lb_model.py, din jurnale)
    codes = [c for c in GRAPHS if os.path.exists(f"q1/exact/{c}_names.txt")]
    subprocess.run([sys.executable, f"{HERE}/lb_model.py", *codes], check=True)
    tab, done = table()
    src = open(f"{HERE}/README_ro.template.md", encoding="utf8").read()
    readme = src.replace("__TABEL__", tab)
    open(f"{HERE}/README_ro.md", "w", encoding="utf8").write(readme)
    out = f"{HERE}/pachet_verificare_minset.tar.gz"
    with tarfile.open(out, "w:gz") as t:
        def add_bytes(name, data):
            ti = tarfile.TarInfo("pachet_verificare_minset/" + name); ti.size = len(data); ti.mode = 0o644
            t.addfile(ti, io.BytesIO(data))
        add_bytes("README_ro.md", readme.encode("utf8"))
        for f in ("verify.py", "solve_lp.py", "verifica_tot.sh", "packing.py"):
            add_bytes(f, open(f"{HERE}/{f}", "rb").read())
        for c in done:
            add_bytes(f"graphs/{c}.tsv.gz", gzip.compress(open(GRAPHS[c], "rb").read()))
            for ext in (".json", "_names.txt", "_cycles.json.gz", "_packing.json.gz"):
                add_bytes(f"exact/{c}{ext}", open(f"q1/exact/{c}{ext}", "rb").read())
            add_bytes(f"exact/{c}.lp.gz", gzip.compress(open(f"q1/exact/{c}.lp", "rb").read()))
    print(tab)
    print(f"\n{out}: {len(done)} dicționare, {os.path.getsize(out) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
