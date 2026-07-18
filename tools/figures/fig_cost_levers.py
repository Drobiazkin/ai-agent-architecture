"""Figure: cost-reduction levers for an LLM system (each lever in isolation).

Horizontal range bars showing the typical cost-reduction percentage each
lever delivers on its own; Batch API is a point estimate (~50%).
Recreated from the original edition with all labels in US English.
Requires only matplotlib + numpy (DejaVu Sans, matplotlib's default font).
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# --- Data: (label, low %, high %, color); None high => point estimate ------
levers = [
    ("Prefix caching\n(on cached tokens)",      50, 90,   "#467AEE"),
    ("Semantic caching\n(on cache hits)",       30, 100,  "#2DA1BD"),
    ("Model routing\n(easy → cheaper models)", 40, 70, "#8F57EF"),
    ("Context compaction\n(fewer tokens)",      50, 70,   "#2AA57F"),
    ("Batch API\n(when latency permits)",       50, None, "#D97706"),
]

GRAY_NOTE = "#6B7280"   # footnote ink
INK = "#2A2A2A"         # spines / ticks
GRID = "#F1F1F1"        # vertical gridlines
BAR_H = 0.55            # bar height in category units

fig, ax = plt.subplots(figsize=(10.35, 5.5))
fig.subplots_adjust(left=0.228, right=0.985, top=0.928, bottom=0.165)

y_positions = np.arange(len(levers))[::-1]  # first lever on top

# gridlines behind the bars
ax.set_axisbelow(True)
ax.grid(axis="x", color=GRID, linewidth=1.0)

for (label, lo, hi, color), y in zip(levers, y_positions):
    if hi is not None:
        ax.barh(y, hi - lo, left=lo, height=BAR_H, color=color, zorder=3)
        ax.text((lo + hi) / 2, y, f"{lo}–{hi}%",
                ha="center", va="center", color="white",
                fontsize=14, fontweight="bold", zorder=4)
    else:
        ax.plot(lo, y, "o", markersize=10.5, color=color, zorder=3)
        ax.text(lo + 1.8, y, f"~{lo}%",
                ha="left", va="center", color="black",
                fontsize=14, fontweight="bold", zorder=4)

ax.set_yticks(y_positions)
ax.set_yticklabels([lv[0] for lv in levers], fontsize=13)
ax.set_xlim(0, 105)
ax.set_ylim(-0.5, len(levers) - 0.5)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.tick_params(axis="both", colors=INK, labelcolor="black", labelsize=13)

ax.set_xlabel("Cost reduction, %", fontsize=15)
ax.set_title("Cost-Reduction Levers for an LLM System (Taken Individually)",
             fontsize=16, fontweight="bold", pad=14)

for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(INK)

fig.text(0.5, 0.052,
         "Ranges are drawn from industry reports (2025–2026); "
         "the levers apply to different parts of the cost and compound.",
         ha="center", va="center", fontsize=12.5, color=GRAY_NOTE)
fig.text(0.5, 0.014,
         "Applied together, they deliver roughly a 70–85% reduction "
         "with no loss of output quality.",
         ha="center", va="center", fontsize=12.5, color=GRAY_NOTE)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_cost_levers.png",
            dpi=150, bbox_inches='tight')
