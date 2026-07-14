"""Figure: "dark knowledge" — soft targets vs. hard label (knowledge distillation).

Grouped bar chart contrasting a one-hot hard label with a teacher's softened
(T > 1) next-token distribution for the context "The fluffy ___".
Self-contained: matplotlib + numpy only, DejaVu Sans (matplotlib default).
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
categories = ["cat", "kitten", "dog", "tiger", "table"]
hard = np.array([1.0, 0.0, 0.0, 0.0, 0.0])          # one-hot hard label
soft = np.array([0.60, 0.20, 0.12, 0.06, 0.02])      # teacher softmax, T > 1

x = np.arange(len(categories))
width = 0.38

# ----------------------------------------------------------------------------
# Palette (sampled from the original figure)
# ----------------------------------------------------------------------------
GRAY_BAR = "#A6ACB7"
BLUE_BAR = "#3B72ED"
BLUE_LABEL = "#1E40AF"
GRAY_LABEL = "#6B7280"
ANNOT_TEXT = "#374151"
ARROW = "#9CA3AF"
GRID = "#F3F3F3"
SPINE = "#2A2A2A"
FOOTNOTE = "#6B7280"

# ----------------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.23, 5.42))
fig.subplots_adjust(left=0.075, right=0.985, top=0.845, bottom=0.155)

ax.set_axisbelow(True)
ax.grid(axis="y", color=GRID, linewidth=1.3)

ax.bar(x - width / 2, hard, width, color=GRAY_BAR, label="Hard label (one-hot)")
ax.bar(x + width / 2, soft, width, color=BLUE_BAR,
       label="Teacher’s soft targets (softmax, T > 1)")

# Value labels ---------------------------------------------------------------
for xi, v in zip(x, hard):
    ax.text(xi - width / 2, v + 0.015, f"{v:g}", ha="center", va="bottom",
            fontsize=12, color=GRAY_LABEL)
for xi, v in zip(x, soft):
    ax.text(xi + width / 2, v + 0.015, f"{v:.2f}", ha="center", va="bottom",
            fontsize=12, fontweight="bold", color=BLUE_LABEL)

# Axes cosmetics -------------------------------------------------------------
ax.set_ylim(0, 1.1)
ax.set_yticks(np.arange(0, 1.01, 0.2))
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=15)
ax.tick_params(axis="x", length=0, pad=8)
ax.tick_params(axis="y", labelsize=12, colors=SPINE)
ax.set_ylabel("Next-token probability", fontsize=14)

for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(SPINE)
    ax.spines[side].set_linewidth(1.2)

ax.set_title(
    "“Dark knowledge”: soft targets carry more information "
    "than a hard label\n(context: “The fluffy ___”)",
    fontsize=16, fontweight="bold", pad=14,
)

# Annotation -----------------------------------------------------------------
ax.annotate(
    "the teacher “knows” that kitten/dog/tiger\n"
    "are closer to cat than table — that similarity\n"
    "structure is the training signal for the student",
    xy=(1 + width, 0.21), xytext=(2.2, 0.835),
    ha="left", va="top", fontsize=12, color=ANNOT_TEXT, linespacing=1.45,
    arrowprops=dict(arrowstyle="->", color=ARROW, linewidth=1.8,
                    shrinkA=8, shrinkB=2),
)

# Legend ---------------------------------------------------------------------
ax.legend(loc="upper right", fontsize=13, frameon=True,
          edgecolor="#D6D6D6", framealpha=1.0, borderpad=0.6)

# Footnote -------------------------------------------------------------------
fig.text(
    0.5, 0.012,
    "A hard label conveys only “the correct answer is cat.” "
    "The teacher’s soft distribution (Hinton et al., 2015) adds the\n"
    "relative probabilities of the other options — more information "
    "per example, which is exactly what transfers to the student.",
    ha="center", va="bottom", fontsize=11.5, color=FOOTNOTE, linespacing=1.4,
)

fig.savefig(r'/Users/aleksandrdrobiazkin/IdeaProjects/ai-agent-architecture/book/images/fig_distillation.png', dpi=150, bbox_inches='tight')
