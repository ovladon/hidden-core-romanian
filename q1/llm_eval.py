#!/usr/bin/env python3
"""Accuracy of the language model against the editors' links, compared with the most-frequent rule, and the
language-model regime of the graph (every ambiguous form takes the model's lemma; "none" drops the token).

  python3 -I q1/llm_eval.py <code>          # needs q1/llm/<code>_choices.json and q1/human/<code>_records.jsonl.gz
"""
import collections, gzip, json, math, re, subprocess, sys, unicodedata

STRESS = re.compile("[̀́]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower().strip()
TOKEN = re.compile(r"[^\W\d_]+")


def wilson(k, n, z=1.96):
    if not n: return [0, 0]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def main(code):
    H = {l.strip() for l in open(f"crossling/graphs/{code}_headwords.txt", encoding="utf8") if l.strip()}
    fmap = json.load(gzip.open(f"q1/forms/{code}.json.gz", "rt", encoding="utf8"))
    closed = {l.strip() for l in open(f"q1/human/{code}_records_closed.txt", encoding="utf8") if l.strip()}
    func = closed - H
    cands = lambda t: set() if (t in func or len(t) == 1) else ({t} | set(fmap.get(t, ()))) & H
    ch = json.load(open(f"q1/llm/{code}_choices.json", encoding="utf8"))
    recs = [json.loads(l) for l in gzip.open(f"q1/human/{code}_records.jsonl.gz", "rt", encoding="utf8")]
    recs = [r for r in recs if nf(r["word"]) in H]
    tokfreq = collections.Counter(t for r in recs for t in TOKEN.findall(nf(r["gloss"])))
    score = collections.Counter({w: tokfreq.get(w, 0) for w in H})
    for t, k in tokfreq.items():
        c = cands(t)
        if len(c) == 1: score[next(iter(c))] += k
    rule = lambda t, c: max(c, key=lambda x: (score[x], x == t, x))
    # toleranta: lema aleasa e ea insasi o forma flexionara a lemei din eticheta SI e fie aceeasi parte de vorbire
    # (variante: bakterie/bakterium), fie adjectiv/participiu al unui verb (dotyczacy/dotyczyc, verwendet/verwenden).
    # Omografele de alta parte de vorbire (verbul "bäumen" in loc de "Baum") raman erori.
    POS = {w: set(p) for w, p in json.load(gzip.open(f"q1/pos/{code}.json.gz", "rt", encoding="utf8")).items()}
    def near(p, tg):
        if p == tg: return True
        if tg not in fmap.get(p, ()): return False
        a, b = POS.get(p, set()), POS.get(tg, set())
        return bool(a & b) or ("adj" in a and "verb" in b)
    st = collections.Counter()
    for r in recs:
        v = nf(r["word"])
        for surface, target in r.get("links") or []:
            s, tg = nf(surface), nf(target)
            c = cands(s)
            if not TOKEN.fullmatch(s or "-") or len(c) < 2 or tg not in c: continue
            key = f"{v}\t{s}"
            if key not in ch: continue
            g = "deliberate" if s != tg else "plain"
            for grp in (g, "all"):
                st[grp] += 1; st[grp + "_llm"] += ch[key] == [tg]; st[grp + "_rule"] += rule(s, c) == tg
                st[grp + "_llm_len"] += len(ch[key]) == 1 and near(ch[key][0], tg)
                st[grp + "_rule_len"] += near(rule(s, c), tg)
    res = {"code": code, "choices": len(ch)}
    for g in ("deliberate", "plain", "all"):
        n = st[g]
        res[g] = {"links": n, "llm_accuracy": st[g + "_llm"] / n if n else None, "llm_ci95": wilson(st[g + "_llm"], n),
                  "rule_accuracy": st[g + "_rule"] / n if n else None, "rule_ci95": wilson(st[g + "_rule"], n),
                  "llm_lenient": st[g + "_llm_len"] / n if n else None, "rule_lenient": st[g + "_rule_len"] / n if n else None}
    arcs = set()
    for r in recs:
        v = nf(r["word"])
        for t in TOKEN.findall(nf(r["gloss"])):
            c = cands(t)
            if not c: continue
            picks = ch.get(f"{v}\t{t}") if len(c) > 1 else None
            if picks is None: picks = [next(iter(c))] if len(c) == 1 else [rule(t, c)]
            for p in picks:
                if p != v: arcs.add((p, v))
    path = f"q1/llm/{code}_llm.tsv"
    with open(path, "w", encoding="utf8") as f:
        for u, w in sorted(arcs): f.write(f"{u}\t{w}\n")
    subprocess.run([sys.executable, "latent_structure.py", path, "--headwords", f"crossling/graphs/{code}_headwords.txt",
                    "--json", f"q1/llm/{code}_llm.json"], capture_output=True)
    d = json.load(open(f"q1/llm/{code}_llm.json")); N = d["headwords"]; k = len(d["kernel"])
    res["llm_regime"] = {"arcs": len(arcs), "kernel": k / N, "minset": [d["minset_lower_bound"] / N, d["minset_upper_bound"] / N],
                         "minset_over_kernel": (d["minset_lower_bound"] + d["minset_upper_bound"]) / 2 / k,
                         "pairs_per_1000": 1000 * len(d["reciprocal_pairs"]) / N}
    json.dump(res, open(f"q1/llm/{code}_eval.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
