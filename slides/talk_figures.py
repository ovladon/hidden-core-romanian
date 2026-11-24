#!/usr/bin/env python3
"""Figures of the short conference talk (slides/talk_*.png): a real piece of the DEX graph and a one-bar-per-language
comparison. Run from slides/.
"""
import json, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

NAVY, ORANGE, BLUE, PALEBLUE, GREY = "#13233f", "#eb6834", "#2a78d6", "#9cc3ef", "#b9b8b3"

# ── a real neighbourhood of the DEX graph, coloured by layer
k = json.load(open("../out/kernel_src12_freq_noexpr_first_ai.json"))
K, C = set(k["kernel"]), set(k["core"])
M = set(json.load(open("../out/minset_exact_src12_freq_noexpr_first_ai.json"))["minset_best"])
nodes = ["copac", "arbore", "pom", "plantă", "trunchi", "lemnos", "ramură", "frunză", "coroană", "stejar", "brad", "fag",
         "pădure", "livadă", "fruct", "rădăcină", "creangă", "tulpină", "lemn", "măr", "fructifer"]
G = nx.DiGraph(); G.add_nodes_from(nodes)
for line in open("../out/graph_src12_freq_noexpr_first_ai.tsv", encoding="utf8"):
    u, v = line.rstrip("\n").split("\t")[:2]
    if u in G and v in G and u != v: G.add_edge(u, v)
layer = lambda w: "MinSet" if w in M else "Core" if w in C else "Satellite" if w in K else "Rest"
COL = {"MinSet": ORANGE, "Core": BLUE, "Satellite": PALEBLUE, "Rest": GREY}
pos = nx.kamada_kawai_layout(G.to_undirected())


def draw(fname, dark):
    fig, ax = plt.subplots(figsize=(7.5, 6.2)); fig.patch.set_alpha(0); ax.set_axis_off()
    ec = "#ffffff" if dark else "#3b3a37"
    for u, v in G.edges():
        mutual = G.has_edge(v, u)
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color=((("#ffffff" if dark else NAVY)) if mutual else ec),
                                    lw=2.4 if mutual else 0.7,
                                    alpha=0.95 if mutual else (0.28 if dark else 0.35), shrinkA=14, shrinkB=14,
                                    mutation_scale=9, connectionstyle="arc3,rad=0.08"))
    for w in nodes:
        x, y = pos[w]; c = COL[layer(w)]
        ax.scatter([x], [y], s=520, color=c, zorder=3, edgecolors=("#ffffff" if dark else "#ffffff"), linewidths=1.5)
        ax.text(x, y - 0.085, w, ha="center", va="top", fontsize=12.5, style="italic", zorder=4,
                color="#ffffff" if dark else "#0b0b0b", family="DejaVu Sans")
    ax.margins(0.08)
    fig.savefig(fname, dpi=220, bbox_inches="tight", transparent=True); plt.close(fig)


draw("talk_graph_dark.png", True)
draw("talk_graph_light.png", False)
print("legaturi reciproce in exemplu:", sorted({tuple(sorted(e)) for e in G.edges() if G.has_edge(e[1], e[0])}))

# ── one bar per language: share of the Kernel taken by the MinSet (same procedure for all)
XS = json.load(open("../crossling/summary.json", encoding="utf8"))
kr = lambda r, g: 100 * (r[g]["minset_lb_n"] + r[g]["minset_ub_n"]) / 2 / r[g]["kernel_n"]
rows = [(r["language"], (kr(r, "freq") + kr(r, "all")) / 2) for r in XS
        if r["code"] not in ("ro_wikt", "simple", "wordnet")]
rows = [("Romanian (DEX)" if l == "Romanian" else l, v) for l, v in rows]
rows.sort(key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(7.2, 5.4)); fig.patch.set_alpha(0)
for i, (l, v) in enumerate(rows):
    dex = l.startswith("Romanian")
    ax.barh(i, v, color=ORANGE if dex else "#8fb4e3", height=0.68)
    ax.text(v + 0.6, i, f"{v:.0f}%", va="center", fontsize=14, fontweight="bold" if dex else "normal",
            color=ORANGE if dex else "#3b3a37")
ax.set_yticks(range(len(rows))); ax.set_yticklabels([l for l, _ in rows], fontsize=14)
for t in ax.get_yticklabels():
    if t.get_text().startswith("Romanian"): t.set_color(ORANGE); t.set_fontweight("bold")
ax.set_xlim(0, 34); ax.set_xticks([]); [ax.spines[s].set_visible(False) for s in ("top", "right", "bottom")]
ax.spines["left"].set_color("#cfcdc8"); ax.tick_params(axis="y", length=0)
fig.savefig("talk_languages.png", dpi=220, bbox_inches="tight", transparent=True); plt.close(fig)
print("scris talk_graph_dark.png, talk_graph_light.png, talk_languages.png")
