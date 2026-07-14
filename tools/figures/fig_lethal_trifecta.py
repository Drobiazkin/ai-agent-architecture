"""Figure: the "lethal trifecta" Venn diagram (S. Willison, 2025).

Three properties of an agent — access to private data, untrusted content
in the context, external communication — are individually manageable;
only the combination of all three enables data exfiltration.
Self-contained: matplotlib + numpy only, DejaVu Sans (matplotlib default).
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# ----- palette (matches the original figure) -----
BLUE_FILL = "#2563eb"
RED_FILL = "#dc2626"
GREEN_FILL = "#059669"
BLUE_TEXT = "#1e40af"
RED_TEXT = "#b91c1c"
GREEN_TEXT = "#047857"
CENTER_TEXT = "#7f1d1d"
GRAY_TEXT = "#6b7280"

FILL_ALPHA = 0.20
EDGE_ALPHA = 0.38

# Layout is expressed in the original figure's pixel grid (1339 x 1248 @ 100 dpi).
# bbox_inches="tight" spans the full axes plus a 0.1 in pad on each side, so the
# figure is drawn 10 px smaller per side and the limits are cropped to match:
# the saved PNG comes out exactly 1339 x 1248.
W, H = 1339, 1248
PAD = 10  # px, savefig tight pad (0.1 in @ 100 dpi)
fig = plt.figure(figsize=((W - 2 * PAD) / 100, (H - 2 * PAD) / 100))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(PAD, W - PAD)
ax.set_ylim(H - PAD, PAD)  # y grows downward, like image coordinates
ax.set_aspect("equal")
ax.axis("off")

# ----- the three circles (draw order: blue, red, green) -----
R = 312
for (cx, cy), color in [
    ((520, 485), BLUE_FILL),
    ((820, 485), RED_FILL),
    ((670, 742), GREEN_FILL),
]:
    ax.add_patch(
        Circle(
            (cx, cy),
            R,
            facecolor=color,
            edgecolor=color,
            alpha=None,
            linewidth=2,
            zorder=2,
        )
    )
    # alpha per component: fill 0.2, edge 0.38
    ax.patches[-1].set_facecolor(
        matplotlib.colors.to_rgba(color, FILL_ALPHA)
    )
    ax.patches[-1].set_edgecolor(
        matplotlib.colors.to_rgba(color, EDGE_ALPHA)
    )

# ----- title -----
ax.text(
    W / 2,
    30,
    "The “lethal trifecta”: danger requires all three properties combined",
    ha="center",
    va="center",
    fontsize=22,
    fontweight="bold",
    color="black",
)

# ----- circle labels -----
ax.text(
    300,
    243,
    "Access to\nprivate data",
    ha="center",
    va="center",
    fontsize=17,
    fontweight="bold",
    color=BLUE_TEXT,
    linespacing=1.25,
)
ax.text(
    1040,
    243,
    "Untrusted content\nin the context",
    ha="center",
    va="center",
    fontsize=17,
    fontweight="bold",
    color=RED_TEXT,
    linespacing=1.25,
)
ax.text(
    670,
    1076,
    "External communication\n(exfiltration)",
    ha="center",
    va="center",
    fontsize=17,
    fontweight="bold",
    color=GREEN_TEXT,
    linespacing=1.25,
)

# ----- pairwise overlap note -----
ax.text(
    670,
    350,
    "2 of 3 — safe",
    ha="center",
    va="center",
    fontsize=15,
    fontstyle="italic",
    color=GRAY_TEXT,
)

# ----- triple-overlap label -----
ax.text(
    670,
    553,
    "Exfiltration\npossible",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold",
    color=CENTER_TEXT,
    linespacing=1.25,
)

# ----- footnote -----
ax.text(
    W / 2,
    1194,
    "S. Willison (2025). The Rule of Two (Meta, 2025): an autonomous agent"
    " may hold at most two of the three properties;\n"
    "with all three, human confirmation is mandatory."
    " Removing any one leg breaks the data-theft chain.",
    ha="center",
    va="center",
    fontsize=14,
    color=GRAY_TEXT,
    linespacing=1.35,
)

fig.savefig(
    r"/Users/aleksandrdrobiazkin/IdeaProjects/ai-agent-architecture/book/images/fig_lethal_trifecta.png",
    dpi=100,
    bbox_inches="tight",
)
