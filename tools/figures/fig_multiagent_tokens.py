"""Figure: token cost of orchestration levels (chat vs. single agent vs. multi-agent).

Recreates fig_multiagent_tokens for the English edition. Data (Anthropic's
multi-agent research system report, 2025): relative token consumption of
~1x (chat, single call), ~4x (single agent, tool-use loop), ~15x
(multi-agent system, supervisor + workers).
Only matplotlib + numpy; DejaVu Sans (matplotlib default).
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----- palette (sampled from the original figure) -----
BLUE = "#317af5"      # chat bar
PURPLE = "#916bdd"    # single-agent bar
RED = "#e23232"       # multi-agent bar
SLATE = "#33475b"     # multiplier labels + annotation
FOOTNOTE = "#7a8a9a"  # footnote text
SPINE = "#383838"     # axis spines

# ----- data -----
labels = [
    "Chat\n(single call)",
    "Single agent\n(tool-use loop)",
    "Multi-agent system\n(supervisor + workers)",
]
values = np.array([1, 4, 15])
colors = [BLUE, PURPLE, RED]
x = np.arange(len(values))

fig, ax = plt.subplots(figsize=(9.35, 5.32))

ax.bar(x, values, width=0.55, color=colors, zorder=3)

# ----- multiplier labels above the bars -----
for xi, v in zip(x, values):
    ax.text(xi, v + 0.35, f"~{v}×", ha="center", va="bottom",
            fontsize=19, fontweight="bold", color=SLATE, zorder=5)

# ----- annotation: quality is paid for in tokens -----
ax.text(
    0.48, 14.55,
    "token consumption explains ~80%\n"
    "of the variance in quality: here,\n"
    "quality is literally paid for in tokens",
    ha="left", va="top", fontsize=11.8, color=SLATE, zorder=5,
)
ax.annotate(
    "", xy=(1.98, 15.05), xytext=(1.50, 14.35),
    arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.6,
                    connectionstyle="arc3,rad=-0.18",
                    shrinkA=4, shrinkB=2),
    zorder=5,
)

# ----- axes cosmetics -----
ax.set_xlim(-0.5, 2.5)
ax.set_ylim(0, 17.3)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=12, color="black")
ax.set_yticks(range(0, 17, 2))
ax.tick_params(axis="y", labelsize=12, colors=SPINE)
ax.set_ylabel("Token consumption relative to chat", fontsize=14.5)
ax.set_title(
    "The price of autonomy: each level of orchestration\n"
    "multiplies token consumption",
    fontsize=16.5, fontweight="bold", pad=14,
)
ax.grid(True, color="#b0b8c8", alpha=0.35, lw=0.8, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(SPINE)

fig.text(
    0.5, -0.015,
    "Based on Anthropic's report on its multi-agent research system (2025). "
    "Multi-agent designs pay off on highly parallelizable,\n"
    "high-value tasks — and only when the value justifies "
    "the multiplied cost (§14.3).",
    ha="center", va="top", fontsize=10.5, color=FOOTNOTE,
)

fig.savefig(r'/Users/aleksandrdrobiazkin/IdeaProjects/ai-agent-architecture/book/images/fig_multiagent_tokens.png', dpi=150, bbox_inches='tight')
