"""Figure: why continuous batching increases throughput.

Two stacked Gantt-style panels. Top: static batching — the whole batch
holds the GPU until its longest request finishes, so shorter requests
idle on hatched "tails" and batch 2 cannot start before t = 7.
Bottom: continuous batching — a freed slot is immediately refilled with
the next waiting request, keeping every slot busy.
Recreated from the original edition with all labels in US English.
Requires only matplotlib + numpy (DejaVu Sans, matplotlib's default font).
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# --- Palette ---------------------------------------------------------------
GREEN = "#2AA57F"
TEAL = "#2DA1BD"
PURPLE = "#8F57EF"
BLUE = "#467AEE"
PINK = "#E0478B"
ORANGE = "#DE8B2B"
HATCH_FACE = "#E5E7EB"   # idle-time fill
HATCH_EDGE = "#9CA3AF"   # idle-time hatch/edge ink
SLATE = "#374151"        # dashed boundary + in-plot annotations
GRAY_NOTE = "#6B7280"    # footnote ink

BAR_H = 0.7              # bar height in category units
BOUNDARY = 7             # step at which batch 1 fully completes

fig, (ax_static, ax_cont) = plt.subplots(
    2, 1, figsize=(11.6, 7.0), sharex=True,
    gridspec_kw={"height_ratios": [1.07, 1.0], "hspace": 0.40},
)
fig.subplots_adjust(left=0.045, right=0.985, top=0.85, bottom=0.175)


def bar(ax, y, x0, x1, color):
    """A solid request segment from step x0 to step x1."""
    ax.barh(y, x1 - x0, left=x0, height=BAR_H, color=color, zorder=3)


def idle(ax, y, x0, x1):
    """A hatched idle segment (slot waiting for the batch to finish)."""
    ax.barh(y, x1 - x0, left=x0, height=BAR_H, facecolor=HATCH_FACE,
            edgecolor=HATCH_EDGE, hatch="///", linewidth=0.8, zorder=3)


# --- Top panel: static batching --------------------------------------------
bar(ax_static, 3, 0, 6, GREEN)
idle(ax_static, 3, 6, BOUNDARY)
bar(ax_static, 2, 0, 4, TEAL)
idle(ax_static, 2, 4, BOUNDARY)
bar(ax_static, 1, 0, BOUNDARY, PURPLE)          # longest request in batch 1
bar(ax_static, 1, BOUNDARY, 10, PURPLE)         # batch 2 request, same slot
bar(ax_static, 0, 0, 3, BLUE)
idle(ax_static, 0, 3, BOUNDARY)
bar(ax_static, 0, BOUNDARY, 12, BLUE)           # batch 2 request, same slot

ax_static.axvline(BOUNDARY, color=SLATE, linestyle="--",
                  linewidth=1.6, zorder=4)
ax_static.text(3.5, 3.92, "Batch 1 completes in full",
               ha="center", va="center", color=SLATE, fontsize=12.5)
ax_static.text(BOUNDARY + 0.25, 3.92, "Batch 2 starts only now",
               ha="left", va="center", color=SLATE, fontsize=12.5)

ax_static.set_ylim(-0.62, 4.4)
ax_static.set_ylabel("requests", fontsize=12.5)
ax_static.set_title("Static batching: the GPU sits idle on the “tails” (hatched)",
                    fontsize=15.5, fontweight="bold", pad=12)

# --- Bottom panel: continuous batching --------------------------------------
bar(ax_cont, 3, 0, 6, GREEN)
bar(ax_cont, 3, 6, 8, BLUE)
bar(ax_cont, 2, 0, 4, TEAL)
bar(ax_cont, 2, 4, 8, PINK)
bar(ax_cont, 1, 0, 7, PURPLE)
bar(ax_cont, 0, 0, 3, BLUE)
bar(ax_cont, 0, 3, 8, ORANGE)

ax_cont.set_ylim(-0.62, 3.95)
ax_cont.set_ylabel("slots", fontsize=12.5)
ax_cont.set_title("Continuous batching: a freed slot is immediately "
                  "taken by a new request",
                  fontsize=15.5, fontweight="bold", pad=12)
ax_cont.set_xlabel("Generation steps (time) →", fontsize=14.5)

# --- Shared cosmetics --------------------------------------------------------
for ax in (ax_static, ax_cont):
    ax.set_xlim(0, 12)
    ax.set_xticks(np.arange(0, 13, 2))
    ax.tick_params(axis="x", labelsize=13.5)
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

fig.suptitle("Why continuous batching increases throughput",
             fontsize=17.5, fontweight="bold", y=0.975)

fig.text(0.5, 0.022,
         "Static: the batch holds the GPU until its longest request finishes "
         "— short requests sit idle.\n"
         "Continuous (Orca, 2022 → vLLM): the scheduler adds and removes "
         "requests on every pass, keeping the GPU busy.",
         ha="center", va="bottom", ma="center",
         fontsize=12.5, color=GRAY_NOTE)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_batching.png",
            dpi=150, bbox_inches='tight')
