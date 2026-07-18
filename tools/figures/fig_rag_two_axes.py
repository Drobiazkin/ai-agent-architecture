"""Figure: two orthogonal axes of RAG quality (2x2 quadrant chart).

Recreates fig_rag_two_axes for the English edition. A quadrant diagram:
retrieval quality (x) vs. faithfulness (y), one colored rounded box per
combination, arrow axes, and a footnote on measuring the axes separately.
Only matplotlib + numpy; DejaVu Sans (matplotlib default).
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ----- palette (sampled from the original figure; Tailwind hues) -----
AMBER = "#FEF3C7"     # top-left fill
GREEN = "#DCFCE7"     # top-right fill
RED = "#FEE2E2"       # bottom-left fill
ORANGE = "#FFEDD5"    # bottom-right fill
BORDER = "#9CA3AF"    # rounded-box border
DARK = "#1F2937"      # quadrant titles / axis labels
ARROW = "#374151"     # axis arrows
SUBTLE = "#4B5563"    # quadrant subtitles
MUTED = "#6B7280"     # tick words + footnote

fig, ax = plt.subplots(figsize=(8.35, 7.35))
ax.set_xlim(-0.2, 10.3)
ax.set_ylim(-0.2, 10.3)
ax.set_aspect("equal")
ax.axis("off")

# ----- quadrant boxes (geometry read off the original, 0..10 data units) -----
boxes = [
    # (x, y, w, h, fill)
    (0.11, 5.02, 4.67, 4.66, AMBER),    # top-left
    (4.95, 5.02, 4.70, 4.66, GREEN),    # top-right
    (0.11, 0.11, 4.67, 4.69, RED),      # bottom-left
    (4.95, 0.11, 4.70, 4.69, ORANGE),   # bottom-right
]
for x, y, w, h, fill in boxes:
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=0.15",
            facecolor=fill, edgecolor=BORDER, linewidth=1.4, zorder=1,
        )
    )

# ----- quadrant titles and explanations -----
LX, RX = 2.44, 7.30          # column centers
TT, TS = 7.93, 6.56          # top row: title / subtitle y
BT, BS = 3.03, 1.68          # bottom row: title / subtitle y

quads = [
    (LX, TT, TS,
     "Honest retelling\nof the wrong context",
     "a retrieval problem\nmasked by a confident tone"),
    (RX, TT, TS,
     "The ideal",
     "retrieved the right context\nand used it correctly"),
    (LX, BT, BS,
     "Everything is wrong",
     "wrong context and\nhallucination on top of it"),
    (RX, BT, BS,
     "Hallucination despite\ngood context",
     "a generation problem:\nright context, wrong answer"),
]
for cx, ty, sy, head, sub in quads:
    ax.text(cx, ty, head, ha="center", va="center",
            fontsize=13.5, fontweight="bold", color=DARK, zorder=2)
    ax.text(cx, sy, sub, ha="center", va="center",
            fontsize=11, color=SUBTLE, linespacing=1.45, zorder=2)

# ----- axis arrows -----
arrow_kw = dict(arrowstyle="-|>", color=ARROW, linewidth=1.6,
                mutation_scale=16, shrinkA=0, shrinkB=0)
ax.annotate("", xy=(0, 10.0), xytext=(0, 0), arrowprops=arrow_kw)
ax.annotate("", xy=(10.0, 0), xytext=(0, 0), arrowprops=arrow_kw)

# ----- tick words -----
ax.text(LX, -0.28, "poor", ha="center", va="top", fontsize=11.5, color=MUTED)
ax.text(RX, -0.28, "good", ha="center", va="top", fontsize=11.5, color=MUTED)
ax.text(-0.35, 7.40, "high", ha="center", va="center", rotation=90,
        fontsize=11.5, color=MUTED)
ax.text(-0.35, 2.50, "low", ha="center", va="center", rotation=90,
        fontsize=11.5, color=MUTED)

# ----- axis labels -----
ax.text(4.88, -0.80, "Retrieval quality  →  (did we fetch the right thing)",
        ha="center", va="top", fontsize=13.5, fontweight="bold", color=DARK)
ax.text(-0.80, 4.90, "Faithfulness  →  (did we use it correctly)",
        ha="center", va="center", rotation=90,
        fontsize=13.5, fontweight="bold", color=DARK)

# ----- title -----
ax.text(4.88, 10.95,
        "Two orthogonal axes of RAG quality: all four combinations are real",
        ha="center", va="center", fontsize=15.5, fontweight="bold",
        color="#111827")

# ----- footnote -----
ax.text(-1.97, -1.55,
        "The axes are independent and measured separately (§6.7, §9.2): "
        "the metric tells you which axis to fix.",
        ha="left", va="top", fontsize=10, color=MUTED)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_rag_two_axes.png", dpi=150, bbox_inches='tight')
