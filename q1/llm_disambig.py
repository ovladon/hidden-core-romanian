#!/usr/bin/env python3
"""Language-model disambiguation for any Wiktionary, with the procedure used for the DEX (disambig.py):
fifteen definitions per request, numbered candidates, answers reduced to the number of the chosen lemma.
Candidates are the headwords of our graph of which the form can be an inflected form (same map as the graph).

  python3 -I q1/llm_disambig.py <code> <lang_code> <Language> <extract.jsonl.gz> --estimate
  python3 -I q1/llm_disambig.py <code> <lang_code> <Language> <extract.jsonl.gz>       # needs ANTHROPIC_API_KEY

Outputs: q1/llm/<code>_raw.jsonl (every request and answer, resumable), q1/llm/<code>_choices.json
"""
import collections, gzip, json, os, re, sys, time, unicodedata
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from llm import ask

MODEL = "claude-haiku-4-5-20251001"; PER_REQ = 15; PRICE = (1.0, 5.0)
STRESS = re.compile("[̀́]")
nf = lambda s: STRESS.sub("", unicodedata.normalize("NFC", s or "")).lower().strip()
TOKEN = re.compile(r"[^\W\d_]+")
CONTENT = {"noun", "verb", "adj", "adv", "num"}
INSTR = ("You are a lexicographer. Each definition below comes from a {lang} dictionary. Some of its words are "
         "ambiguous: the same form can belong to several lemmas. For each marked word, choose, in the context of the "
         "definition, the lemma it belongs to.\n"
         "Answer ONLY with one line per marked word, of the form ID.k=n (ID = number of the definition, k = number of "
         "the word, n = number of the chosen lemma). Normally choose ONE lemma. Only if the same word occurs several "
         "times in the definition with different functions, give the numbers separated by commas (ID.k=n,m). If no "
         "lemma fits, write ID.k=0. No explanations.\n\n")


def build(code, lang, extract):
    H = {l.strip() for l in open(f"crossling/graphs/{code}_headwords.txt", encoding="utf8") if l.strip()}
    fmap = json.load(gzip.open(f"q1/forms/{code}.json.gz", "rt", encoding="utf8"))
    closed = {l.strip() for l in open(f"q1/human/{code}_records_closed.txt", encoding="utf8") if l.strip()}
    func = closed - H
    pos = collections.defaultdict(set); key = f'"lang_code": "{lang}"'
    with gzip.open(extract, "rt", encoding="utf8") as f:
        for line in f:
            if key not in line: continue
            d = json.loads(line)
            if d.get("lang_code") == lang and d.get("pos") in CONTENT: pos[nf(d.get("word"))].add(d["pos"])
    items = []
    for r in (json.loads(l) for l in gzip.open(f"q1/human/{code}_records.jsonl.gz", "rt", encoding="utf8")):
        w = nf(r["word"])
        if w not in H: continue
        amb, seen = [], set()
        for t in TOKEN.findall(nf(r["gloss"])):
            if t in func or len(t) == 1 or t in seen: continue
            c = ({t} | set(fmap.get(t, ()))) & H
            if len(c) > 1: seen.add(t); amb.append((t, sorted(c)))
        if amb: items.append({"head": w, "text": r["gloss"][:600], "amb": amb})
    return items, pos


def render(batch, pos, lang):
    out = [INSTR.format(lang=lang)]
    for i, it in enumerate(batch, 1):
        out.append(f"[{i}] Headword: {it['head']}\nDefinition: {it['text']}")
        for k, (t, cands) in enumerate(it["amb"], 1):
            opts = " ".join(f"({n}) {c}" + (f" [{', '.join(sorted(pos[c]))}]" if pos.get(c) else "") for n, c in enumerate(cands, 1))
            out.append(f"  {i}.{k} «{t}»: {opts}")
        out.append("")
    return "\n".join(out)


def parse(resp, batch):
    got = {}
    for i, k, ns in re.findall(r"(\d+)\.(\d+)[ \t]*=[ \t]*(\d+(?:[ \t]*,[ \t]*\d+)*)", resp or ""):
        i, k = int(i), int(k)
        if 1 <= i <= len(batch) and 1 <= k <= len(batch[i - 1]["amb"]):
            t, cands = batch[i - 1]["amb"][k - 1]
            got[f"{batch[i - 1]['head']}\t{t}"] = sorted({cands[int(n) - 1] for n in re.findall(r"\d+", ns) if 1 <= int(n) <= len(cands)})
    return got


def main():
    code, lang, language, extract = sys.argv[1:5]
    items, pos = build(code, lang, extract)
    batches = [items[i:i + PER_REQ] for i in range(0, len(items), PER_REQ)]
    chars = sum(len(render(b, pos, language)) for b in batches)
    n_amb = sum(len(it["amb"]) for it in items)
    est = chars / 3.5 / 1e6 * PRICE[0] + n_amb * 8 / 1e6 * PRICE[1]
    print(f"{code}: {len(items)} definitii cu {n_amb} forme ambigue, {len(batches)} cereri, cost estimat ~{est:.1f} USD", flush=True)
    if "--estimate" in sys.argv: return
    key = os.environ.get("ANTHROPIC_API_KEY") or sys.exit("lipseste ANTHROPIC_API_KEY")
    os.makedirs("q1/llm", exist_ok=True); rawp = f"q1/llm/{code}_raw.jsonl"
    done = set()
    if os.path.exists(rawp):
        for l in open(rawp, encoding="utf8"):
            try:
                rec = json.loads(l)
                if rec.get("resp"): done.add(rec["batch"])      # cererile esuate (ex. credit epuizat) se reiau
            except Exception: pass
    todo = [(i, b) for i, b in enumerate(batches) if i not in done]
    if "--pilot" in sys.argv: todo = todo[:int(sys.argv[sys.argv.index("--pilot") + 1])]
    cost = [0.0]

    def work(ib):
        i, b = ib
        out, ti, to, err = ask(render(b, pos, language), MODEL, "anthropic", key)
        cost[0] += ti / 1e6 * PRICE[0] + to / 1e6 * PRICE[1]
        return {"batch": i, "resp": out, "err": err}
    with ThreadPoolExecutor(8) as ex, open(rawp, "a", encoding="utf8") as g:
        for k, rec in enumerate(ex.map(work, todo), 1):
            g.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if k % 200 == 0: print(f"  {k}/{len(todo)} cereri | cost ~{cost[0]:.2f} USD", flush=True)
    choices = {}
    for l in open(rawp, encoding="utf8"):
        rec = json.loads(l)
        if rec.get("resp"): choices.update(parse(rec["resp"], batches[rec["batch"]]))
    json.dump(choices, open(f"q1/llm/{code}_choices.json", "w"), ensure_ascii=False)
    print(f"{code}: {len(choices)} alegeri din {n_amb} forme ambigue | cost acestei rulari ~{cost[0]:.2f} USD")


if __name__ == "__main__":
    main()
