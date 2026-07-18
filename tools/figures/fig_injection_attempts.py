"""Figure: indirect prompt injection success rate vs. number of attempts.

Data: Claude Opus 4.5 system card (Anthropic, November 2025),
Gray Swan Shade tool, "thinking" variant.
Self-contained: matplotlib + numpy only, DejaVu Sans (matplotlib default).
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ----- data (read off the system card) -----
attempts = np.array([1, 10, 100])
success = np.array([4.7, 33.6, 63.0])  # percent

# ----- palette (matches the original figure) -----
LINE_RED = "#dc2626"
LABEL_RED = "#7f1d1d"
FOOT_GRAY = "#6b7280"
GRID_GRAY = "#e6e6e6"

fig, ax = plt.subplots(figsize=(14.2, 8))

ax.set_xscale("log")
ax.plot(
    attempts,
    success,
    color=LINE_RED,
    linewidth=4,
    marker="o",
    markersize=13,
    zorder=3,
)

# value labels above each point
for x, y in zip(attempts, success):
    ax.annotate(
        f"{y}%",
        xy=(x, y),
        xytext=(0, 22),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=17,
        fontweight="bold",
        color=LABEL_RED,
    )

# ----- axes -----
ax.set_ylim(0, 75)
ax.set_yticks(np.arange(0, 71, 10))
ax.set_xticks(attempts)
ax.set_xticklabels(["1 attempt", "10 attempts", "100 attempts"])
ax.tick_params(axis="both", which="major", labelsize=15)
ax.xaxis.set_minor_formatter(plt.NullFormatter())

ax.set_ylabel("Indirect prompt injection success, %", fontsize=16)

ax.grid(True, which="both", color=GRID_GRAY, linewidth=1, zorder=0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.set_title(
    "Indirect injection success rises with the number of attempts\n"
    "(even for a modern model with safeguards)",
    fontsize=19,
    fontweight="bold",
    pad=16,
)

# ----- footnote -----
footnote = (
    "Claude Opus 4.5 system card (Anthropic, November 2025), "
    "Gray Swan Shade tool, “thinking” variant.\n"
    "Takeaway: safeguards reduce the per-attempt probability "
    "but do not eliminate it — “the attacker moves second.”"
)
fig.text(0.5, 0.045, footnote, ha="center", va="top", fontsize=13, color=FOOT_GRAY)

fig.subplots_adjust(left=0.07, right=0.98, top=0.87, bottom=0.09)

fig.savefig(
    Path(__file__).resolve().parents[2] / "book" / "images" / "fig_injection_attempts.png",
    dpi=100,
    bbox_inches="tight",
)
