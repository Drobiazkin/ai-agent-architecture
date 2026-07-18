"""Figure: LoRA — a trainable low-rank update on top of frozen weights.

Block diagram: frozen pretrained matrix W0 (d x k) plus the product of two
trainable low-rank matrices B (d x r) and A (r x k) yields the effective
weights W = W0 + BA. Footnote gives the parameter-count arithmetic.
Self-contained: matplotlib + numpy only, DejaVu Sans (matplotlib default).
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ----------------------------------------------------------------------------
# Canvas: original is 1513 x 794 px at 150 dpi. bbox_inches='tight' keeps the
# full axes and adds pad_inches=0.1 (15 px at 150 dpi) on every side, so the
# canvas covers the original's content region [15, 1498] x [15, 779] and the
# tight pad reproduces the outer 15 px margin. Data coordinates below are the
# ORIGINAL image's pixel coordinates (y grows downward).
# ----------------------------------------------------------------------------
W_PX, H_PX = 1513, 794
DPI = 150
PAD = 15  # bbox_inches='tight' default pad_inches=0.1 -> 15 px at 150 dpi

fig = plt.figure(figsize=((W_PX - 2 * PAD) / DPI, (H_PX - 2 * PAD) / DPI))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(PAD, W_PX - PAD)
ax.set_ylim(H_PX - PAD, PAD)
ax.axis("off")

# ----------------------------------------------------------------------------
# Palette (sampled from the original figure; Tailwind-style hues)
# ----------------------------------------------------------------------------
SLATE_800 = "#1E293B"   # W0 glyph
SLATE_700 = "#334155"   # plus/times signs, caption, arrow, footnote
SLATE_600 = "#475569"   # "pretrained weights", "frozen (d x k)"
W0_FILL, W0_EDGE = "#C4CCD8", "#9AA1AC"
B_FILL, B_EDGE = "#467AEE", "#405DBB"
A_FILL, A_EDGE = "#E14646", "#A83D3D"
W_FILL, W_EDGE = "#B3DFD1", "#B3D6CC"
RED_800 = "#991B1B"     # "r x k"
BLUE_800 = "#1E40AF"    # "d x r"
EMERALD_800 = "#065F46"  # W glyph
EMERALD_700 = "#047857"  # "W = W0 + BA"

# ----------------------------------------------------------------------------
# Title
# ----------------------------------------------------------------------------
ax.text(756.5, 15, "LoRA: a trainable low-rank update on top of frozen weights",
        ha="center", va="top", fontsize=15, fontweight="bold", color="black")

# ----------------------------------------------------------------------------
# Blocks (pixel geometry measured off the original)
# ----------------------------------------------------------------------------
BOX_TOP, BOX_H = 177, 390
LW = 1.0  # 2 px at 150 dpi
GLYPH_Y = 373  # vertical center of the large matrix glyphs

# W0 — frozen pretrained weights
ax.text(89, 118, "pretrained weights", ha="left", va="center",
        fontsize=11, style="italic", color=SLATE_600)
ax.add_patch(Rectangle((60, BOX_TOP), 296, BOX_H,
                       facecolor=W0_FILL, edgecolor=W0_EDGE, linewidth=LW))
ax.text(208, GLYPH_Y, "W₀", ha="center", va="center",
        fontsize=20, fontweight="bold", color=SLATE_800)
ax.text(207.5, 606.5, "frozen (d × k)", ha="center", va="center",
        fontsize=10.5, color=SLATE_600)

# +
ax.text(430.5, 373.5, "+", ha="center", va="center",
        fontsize=26, fontweight="bold", color=SLATE_700)

# B — tall thin trainable matrix
ax.add_patch(Rectangle((503, BOX_TOP), 62, BOX_H,
                       facecolor=B_FILL, edgecolor=B_EDGE, linewidth=LW))
ax.text(534, GLYPH_Y, "B", ha="center", va="center",
        fontsize=16.5, fontweight="bold", color="white")
ax.text(533.5, 605, "d × r", ha="center", va="center",
        fontsize=10.5, color=BLUE_800)

# x
ax.text(618, 374, "×", ha="center", va="center",
        fontsize=20, fontweight="bold", color=SLATE_700)

# A — wide flat trainable matrix
ax.add_patch(Rectangle((671, BOX_TOP), 297, 80,
                       facecolor=A_FILL, edgecolor=A_EDGE, linewidth=LW))
ax.text(819.5, 219, "A", ha="center", va="center",
        fontsize=16.5, fontweight="bold", color="white")
ax.text(820, 297, "r × k", ha="center", va="center",
        fontsize=10.5, color=RED_800)
ax.text(820, 416, "trainable matrices\nof rank r ≪ d,k",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color=SLATE_700, linespacing=1.6)

# arrow ->
ax.annotate("", xy=(1108, 372), xytext=(1010, 372),
            arrowprops=dict(arrowstyle="->", color=SLATE_700, linewidth=1.6,
                            mutation_scale=16, shrinkA=0, shrinkB=0))

# W — merged effective weights
ax.add_patch(Rectangle((1141, BOX_TOP), 297, BOX_H,
                       facecolor=W_FILL, edgecolor=W_EDGE, linewidth=LW))
ax.text(1289.5, GLYPH_Y, "W", ha="center", va="center",
        fontsize=20, fontweight="bold", color=EMERALD_800)
ax.text(1290, 605, "W = W₀ + BA", ha="center", va="center",
        fontsize=11, fontweight="bold", color=EMERALD_700)

# ----------------------------------------------------------------------------
# Footnote
# ----------------------------------------------------------------------------
ax.text(16, 700,
        "Trainable parameters: full fine-tuning d·k  →  LoRA r·(d + k).  "
        "Example: d = k = 4096, r = 8: 16.8M → 65.5K (≈256× fewer).",
        ha="left", va="top", fontsize=11, color=SLATE_700)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_lora.png", dpi=150, bbox_inches='tight')
