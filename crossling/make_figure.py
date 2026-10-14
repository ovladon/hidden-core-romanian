#!/usr/bin/env python3
"""Figura comparatiei translingvistice: MinSet/Kernel si perechi reciproce la 1.000 de cuvinte-titlu, pe dictionar."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, GRAY, INK, INK2, GRID, SURF = "#2a78d6", "#eb6834", "#b9b8b3", "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
rows = json.load(open("crossling/summary.json", encoding="utf8"))
for r in rows:
    f, a = r["freq"], r.get("all", r["freq"])
    r["ratio"] = (100 * (f["minset_lb_n"] + f["minset_ub_n"]) / 2 / f["kernel_n"],
                  100 * (a["minset_lb_n"] + a["minset_ub_n"]) / 2 / a["kernel_n"])
    r["label"] = f"{r['language']} – {r['dictionary']}" if r["dictionary"] != "Wiktionary" else r["language"]
rows.sort(key=lambda r: sum(r["ratio"]))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 0.32 * len(rows) + 1.0), sharey=True)
for i, r in enumerate(rows):
    col = BLUE if r["language"] == "Romanian" else GRAY
    lo, hi = sorted(r["ratio"])
    ax1.plot([lo, hi], [i, i], color=col, lw=3, solid_capstyle="round", zorder=2)
    ax1.text(hi + 0.6, i, f"{lo:.0f}%" if round(lo) == round(hi) else f"{lo:.0f}–{hi:.0f}%", va="center", fontsize=8, color=INK if col == BLUE else INK2)
    ax2.barh(i, r["reciprocal_pairs_per_1000"], height=0.6, color=col, zorder=2)
    ax2.text(r["reciprocal_pairs_per_1000"] + 1.5, i, f"{r['reciprocal_pairs_per_1000']:.0f}", va="center", fontsize=8,
             color=INK if col == BLUE else INK2)
ax1.set_yticks(range(len(rows))); ax1.set_yticklabels([r["label"] for r in rows])
ax1.set_xlabel("MinSet as % of the Kernel\n(range over the two regimes)"); ax1.set_xlim(0, 40)
ax2.set_xlabel("reciprocally defined pairs\nper 1,000 headwords"); ax2.set_xlim(0, 150)
for ax in (ax1, ax2):
    ax.grid(axis="x", color=GRID, zorder=0); ax.tick_params(length=0)
fig.tight_layout()
for ext in ("png", "pdf", "svg"):
    fig.savefig(f"crossling/fig_crossling.{ext}", dpi=220, bbox_inches="tight")
    fig.savefig(f"figures/fig5_crossling.{ext}", dpi=220, bbox_inches="tight")
print("scris crossling/fig_crossling.png")
