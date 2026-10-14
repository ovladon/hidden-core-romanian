#!/usr/bin/env python3
"""Q1, task 1: the human gold standard in full.

Gold labels: the links that Romanian Wiktionary editors placed by hand in first definitions that are near-copies of the
DEX first sense (similarity >= 0.8). Only forms that are ambiguous in the dexonline inflection tables and for which the
language model made a choice are scored. Deliberate links ([[lemma|form]], lemma != form) are the reliable gold; plain
links ([[form]]) may simply point to the page of the form and are reported separately.

Outputs
  q1/gold_records.tsv     one row per scored link
  q1/gold_summary.json    accuracy by link type, regime and error category
  q1/choices_goldfix.json the model's choices with every deliberate gold label substituted (to rebuild the graph)

  python3 -I q1/gold_analysis.py crossling/raw/ro/rowiktionary-latest-pages-articles.xml.bz2
"""
import bz2, collections, difflib, json, math, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import kernel

kernel.MODE["first_sense"], kernel.MODE["no_expr"] = True, True
HEADER = re.compile(r"\{\{-(substantiv|verb|adjectiv|adverb|numeral)-(?:\|ron)?\}\}")
POSCLASS = {"M": "noun", "F": "noun", "N": "noun", "MF": "noun", "SF": "noun", "FF": "noun", "NL": "noun",
            "A": "adj", "AF": "adj", "AM": "adj", "AN": "adj", "V": "verb", "VT": "verb", "P": "pron", "PT": "pron",
            "I": "invar", "IL": "invar", "SP": "noun", "T": "other"}


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def first_def_line(text):
    m = re.search(r"==\s*\{\{limba\|ron\}\}\s*==(.*?)(?=\n==\s*\{\{limba\||\Z)", text, re.S)
    if not m: return None
    h = HEADER.search(m.group(1))
    if not h: return None
    return next((l.lstrip("#").strip() for l in m.group(1)[h.end():].split("\n") if re.match(r"#(?![:*#])", l)), None)


