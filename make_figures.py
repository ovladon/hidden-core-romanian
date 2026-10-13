#!/usr/bin/env python3
"""Figurile lucrarii si ale prezentarii, din results/results.json (paleta validata, fara axa dubla)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = json.load(open("results/results.json", encoding="utf8"))
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
GRAY, INK, INK2, GRID, SURF = "#b9b8b3", "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF})


def save(fig, name):
    for ext in ("png", "svg", "pdf"):
        fig.savefig(f"figures/{name}.{ext}", dpi=220, bbox_inches="tight")
    plt.close(fig)


ai = R["regimes"]["ai"]; N = R["data"]["headwords"]
lb = ai.get("minset_lb_ilp", ai["minset_lb"]); ub = ai["minset_ub"]

# --- Fig. 1: cat de mare e nucleul: DEX, WordNet procesat la fel, dictionarele englezesti publicate -----------
import sys as _s; _s.path.insert(0, ".")
from calib import calib
CB = calib(R)
fig, ax = plt.subplots(figsize=(6.6, 2.75))
rows = [("Kernel", (100 * ai["kernel"] / N,) * 2, CB["wn_k"], (7, 12)),
        ("MinSet", (100 * lb / N, 100 * ub / N), CB["wn_m"], (1, 1))]
H = 0.24
for i, (name, dex, wn, eng) in enumerate(rows):
    y = 1.1 - 1.1 * i
    for off, (lo, hi), col, lab in ((H, dex, BLUE, "DEX (this study)"), (0, wn, ORANGE, "English WordNet, same procedure"),
                                    (-H, eng, GRAY, "English dictionaries (Vincent-Lamarre et al. 2016)")):
        ax.barh(y + off, lo, height=H * 0.86, color=col, zorder=2)
        if hi > lo: ax.barh(y + off, hi - lo, left=lo, height=H * 0.86, color=col, alpha=0.45, zorder=2)
        txt = f"{lo:.1f}%" if hi == lo else (f"{lo:.1f}–{hi:.1f}%" if col != GRAY else f"{lo:.0f}–{hi:.0f}%")
        if col == GRAY and hi == lo: txt = f"≈{lo:.0f}%"
        ax.text(hi + 0.6, y + off, txt, va="center", color=INK if col == BLUE else INK2, fontsize=8.5)
ax.set_yticks([1.1, 0]); ax.set_yticklabels(["Kernel", "MinSet"])
ax.set_xlim(0, 45); ax.set_xlabel("share of the dictionary's headwords (%)")
ax.grid(axis="x", color=GRID, zorder=0); ax.tick_params(length=0)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=BLUE, label="DEX (this study)"), Patch(color=ORANGE, label="English WordNet, same procedure"),
                   Patch(color=GRAY, label="English dictionaries (Vincent-Lamarre et al. 2016)")],
          loc="lower right", frameon=False, fontsize=8)
save(fig, "fig1_size")

# --- Fig. 2: liste de experti in Kernel si in MinSet, fata de asteptarea intamplatoare ---------
lists = [("Swadesh list", R["swadesh"]["layers"]), ("Graur: most certain", R["graur"]["core"]),
         ("Graur: middle circle", R["graur"]["middle"]), ("Graur: maximal circle", R["graur"]["maximal"])]
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
for ax, layer in zip(axes, ("Kernel", "MinSet")):
    vals = [100 * d[layer]["rate"] for _, d in lists]
    exp = 100 * lists[0][1][layer]["expected"]
    ys = list(range(len(lists)))[::-1]
    ax.barh(ys, vals, height=0.6, color=BLUE, zorder=2)
    for y, v in zip(ys, vals):
        ax.text(v + 1.5, y, f"{v:.0f}%", va="center", fontsize=9, color=INK)
    ax.axvline(exp, color=INK2, ls="--", lw=1.2, zorder=3)
    ax.text(exp + 1.2, len(lists) - 0.42, f"chance: {exp:.0f}%", fontsize=8.5, color=INK2)
    ax.set_title(f"…inside the {layer}", fontsize=10, color=INK, loc="left")
    ax.set_xlim(0, 112); ax.set_ylim(-0.5, len(lists) - 0.2)
    ax.grid(axis="x", color=GRID, zorder=0); ax.tick_params(length=0)
    ax.set_xlabel("% of the list")
axes[0].set_yticks(list(range(len(lists)))[::-1]); axes[0].set_yticklabels([n for n, _ in lists])
save(fig, "fig2_enrichment")

# --- Fig. 3: robustete la modul de lematizare ------------------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 2.5))
names = [("freq", "frequency rule"), ("ai", "LLM (main)"), ("all", "all candidates")]
for i, (k, lab) in enumerate(names):
    r = R["regimes"][k]; y = 2 - i
    kv = 100 * r["kernel"] / N
    l = 100 * r.get("minset_lb_ilp", r["minset_lb"]) / N; u = 100 * r["minset_ub"] / N
    ax.plot([kv], [y], "o", ms=8, color=BLUE, zorder=3)
    ax.plot([l, u], [y, y], lw=6, color=ORANGE, solid_capstyle="round", zorder=3)
    ax.text(kv + 0.8, y + 0.22, f"Kernel {kv:.1f}%", fontsize=8.5, color=INK)
    ax.text(u + 0.8, y - 0.05, f"MinSet {l:.1f}–{u:.1f}%", fontsize=8.5, color=INK, va="center")
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([lab for _, lab in names])
ax.set_xlim(0, 45); ax.set_ylim(-0.6, 2.6); ax.set_xlabel("share of the dictionary's headwords (%)")
ax.grid(axis="x", color=GRID, zorder=0); ax.tick_params(length=0)
save(fig, "fig3_robustness")

# --- Fig. 4: etimologia: lista lui Graur vs vocabularul definitoriu ------------------------
cats = [("latin", "Latin", BLUE), ("slav", "Slavic", ORANGE), ("francez", "French", AQUA),
        ("formație internă", "formed in Romanian", YELLOW)]
sets = [("Graur's list (1954)", R["etymology"]["graur_list"]), ("1,419 most-used\ndefining words", R["etymology"]["top1419_definers"])]
fig, ax = plt.subplots(figsize=(7.2, 2.6))
handles = []
for i, (lab, comp) in enumerate(sets):
    y = 1 - i; left = 0
    for key, name, col in cats:
        w = 100 * comp.get(key, 0)
        b = ax.barh(y, w - 0.4, left=left, height=0.55, color=col, zorder=2, label=name if i == 0 else None)
        if w >= 4: ax.text(left + w / 2, y, f"{w:.0f}%", ha="center", va="center", fontsize=9, color=INK)
        left += w
    rest = 100 - left
    ax.barh(y, rest, left=left, height=0.55, color=GRID, zorder=2, label="other / unclassified" if i == 0 else None)
    ax.text(left + rest / 2, y, f"{rest:.0f}%", ha="center", va="center", fontsize=9, color=INK2)
ax.set_yticks([1, 0]); ax.set_yticklabels([s for s, _ in sets]); ax.set_xlim(0, 100)
ax.set_xticks([]); ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(False); ax.tick_params(length=0)
ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.45, -0.02), frameon=False, fontsize=8.5,
          handlelength=1.2, columnspacing=1.2)
save(fig, "fig4_etymology")
print("figuri scrise in figures/")
