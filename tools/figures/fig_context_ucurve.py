"""Figure: "Lost in the middle" — answer accuracy vs. position of the
relevant passage in the context window (schematic, after Liu et al. 2023).

Self-contained: matplotlib + numpy only, DejaVu Sans (matplotlib default).
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------- palette
BLUE = "#2563eb"    # main curve + primacy/recency annotations
RED = "#dc2626"     # dip annotation + shaded degradation band
GRAY = "#6b7280"    # closed-book baseline + footnote
GRID = "#f1f1f1"    # gridlines

# ---------------------------------------------------------------- data
# U-shaped accuracy curve: parabola anchored at
#   f(0) = 0.97 (primacy), min f(h) = 0.52, f(1) = 0.91 (recency)
H_MIN = 0.518       # position of the trough (slightly right of center)
K_MIN = 0.52        # accuracy at the trough
A = (0.97 - K_MIN) / H_MIN**2

x = np.linspace(0.0, 1.0, 400)
acc = K_MIN + A * (x - H_MIN) ** 2

CLOSED_BOOK = 0.56  # closed-book (no-context) accuracy level

# ---------------------------------------------------------------- figure
fig, ax = plt.subplots(figsize=(11.77, 5.36), dpi=150)

ax.set_xlim(0.0, 1.0)  # curve starts flush with the y-axis spine, as in the original
ax.set_ylim(0.2, 1.0)

# grid under everything; the original has no vertical gridline at x = 0
ax.set_axisbelow(True)
ax.grid(True, color=GRID, linewidth=1.0)
ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
ax.set_xticklabels(["beginning", "¼", "middle", "¾", "end"],
                   fontsize=13.5)
ax.set_yticks(np.arange(0.2, 1.01, 0.1))
ax.tick_params(axis="y", labelsize=13.5)
fig.canvas.draw()  # materialize gridlines before hiding the x=0 one
ax.xaxis.get_gridlines()[0].set_visible(False)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# shaded degradation band: from y = 0.4 up to the curve, mid-context only
band = (x >= 0.152) & (x <= 0.878)
ax.fill_between(x, 0.4, acc, where=band, color=RED, alpha=0.06, linewidth=0)

# closed-book baseline
ax.axhline(CLOSED_BOOK, color=GRAY, linewidth=1.3, linestyle="--")
ax.text(0.5, CLOSED_BOOK + 0.008, "closed-book baseline (no context)",
        ha="center", va="bottom", fontsize=13, color=GRAY)

# main curve
ax.plot(x, acc, color=BLUE, linewidth=3.5, solid_capstyle="round")

# annotations: primacy / recency (blue), mid-context dip (red)
ax.annotate("beginning\n(primacy)",
            xy=(0.02, K_MIN + A * (0.02 - H_MIN) ** 2),
            xytext=(0.075, 0.952), fontsize=13, color=BLUE,
            ha="left", va="top",
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5,
                            connectionstyle="arc3,rad=-0.15"))
ax.annotate("end\n(recency)",
            xy=(0.978, K_MIN + A * (0.978 - H_MIN) ** 2),
            xytext=(0.80, 0.952), fontsize=13, color=BLUE,
            ha="left", va="top",
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5,
                            connectionstyle="arc3,rad=0.15"))
ax.annotate("the dip in the middle\n(“lost in the middle”)",
            xy=(0.5, 0.514),
            xytext=(0.5, 0.353), fontsize=13, color=RED,
            ha="center", va="top",
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.8))

# titles and labels
ax.set_title("“Lost in the middle”: accuracy depends on"
             " the position of the relevant passage",
             fontsize=16, fontweight="bold", pad=12)
ax.set_xlabel("Position of the relevant passage in the context", fontsize=14)
ax.set_ylabel("Answer accuracy", fontsize=14)

# footnote
fig.text(0.005, 0.005,
         "Schematic, after Liu et al. (2023). Dip depth varies by model"
         " and task; in the original study, mid-context accuracy sometimes"
         " fell below the closed-book level.",
         ha="left", va="bottom", fontsize=10.5, color=GRAY)

fig.tight_layout(rect=(0, 0.04, 1, 1))

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_context_ucurve.png", dpi=150, bbox_inches='tight')
