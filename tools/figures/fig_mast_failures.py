"""MAST failure taxonomy: distribution of multi-agent system failures by category.

Horizontal bar chart of the three top-level failure categories from
Cemri et al. (2025), "Why Do Multi-Agent LLM Systems Fail?" (MAST).
Data: 41.77% specification and system design, 36.94% inter-agent
misalignment, 21.30% task verification and termination.
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# --- Data (exact category shares from the MAST paper) ---------------------
categories = [
    "Specification and\nsystem design",
    "Inter-agent\nmisalignment",
    "Task verification\nand termination",
]
values = np.array([41.77, 36.94, 21.30])
bar_labels = ["42%", "37%", "21%"]
bar_colors = ["#467aee", "#8f57ef", "#2da1bd"]

LABEL_COLOR = "#374151"   # bar value labels
FOOTNOTE_COLOR = "#6b7280"
GRID_COLOR = "#f1f1f1"

# --- Figure ----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 4.62))
fig.subplots_adjust(left=0.19, right=0.97, top=0.90, bottom=0.24)

y = np.arange(len(categories))
ax.barh(y, values, height=0.6, color=bar_colors, zorder=3)
ax.invert_yaxis()  # first category on top

ax.set_xlim(0, 50)
ax.set_xticks(np.arange(0, 51, 10))
ax.set_yticks(y)
ax.set_yticklabels(categories, fontsize=14)
ax.tick_params(axis="x", labelsize=14)

ax.set_xlabel("Share of failures, %", fontsize=14)
ax.set_title(
    "MAST: Distribution of Multi-Agent System Failures by Category",
    fontsize=16,
    fontweight="bold",
    pad=14,
)

# Faint vertical gridlines behind the bars
ax.xaxis.grid(True, color=GRID_COLOR, linewidth=1.0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Value labels just past the bar ends
for yi, v, lab in zip(y, values, bar_labels):
    ax.annotate(
        lab,
        xy=(v, yi),
        xytext=(9, 0),
        textcoords="offset points",
        va="center",
        ha="left",
        fontsize=14,
        fontweight="bold",
        color=LABEL_COLOR,
    )

# Two-line footnote centered under the figure
footnote = (
    "Cemri et al. (2025), 14 failure modes across 3 categories "
    "(7 frameworks, 1,600+ traces, κ=0.88).\n"
    "Failures are predominantly design flaws, not artifacts of "
    "base-model quality."
)
fig.text(
    0.5,
    0.015,
    footnote,
    ha="center",
    va="bottom",
    fontsize=11.5,
    color=FOOTNOTE_COLOR,
    linespacing=1.4,
)

fig.savefig(
    Path(__file__).resolve().parents[2] / "book" / "images" / "fig_mast_failures.png",
    dpi=150,
    bbox_inches="tight",
)