def clean(s):
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", " ", s).replace("'''", "").replace("''", "")
    return re.sub(r"^\s*(\([^()]*\)\s*)+", "", re.sub(r"\s+", " ", s)).strip()


def main(dump):
    D = kernel.load_defs((1, 2)); dex = {}; varlist = collections.defaultdict(set)
    for lex, rep in zip(D.lexicon, D.internalRep):
        h = kernel.norm(lex).strip()
        if h not in dex: dex[h] = re.sub(r"\s+", " ", kernel.clean(rep)).strip(" ;,.*").lower()
        # variantele inregistrate chiar de DEX: "Var.: @'arbor@ #s. m.#"
        for seg in re.findall(r"Var\.[^\n]{0,250}", rep):
            seg = re.split(r"\s[–-]\s", seg)[0]
            varlist[h] |= {kernel.norm(t) for t in re.findall(r"[^\W\d_]+", re.sub(r"[@#$^'\u0301]", "", seg))}
    H = set(dex)
    L = pd.read_pickle("data/Lexeme.pkl"); F = pd.read_pickle("data/InflectedForm.pkl"); I = pd.read_pickle("data/Inflection.pkl")
    lexform = dict(zip(L.id, (kernel.norm(x) for x in L.formNoAccent)))
    lexpos = collections.defaultdict(set)
    for f_, mt in zip(L.formNoAccent, L.modelType): lexpos[kernel.norm(f_)].add(POSCLASS.get(mt, "other"))
    freq = collections.defaultdict(float)
    for f_, fr in zip(L.formNoAccent, L.frequency): freq[kernel.norm(f_)] = max(freq[kernel.norm(f_)], fr or 0.0)
    infl = dict(zip(I.id, I.description))
    # variante ale aceluiasi cuvant: leme care apartin aceleiasi intrari dexonline (arbore/arbor, strugure/strugur)
    EL = pd.read_pickle("data/EntryLexeme.pkl")
    entries_of = collections.defaultdict(set)
    for eid, lid in zip(EL.entryId, EL.lexemeId):
        if lid in lexform: entries_of[lexform[lid]].add(eid)
    form2lem, how = collections.defaultdict(set), collections.defaultdict(set)
    for form, lid, iid in zip(F.formNoAccent, F.lexemeId, F.inflectionId):
        lem = lexform.get(lid)
        if lem in H:
            fm = kernel.norm(form); form2lem[fm].add(lem); how[(fm, lem)].add(infl.get(iid, ""))
    for h in H: form2lem[h].add(h)
    choices = json.load(open("ai/choices_haiku12.json", encoding="utf8"))
    words = lambda s: re.sub(r"[^\w ]", " ", s.lower()).split()

    def pos_of(form, lem):
        """Partea de vorbire a formei pentru o lema, din descrierile flexionare dexonline (Substantiv..., Verb...)."""
        out = set()
        for d in how.get((form, lem), ()):
            if d.startswith("Substantiv"): out.add("noun")
            elif d.startswith("Adjectiv"): out.add("adj")
            elif "Participiu" in d: out.add("participle")
            elif d.startswith("Verb"): out.add("verb")
            elif d.startswith(("Pronume", "Articol", "Numeral")): out.add("function")
            elif d: out.add("invariable")
        return out or {"invariable"}

    def category(form, gold, pred):
        """Tipul dezacordului dintre eticheta umana si alegerea modelului."""
        if not pred: return "no_choice"
        pg, pp = pos_of(form, gold), pos_of(form, pred)
        if pred in varlist.get(gold, ()) or gold in varlist.get(pred, ()):
            return "lemma_variant"                      # varianta inregistrata in DEX (Var.): arbore/arbor, referi/refera
        if "participle" in pg | pp and pg & {"adj", "noun"} | pp & {"adj", "noun"}: return "participle_vs_adjective"
        if "verb" in pg and "verb" in pp: return "two_verbs"
        if ("noun" in pg and "verb" in pp) or ("verb" in pg and "noun" in pp): return "noun_vs_verb"
        if ("noun" in pg and "adj" in pp) or ("adj" in pg and "noun" in pp): return "noun_vs_adjective"
        if "noun" in pg and "noun" in pp: return "two_nouns"
        if "function" in pg | pp or "invariable" in pg | pp: return "function_vs_content"
        return "other"

    recs, pages = [], 0
    title, buf, intext = None, [], False
    with bz2.open(dump, "rt", encoding="utf8") as f:
        for line in f:
            mt = re.search(r"<title>(.*?)</title>", line)
            if mt: title = mt.group(1)
            if "<text" in line: intext = True; buf = [line.split(">", 1)[-1]]
            elif intext: buf.append(line)
            if not (intext and "</text>" in line): continue
            intext = False
            h = kernel.norm(title or "").strip()
            if h not in dex: continue
            text = "".join(buf).split("</text>")[0].replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            raw = first_def_line(text)
            if not raw or difflib.SequenceMatcher(None, words(clean(raw)), words(dex[h])).ratio() < 0.8: continue
            pages += 1
            for target, form in re.findall(r"\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]", raw):
                piped = bool(form) and kernel.norm(form).strip() != kernel.norm(target).strip()
                form = kernel.norm(form or target).strip(); target = kernel.norm(target).strip()
                cands = form2lem.get(form, set())
                key = f"{h}\t{form}"
                if len(cands) < 2 or target not in cands or key not in choices: continue
                llm = choices[key]
                rule = max(cands, key=lambda x: (freq[x], x == form, x))
                pred = llm[0] if len(llm) == 1 else ("|".join(llm) or "-")
                ok = target in llm and len(llm) == 1
                recs.append({"headword": h, "form": form, "gold": target, "piped": piped, "llm": pred, "llm_ok": ok,
                             "rule": rule, "rule_ok": rule == target, "n_cands": len(cands),
                             "category": "" if ok else category(form, target, llm[0] if llm else "")})
    R = pd.DataFrame(recs)
    R.to_csv("q1/gold_records.tsv", sep="\t", index=False)
    out = {"pages_copied_from_dex": pages, "scored_links": len(R)}
    for name, sub in (("deliberate", R[R.piped]), ("plain", R[~R.piped]), ("all", R)):
        n = len(sub); kl, kr = int(sub.llm_ok.sum()), int(sub.rule_ok.sum())
        cats = sub[~sub.llm_ok].category.value_counts().to_dict()
        lenient = kl + cats.get("participle_vs_adjective", 0) + cats.get("lemma_variant", 0)
        out[name] = {"links": n, "llm_accuracy": kl / n, "llm_ci95": wilson(kl, n),
                     "rule_accuracy": kr / n, "rule_ci95": wilson(kr, n),
                     "llm_accuracy_lenient": lenient / n, "llm_ci95_lenient": wilson(lenient, n),
                     "llm_errors_by_category": cats,
                     "accuracy_by_candidates": {str(k): float(v) for k, v in sub.groupby(sub.n_cands.clip(upper=4)).llm_ok.mean().items()}}
    err = R[R.piped & ~R.llm_ok].groupby(["form", "gold", "llm", "category"]).size().sort_values(ascending=False).head(30)
    out["top_errors_deliberate"] = [[*k, int(v)] for k, v in err.items()]
    json.dump(out, open("q1/gold_summary.json", "w"), indent=1, ensure_ascii=False)
    fix = dict(choices); changed = 0
    for r in recs:
        if r["piped"] and not r["llm_ok"]:
            fix[f"{r['headword']}\t{r['form']}"] = [r["gold"]]; changed += 1
    json.dump(fix, open("q1/choices_goldfix.json", "w"), ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "top_errors_deliberate"}, indent=1, ensure_ascii=False))
    print("alegeri inlocuite cu eticheta umana:", changed)


if __name__ == "__main__":
    main(sys.argv[1])
