"""Figure: the third scaling axis — test-time compute.

Schematic log-linear quality curve (shaped after OpenAI o1 / DeepSeek-R1
result plots) showing that a reasoning model buys quality with per-answer
compute, versus the same model without reasoning and a larger base model.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# ---- palette (sampled from the original figure) ----
BLUE = "#1F6FF5"      # reasoning-model curve
PURPLE = "#7A3FF0"    # same model, no reasoning
RED = "#E02020"       # larger base model
SLATE = "#33475B"     # marker + annotation
GRID = "#E7E7E7"
SPINE = "#383838"
FOOT = "#7A8A9A"      # footnote

fig, ax = plt.subplots(figsize=(9.56, 6.02))
fig.subplots_adjust(left=0.085, right=0.985, top=0.868, bottom=0.165)

# ---- data ----
x = np.logspace(0, 3, 300)
quality = 55.0 + 14.0 * np.log10(x)  # +14 quality points per decade of compute

ax.set_xscale("log")
ax.plot(
    x, quality, color=BLUE, lw=3.4, solid_capstyle="round", zorder=3,
    label="Reasoning model: longer reasoning / more samples",
)
ax.axhline(
    57, color=PURPLE, lw=2.9, ls="--", zorder=2,
    label="Same model, answer without reasoning",
)
ax.axhline(
    72, color=RED, lw=2.9, ls=":", zorder=4,
    label="Larger base model (scaling up N·D, no reasoning)",
)

# ---- marker at the training-vs-inference budget crossover ----
x_star = 10 ** (17.0 / 14.0)  # blue curve crosses quality = 72 here (~16.4)
ax.plot([x_star], [72], marker="o", ms=9, color=SLATE, zorder=5)

ax.annotate(
    "the same quality level is reachable\nwith two budgets: training OR inference",
    xy=(x_star, 72.6),
    xytext=(14.5, 87.3),
    ha="center", va="bottom",
    fontsize=13.5, color=SLATE, linespacing=1.35,
    arrowprops=dict(
        arrowstyle="-|>", color=SLATE, lw=1.8,
        connectionstyle="arc3,rad=0.0", shrinkB=7, mutation_scale=18,
    ),
    zorder=6,
)

# ---- axes cosmetics ----
ax.set_ylim(48, 100)
ax.set_yticks([50, 60, 70, 80, 90, 100])
ax.grid(True, which="major", color=GRID, lw=1.0)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(SPINE)
    ax.spines[side].set_linewidth(1.0)
ax.tick_params(axis="both", which="major", labelsize=9.5, colors=SPINE)
ax.tick_params(axis="x", which="minor", colors=SPINE)
for lbl in ax.get_xticklabels() + ax.get_yticklabels():
    lbl.set_color("black")

ax.set_xlabel("Compute per answer (log scale, relative units)", fontsize=14.5)
ax.set_ylabel("Quality on reasoning tasks (arb. units)", fontsize=14.5)
ax.set_title(
    "The third scaling axis: quality can be bought\n"
    "with compute at inference time (test-time compute)",
    fontsize=16, fontweight="bold", pad=12,
)

leg = ax.legend(loc="lower right", fontsize=11.5, framealpha=1.0)
leg.get_frame().set_edgecolor("#CCCCCC")

fig.text(
    0.5, 0.012,
    "Schematic, shaped after the OpenAI o1 (2024) and DeepSeek-R1 (2025) results; axes are notional."
    " Choosing between the axes\nis a matter of deployment economics: high-volume cheap inference"
    " versus rare, expensive answers (§13.8, §23.5).",
    ha="center", va="bottom", fontsize=10.5, color=FOOT, linespacing=1.45,
)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_test_time_compute.png", dpi=150, bbox_inches='tight')
