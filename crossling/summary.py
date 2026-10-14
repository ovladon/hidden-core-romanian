#!/usr/bin/env python3
"""Cross-linguistic summary: one row per dictionary processed with the identical procedure.

Columns: headwords, mean content tokens per definition, unmapped and ambiguous token rates, Kernel and MinSet bounds
under both regimes, reciprocal pairs per 1,000 headwords and share of headwords defined by at most two words.

  python3 crossling/summary.py        # writes crossling/summary.json and prints a table
"""
import collections, json, os

DICTS = [("dex", "Romanian", "DEX, 2nd ed. (dexonline)"), ("ro_wikt", "Romanian", "Wiktionary (70% from DEX)"),
         ("it", "Italian", "Wiktionary"), ("es", "Spanish", "Wiktionary"), ("pt", "Portuguese", "Wiktionary"),
         ("fr", "French", "Wiktionary"), ("en", "English", "Wiktionary"), ("simple", "English", "Simple English Wiktionary"),
         ("wordnet", "English", "WordNet 3.0"), ("de", "German", "Wiktionary"), ("nl", "Dutch", "Wiktionary"),
         ("pl", "Polish", "Wiktionary"), ("cs", "Czech", "Wiktionary"), ("ru", "Russian", "Wiktionary"),
         ("el", "Greek", "Wiktionary")]
G = "crossling/graphs"


def files(code, reg):
    if code == "wordnet":
        return f"crossling/wordnet_{reg}.tsv", f"crossling/wordnet_{reg}.json", None
    return f"{G}/{code}_{reg}.tsv", f"{G}/{code}_{reg}.json", f"{G}/{code}_stats.json"


rows = []
for code, lang, src in DICTS:
    arcs, js, st = files(code, "freq")
    if not (os.path.exists(arcs) and os.path.exists(js)): continue
    r = {"code": code, "language": lang, "dictionary": src}
    if st and os.path.exists(st):
        s = json.load(open(st))
        r.update({"tokens_per_definition": s["mean_definition_tokens"], "unknown_rate": s["unknown_rate"],
                  "ambiguous_rate": s["ambiguous_rate"]})
    for reg in ("freq", "all"):
        a, j, _ = files(code, reg)
        if not os.path.exists(j): continue
        d = json.load(open(j)); N = d["headwords"]
        r[reg] = {"headwords": N, "kernel": len(d["kernel"]) / N, "core": len(d["core"]) / N,
                  "minset_lb": d["minset_lower_bound"] / N, "minset_ub": d["minset_upper_bound"] / N,
                  "kernel_n": len(d["kernel"]), "minset_lb_n": d["minset_lower_bound"], "minset_ub_n": d["minset_upper_bound"]}
        r["headwords"] = N
    out, indeg = collections.defaultdict(set), collections.Counter()
    for line in open(arcs, encoding="utf8"):
        u, v = line.rstrip("\n").split("\t"); out[u].add(v); indeg[v] += 1
    pairs = sum(1 for u in out for v in out[u] if u < v and u in out.get(v, ()))
    r["reciprocal_pairs_per_1000"] = 1000 * pairs / r["headwords"]; r["reciprocal_pairs"] = pairs
    r["short_definitions"] = sum(1 for v, k in indeg.items() if k <= 2) / max(1, len(indeg))
    rows.append(r)
json.dump(rows, open("crossling/summary.json", "w"), indent=1, ensure_ascii=False)
pc = lambda x: f"{100 * x:5.1f}"
print(f"{'dictionary':38s} {'N':>7s} {'tok':>5s} {'unk':>5s} | {'K freq':>6s} {'K all':>6s} | {'MinSet freq':>11s} {'MinSet all':>11s} | {'pairs/1k':>8s} {'<=2 w':>6s}")
for r in rows:
    f, a = r["freq"], r.get("all", r["freq"])
    print(f"{r['language'] + ' ' + r['dictionary']:38s} {r['headwords']:7d} {r.get('tokens_per_definition', float('nan')):5.1f} "
          f"{pc(r.get('unknown_rate', float('nan')))} | {pc(f['kernel'])}% {pc(a['kernel'])}% | "
          f"{pc(f['minset_lb'])}-{pc(f['minset_ub'])} {pc(a['minset_lb'])}-{pc(a['minset_ub'])} | "
          f"{r['reciprocal_pairs_per_1000']:8.1f} {pc(r['short_definitions'])}%")

print()
print(f"{'dictionary (regime freq), absolute numbers':44s} {'N':>7s} {'Kernel':>7s} {'MinSet':>13s} {'pairs':>7s} {'MinSet/Kernel':>13s}")
for r in rows:
    f = r["freq"]
    print(f"{r['language'] + ' ' + r['dictionary']:44s} {r['headwords']:7d} {f['kernel_n']:7d} {f['minset_lb_n']:6d}-{f['minset_ub_n']:6d} "
          f"{r['reciprocal_pairs']:7d} {100 * (f['minset_lb_n'] + f['minset_ub_n']) / 2 / f['kernel_n']:12.1f}%")
