"""Figure: quadratic cost of self-attention vs. context length.

Recreates fig_attention_complexity for the English edition. Two panels:
  - Left: linear scale. Full attention O(n^2) vs. a linear alternative O(n),
    cost relative to a 1,024-token baseline, annotated at each doubling.
  - Right: log-log scale, where the slope reveals the growth exponent
    (slope 2 for O(n^2), slope 1 for O(n)).
Values are exact: cost(n) = (n/1024)^p for p in {1, 2}.
Only matplotlib + numpy; DejaVu Sans (matplotlib default).
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----- palette (sampled from the original figure) -----
RED = "#dc2626"       # full attention O(n^2)
BLUE = "#2563eb"      # linear alternative O(n)
LABEL = "#374151"     # per-point multiplier labels
FOOTNOTE = "#6b7280"  # footnote text
GRID = "#eeeeee"      # gridlines
SPINE = "#2a2a2a"     # axis spines

# ----- data (exact, by construction) -----
n = np.array([1024, 2048, 4096, 8192, 16384, 32768])
quad = (n / 1024.0) ** 2   # 1, 4, 16, 64, 256, 1024
lin = n / 1024.0           # 1, 2, 4, 8, 16, 32

# ----- figure -----
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.65, 5.3))
fig.subplots_adjust(left=0.058, right=0.995, top=0.795, bottom=0.185,
                    wspace=0.14)

fig.suptitle("Attention cost grows quadratically with context length"
             "  ·  O(n²·d)",
             fontsize=18, fontweight="bold", y=0.985)

for ax in (ax1, ax2):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(SPINE)
    ax.spines["bottom"].set_color(SPINE)
    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_linewidth(1.2)
    ax.tick_params(labelsize=13, colors=SPINE)

# ----- left panel: linear scale -----
ax1.plot(n, quad, "-o", color=RED, linewidth=3, markersize=10,
         label="Full attention  O(n²)", zorder=3)
ax1.plot(n, lin, "-s", color=BLUE, linewidth=3, markersize=9,
         label="Linear alternative  O(n)", zorder=3)

ax1.set_title("Linear scale", fontsize=16, fontweight="bold", pad=12)
ax1.set_xlabel("Context length n (tokens)", fontsize=14)
ax1.set_ylabel("Relative cost (baseline = 1024)", fontsize=14)
ax1.grid(True, color=GRID, linewidth=1, zorder=0)
ax1.set_axisbelow(True)
ax1.legend(loc="upper left", fontsize=13, frameon=False)

# multiplier labels at each doubling of n
offsets = {
    1024: (-10, 5),
    2048: (2, 5),
    4096: (4, 12),
    8192: (-2, 5),
    16384: (-4, 10),
    32768: (-10, 30),   # sits above the axes; clipping disabled
}
for xi, yi in zip(n, quad):
    ax1.annotate(f"{int(yi)}×", xy=(xi, yi),
                 xytext=offsets[int(xi)], textcoords="offset points",
                 ha="center", fontsize=12, color=LABEL,
                 annotation_clip=False, clip_on=False, zorder=4)

# arrow: each doubling of n quadruples the work
ax1.annotate("doubling n → 4× the work",
             xy=(2400, 12), xytext=(6000, 112),
             fontsize=14, color=RED, ha="left", va="baseline",
             arrowprops=dict(arrowstyle="->", color=RED, linewidth=1.5))

# ----- right panel: log-log scale -----
ax2.plot(n, quad, "-o", color=RED, linewidth=3, markersize=10,
         label="O(n²)", zorder=3)
ax2.plot(n, lin, "-s", color=BLUE, linewidth=3, markersize=9,
         label="O(n)", zorder=3)
ax2.set_xscale("log")
ax2.set_yscale("log")

ax2.set_title("Log–log scale (slope = growth exponent)",
              fontsize=16, fontweight="bold", pad=12)
ax2.set_xlabel("Context length n (tokens, log)", fontsize=14)
ax2.set_ylabel("Relative cost (log)", fontsize=14)
ax2.grid(True, which="both", color=GRID, linewidth=1, zorder=0)
ax2.set_axisbelow(True)
ax2.legend(loc="upper left", fontsize=13, frameon=False)

# ----- footnote -----
fig.text(0.5, 0.028,
         "At 32k context, full attention takes ~1000× the work relative"
         " to 1k — a direct consequence of the n×n matrix (§1.4)."
         " The values are exact (this is the complexity itself).",
         ha="center", fontsize=10.5, color=FOOTNOTE)

fig.savefig(r'/Users/aleksandrdrobiazkin/IdeaProjects/ai-agent-architecture/book/images/fig_attention_complexity.png',
            dpi=150, bbox_inches='tight')
