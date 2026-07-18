"""Figure: Hosted API vs. self-host break-even analysis.

Recreates fig_breakeven for the English edition. Cost model:
  - Hosted API: blended $2-5 per million tokens (band), $3/M midpoint (line).
    Monthly cost ($K) = rate ($/M) * load (M tokens/day) * 30 / 1000.
  - Self-host: rented GPU nodes at $3K/month each; one node covers up to
    ~50M tokens/day, then a second node is added (step function).
Only matplotlib + numpy; DejaVu Sans (matplotlib default).
"""

from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----- palette (sampled from the original figure) -----
BLUE = "#1f6ff5"      # hosted API line / marker / band hue
RED = "#e02020"       # self-host step line
PURPLE = "#7c3aed"    # break-even zone band + annotation
SLATE = "#33475b"     # example annotation
FOOTNOTE = "#7a8a9a"  # footnote text
SPINE = "#383838"     # axis spines

# ----- data -----
x = np.linspace(0, 80, 400)
hosted_low = 0.06 * x    # $2/M tokens -> $K/month
hosted_high = 0.15 * x   # $5/M tokens -> $K/month
hosted_mid = 0.09 * x    # $3/M tokens -> $K/month

# self-host: $3K/month per node, second node needed beyond ~50M tokens/day
step_x = [0, 50, 50, 80]
step_y = [3, 3, 6, 6]

fig, ax = plt.subplots(figsize=(9.4, 5.5))

# break-even zone (vertical band)
ax.axvspan(20, 50, color=PURPLE, alpha=0.11, zorder=0)

# hosted API cost band and midpoint line
ax.fill_between(x, hosted_low, hosted_high, color=BLUE, alpha=0.18, zorder=1,
                label="Hosted API: $2–5 per million tokens (blended)")
ax.plot(x, hosted_mid, color=BLUE, lw=3, zorder=3,
        label="Hosted API: $3 per million (midpoint)")

# self-host step function
ax.plot(step_x, step_y, color=RED, lw=3, zorder=4,
        label="Self-host: rented GPU nodes ($3K/month per node)")

# worked example from §2.2: ~9.5M tokens/day on the $3/M midline
ax.plot([9.5], [0.09 * 9.5], "o", color=BLUE, markersize=9, zorder=5)

# ----- annotations -----
ax.annotate(
    "break-even zone\n≈ 20–50M tokens/day",
    xy=(33.3, 3.0), xytext=(36, 7.4),
    fontsize=12.5, color=PURPLE, ha="left", va="center",
    arrowprops=dict(arrowstyle="->", color=PURPLE, lw=1.6,
                    shrinkA=6, shrinkB=4),
    zorder=6,
)
ax.annotate(
    "example in §2.2:\n~9.5M/day → hundreds of $/month",
    xy=(9.5, 0.9), xytext=(3.0, 4.0),
    fontsize=12.5, color=SLATE, ha="left", va="center",
    arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.6,
                    connectionstyle="arc3,rad=-0.15",
                    shrinkA=8, shrinkB=8),
    zorder=6,
)

# ----- axes cosmetics -----
ax.set_xlim(0, 80)
ax.set_ylim(0, 13)
ax.set_xticks(range(0, 81, 10))
ax.set_yticks(range(0, 13, 2))
ax.tick_params(labelsize=12, colors=SPINE)
ax.set_xlabel("Sustained load, million tokens per day", fontsize=14.5)
ax.set_ylabel("Cost, $K per month", fontsize=14.5)
ax.set_title(
    "Hosted vs. self-host: the break-even point —\n"
    "a question of sustained volume, not ideology",
    fontsize=16.5, fontweight="bold", pad=14,
)
ax.grid(True, color="#b0b8c8", alpha=0.35, lw=0.8, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(SPINE)

legend = ax.legend(loc="upper left", fontsize=12.2, framealpha=0.95,
                   edgecolor="#c8c8c8", borderpad=0.7)
legend.set_zorder(7)

fig.text(
    0.5, -0.015,
    "Illustrative: rates and rentals are 2025–2026 orders of magnitude; "
    "peaky traffic worsens the self-host math (provisioning for peak),\n"
    "while batch workloads improve it. The structure of the calculation "
    "(§2.6) outlives any specific prices.",
    ha="center", va="top", fontsize=10.5, color=FOOTNOTE,
)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_breakeven.png", dpi=150, bbox_inches='tight')
