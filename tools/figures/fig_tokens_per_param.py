"""Figure: Tokens per parameter — three training philosophies.

Horizontal log-scale bar chart comparing tokens-per-parameter ratios of
GPT-3 (undertrained), Chinchilla-optimal, and LLaMA-style over-training,
with a dashed reference line at the Chinchilla optimum (~20).

English-edition recreation of the original figure (matplotlib + numpy only).
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------- palette
RED = "#e14646"       # GPT-3: undertrained
PURPLE = "#8f57ef"    # Chinchilla optimum
GREEN = "#2aa57f"     # LLaMA-style over-training
VLINE = "#ab84ef"     # dashed reference line at the Chinchilla optimum
GRID = "#f3f3f3"      # very light vertical gridlines
VALUE_INK = "#374151" # bold value labels next to bar ends
FOOT_INK = "#6b7280"  # gray footnote

# ------------------------------------------------------------------ data
labels = [
    "LLaMA-style\n(inference-optimal,\nover-training)",  # y = 0 (bottom)
    "Chinchilla optimum\n(training-optimal)",            # y = 1
    "GPT-3 (2020)\nundertrained",                        # y = 2 (top)
]
values = np.array([140.0, 20.0, 1.7])
colors = [GREEN, PURPLE, RED]
value_tags = ["~140", "~20", "~1.7"]

# ---------------------------------------------------------------- figure
fig, ax = plt.subplots(figsize=(10.75, 3.6))

y = np.arange(len(values))
ax.barh(y, values, height=0.55, color=colors, zorder=3)

ax.set_xscale("log")
ax.set_xlim(1, 400)

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=10)

# Vertical gridlines at both major and minor log ticks, behind the bars.
ax.grid(axis="x", which="both", color=GRID, linewidth=1.0, zorder=0)
ax.set_axisbelow(True)

# Dashed reference line at the Chinchilla optimum (~20), above the bars.
ax.axvline(20, color=VLINE, linestyle="--", linewidth=1.5, zorder=4)

# Value labels just right of each bar end.
for yi, v, tag in zip(y, values, value_tags):
    ax.text(v * 1.12, yi, tag, va="center", ha="left",
            fontsize=12, fontweight="bold", color=VALUE_INK, zorder=5)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.set_xlabel("Tokens per parameter (log scale)", fontsize=12.5)
ax.set_title("How Many Tokens per Parameter: Three Training Philosophies",
             fontsize=13, fontweight="bold", pad=12)

footnote = (
    "The Chinchilla optimum (~20) minimizes TRAINING cost; for deployment, "
    "it pays to over-train\na smaller model on more tokens, cutting "
    "INFERENCE cost. The exact optimum is debated (~10–20)."
)
fig.text(0.5, -0.02, footnote, ha="center", va="top",
         fontsize=10.5, color=FOOT_INK, linespacing=1.4)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_tokens_per_param.png", dpi=150, bbox_inches='tight')
