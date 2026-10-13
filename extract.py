#!/usr/bin/env python3
"""Extrage din dump-ul dexonline (dex-database.sql.gz) tabelele de care avem nevoie, ca .pkl.

MySQL local nu e accesibil (fara parola), asa ca parsam direct INSERT-urile mysqldump.
O singura trecere prin fisierul comprimat; fiecare tabel devine un DataFrame.

  python3 extract.py            # scrie data/<Tabel>.pkl
"""
import gzip, re, sys, pickle, time
import pandas as pd

DUMP = "data/dex-database.sql.gz"
WANT = {"Source", "Definition", "Lexeme", "InflectedForm", "Inflection", "Entry",
        "EntryDefinition", "EntryLexeme", "Meaning", "Tree", "TreeEntry", "Relation"}
# coloanele pe care le pastram (restul se arunca, ca sa incapa in memorie)
KEEP = {
    "InflectedForm": ["formNoAccent", "lexemeId", "inflectionId"],
    "Lexeme": ["id", "form", "formNoAccent", "description", "frequency", "stopWord",
               "compound", "modelType", "modelNumber"],
    "Definition": ["id", "sourceId", "lexicon", "internalRep", "status", "structured"],
}

TOK = re.compile(r"""\(|\)|,|NULL|'(?:[^'\\]|\\.)*'|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?""", re.S)
ESC = {"0": "\0", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a"}


def unescape(s):
    return re.sub(r"\\(.)", lambda m: ESC.get(m.group(1), m.group(1)), s[1:-1])


def parse_values(payload):
    row, rows, depth = [], [], 0
    for m in TOK.finditer(payload):
        t = m.group(0)
        if t == "(":
            depth += 1; row = []
        elif t == ")":
            depth -= 1; rows.append(row)
        elif t == ",":
            continue
        elif t == "NULL":
            row.append(None)
        elif t[0] == "'":
            row.append(unescape(t))
        else:
            row.append(float(t) if any(c in t for c in ".eE") else int(t))
    return rows


def main():
    cols, data = {}, {t: [] for t in WANT}
    cur = None
    t0 = time.time()
    with gzip.open(DUMP, "rt", encoding="utf8", errors="replace") as f:
        for line in f:
            if line.startswith("CREATE TABLE `"):
                cur = line.split("`")[1]
                if cur in WANT:
                    cols[cur] = []
                continue
            if cur in WANT and cur in cols and line.startswith("  `"):
                cols[cur].append(line.split("`")[1])
                continue
            if line.startswith("INSERT INTO `"):
                t = line.split("`")[1]
                if t not in WANT:
                    continue
                rows = parse_values(line[line.index(" VALUES ") + 8:])
                keep = KEEP.get(t)
                if keep:
                    idx = [cols[t].index(c) for c in keep]
                    rows = [[r[i] for i in idx] for r in rows]
                data[t].extend(rows)
    for t, rows in data.items():
        c = KEEP.get(t, cols.get(t, []))
        df = pd.DataFrame(rows, columns=c if rows and len(c) == len(rows[0]) else None)
        df.to_pickle(f"data/{t}.pkl")
        print(f"{t:<16}{len(df):>10} randuri")
    print(f"gata in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
