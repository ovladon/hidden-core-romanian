#!/usr/bin/env python3
"""Gold standard for lemma disambiguation, made by humans and already available: the links that Romanian Wiktionary
editors placed by hand in definitions copied from the DEX ([[avea|având]] = the form 'având' belongs to 'avea').

For every Romanian Wiktionary page whose first definition is a near-copy of the DEX first sense (similarity >= 0.8),
each link [[lemma|form]] whose form is ambiguous in the dexonline inflection tables is compared with
  - the choice of the language model (ai/choices_haiku12.json),
  - the most-frequent-candidate rule (dexonline frequencies, as in kernel.py).

  python3 -I crossling/wikt_gold.py crossling/raw/ro/rowiktionary-latest-pages-articles.xml.bz2
"""
import bz2, collections, difflib, json, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import kernel

kernel.MODE["first_sense"], kernel.MODE["no_expr"] = True, True
HEADER = re.compile(r"\{\{-(substantiv|verb|adjectiv|adverb|numeral)-(?:\|ron)?\}\}")


def first_def_lines(text):
    m = re.search(r"==\s*\{\{limba\|ron\}\}\s*==(.*?)(?=\n==\s*\{\{limba\||\Z)", text, re.S)
    if not m: return []
    out = []
    for h in HEADER.finditer(m.group(1)):
        rest = m.group(1)[h.end():]
        line = next((l for l in rest.split("\n") if re.match(r"#(?![:*#])", l)), None)
        if line: out.append(line.lstrip("#").strip())
    return out


def clean(s):
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", " ", s).replace("'''", "").replace("''", "")
    return re.sub(r"^\s*(\([^()]*\)\s*)+", "", re.sub(r"\s+", " ", s)).strip()


def main(dump):
    D = kernel.load_defs((1, 2)); dex = {}
    for lex, rep in zip(D.lexicon, D.internalRep):
        h = kernel.norm(lex).strip()
        if h not in dex: dex[h] = re.sub(r"\s+", " ", kernel.clean(rep)).strip(" ;,.*").lower()
    L = pd.read_pickle("data/Lexeme.pkl"); F = pd.read_pickle("data/InflectedForm.pkl")
    H = set(dex)
    lexform = dict(zip(L.id, (kernel.norm(x) for x in L.formNoAccent)))
    freq = collections.defaultdict(float)
    for f_, fr in zip(L.formNoAccent, L.frequency): freq[kernel.norm(f_)] = max(freq[kernel.norm(f_)], fr or 0.0)
    form2lem = collections.defaultdict(set)
    for form, lid in zip(F.formNoAccent, F.lexemeId):
        lem = lexform.get(lid)
        if lem in H: form2lem[kernel.norm(form)].add(lem)
    for h in H: form2lem[h].add(h)
    choices = json.load(open("ai/choices_haiku12.json", encoding="utf8"))
    words = lambda s: re.sub(r"[^\w ]", " ", s.lower()).split()
    stats = collections.Counter(); errors = collections.Counter(); examples = []
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
            for raw in first_def_lines(text)[:1]:
                if difflib.SequenceMatcher(None, words(clean(raw)), words(dex[h])).ratio() < 0.8: continue
                stats["pages"] += 1
                for target, form in re.findall(r"\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]", raw):
                    piped = bool(form) and kernel.norm(form).strip() != kernel.norm(target).strip()
                    form = kernel.norm(form or target).strip(); target = kernel.norm(target).strip()
                    cands = form2lem.get(form, set())
                    if len(cands) < 2 or target not in cands: continue
                    key = f"{h}\t{form}"
                    if key not in choices: continue
                    llm = choices[key]
                    rule = max(cands, key=lambda x: (freq[x], x == form))
                    for grp in ("all", "piped" if piped else "self"):
                        stats[grp + "_links"] += 1
                        stats[grp + "_llm_ok"] += target in llm and len(llm) == 1
                        stats[grp + "_rule_ok"] += rule == target
                    stats["links"] += 1; stats["llm_ok"] += target in llm and len(llm) == 1
                    stats["llm_contains"] += target in llm; stats["rule_ok"] += rule == target
                    if target not in llm:
                        errors[(form, target, ",".join(llm) or "-")] += 1
    n = stats["links"]
    res = {"pages_copied_from_dex": stats["pages"], "ambiguous_links": n,
           "llm_accuracy_exact": stats["llm_ok"] / n, "llm_accuracy_contains": stats["llm_contains"] / n,
           "most_frequent_rule_accuracy": stats["rule_ok"] / n,
           "frequent_llm_errors": [[*k, c] for k, c in errors.most_common(25)]}
    for grp in ("piped", "self"):
        m = stats[grp + "_links"]
        res[grp] = {"links": m, "llm_accuracy": stats[grp + "_llm_ok"] / max(1, m), "rule_accuracy": stats[grp + "_rule_ok"] / max(1, m)}
    json.dump(res, open("crossling/wikt_gold.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "frequent_llm_errors"}, indent=1))
    print("erori frecvente ale modelului (forma, eticheta Wiktionary, alegerea modelului, de cate ori):")
    for e in res["frequent_llm_errors"][:15]: print("  ", e)


if __name__ == "__main__":
    main(sys.argv[1])
