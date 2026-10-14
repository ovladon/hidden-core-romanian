#!/usr/bin/env python3
"""Care tokeni produc cele mai multe legaturi in regimul 'all' (diagnostic pentru maparea forma -> lema)."""
import collections, sys
out = collections.defaultdict(set)
for line in open(sys.argv[1], encoding="utf8"):
    u, v = line.rstrip("\n").split("\t"); out[u].add(v)
fr = collections.defaultdict(set)
for line in open(sys.argv[2], encoding="utf8"):
    u, v = line.rstrip("\n").split("\t"); fr[u].add(v)
diff = sorted(((len(out[u]) - len(fr.get(u, ())), u) for u in out), reverse=True)[:25]
print([(u, n, len(fr.get(u, ()))) for n, u in diff])
