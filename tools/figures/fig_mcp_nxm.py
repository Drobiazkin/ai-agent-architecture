"""Figure: The N×M integration problem and its solution with a standard protocol (MCP).

Two-panel node-link diagram. Left: every app wired to every capability
(M×N point-to-point connectors). Right: a single MCP hub (M + N protocol
implementations). Recreated from the original with English labels.

Canvas geometry is authored in the original figure's pixel space
(2010 x 925 at 150 dpi) so positions can be read straight off the source.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle

# ----- palette (sampled from the original) -----------------------------------
BLUE = "#467AEE"       # app boxes
GREEN = "#2AA57F"      # capability boxes (data / tools / APIs / files)
PURPLE = "#894DEE"     # MCP hub ellipse
RED_LINE = "#EF9D9D"   # point-to-point connector lines (left panel)
PURPLE_LINE = "#B089F4"  # protocol lines (right panel)
RED_NOTE = "#B91C1C"   # left footnote
PURPLE_NOTE = "#6D28D9"  # right footnote

W, H = 2010, 925  # original pixel canvas
DPI = 150

fig = plt.figure(figsize=(W / DPI, H / DPI))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)  # y grows downward, matching image pixel coordinates
ax.set_aspect("equal")
ax.axis("off")

# White background rectangle anchors bbox_inches='tight' to the full canvas.
ax.add_patch(Rectangle((0, 0), W, H, facecolor="white", edgecolor="none",
                       zorder=0))

# ----- node geometry (pixel coords from the original) ------------------------
APP_W, APP_H = 136, 75
SRV_W, SRV_H = 146, 67

app_rows = [303.5, 531.0, 758.0]          # box centers, y
srv_rows = [265.5, 442.5, 619.5, 795.5]

APPS_L_X = 35        # left panel, app column (left edge)
SRVS_L_X = 837       # left panel, capability column
APPS_R_X = 1036      # right panel, app column
SRVS_R_X = 1838      # right panel, capability column

ELL_CX, ELL_CY = 1505.5, 530.5
ELL_W, ELL_H = 165, 127

app_labels = ["App 1", "App 2", "App 3"]
srv_labels = ["Data A", "Tool B", "API C", "Files D"]


def box(x_left, y_center, w, h, color, label, bold):
    ax.add_patch(Rectangle((x_left, y_center - h / 2), w, h,
                           facecolor=color, edgecolor="none", zorder=2))
    ax.text(x_left + w / 2, y_center, label, ha="center", va="center",
            color="white", fontsize=10,
            fontweight="bold" if bold else "normal", zorder=4)


# ----- left panel: full M x N mesh -------------------------------------------
for ay in app_rows:
    for sy in srv_rows:
        ax.plot([APPS_L_X + APP_W, SRVS_L_X], [ay, sy],
                color=RED_LINE, lw=1.0, zorder=1)

for ay, lbl in zip(app_rows, app_labels):
    box(APPS_L_X, ay, APP_W, APP_H, BLUE, lbl, bold=True)
for sy, lbl in zip(srv_rows, srv_labels):
    box(SRVS_L_X, sy, SRV_W, SRV_H, GREEN, lbl, bold=False)

# ----- right panel: hub-and-spoke through MCP --------------------------------
for ay in app_rows:
    ax.plot([APPS_R_X + APP_W, ELL_CX], [ay, ELL_CY],
            color=PURPLE_LINE, lw=2.0, zorder=1)
for sy in srv_rows:
    ax.plot([ELL_CX, SRVS_R_X], [ELL_CY, sy],
            color=PURPLE_LINE, lw=2.0, zorder=1)

for ay, lbl in zip(app_rows, app_labels):
    box(APPS_R_X, ay, APP_W, APP_H, BLUE, lbl, bold=True)
for sy, lbl in zip(srv_rows, srv_labels):
    box(SRVS_R_X, sy, SRV_W, SRV_H, GREEN, lbl, bold=False)

ax.add_patch(Ellipse((ELL_CX, ELL_CY), ELL_W, ELL_H,
                     facecolor=PURPLE, edgecolor="none", zorder=3))
ax.text(ELL_CX, ELL_CY, "MCP", ha="center", va="center", color="white",
        fontsize=11.5, fontweight="bold", zorder=4)

# ----- titles and footnotes ---------------------------------------------------
ax.text(W / 2, 29.5,
        "The N×M Integration Problem and Its Solution"
        " with a Standard Protocol",
        ha="center", va="center", fontsize=15, fontweight="bold", color="black")

ax.text(503.5, 120, "Without a standard: M×N integrations",
        ha="center", va="center", fontsize=13, fontweight="bold", color="black")
ax.text(1505, 120, "With MCP: M + N protocol implementations",
        ha="center", va="center", fontsize=13, fontweight="bold", color="black")

ax.text(504.5, 888.5,
        "M × N = 3 × 4 = 12 custom connectors",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color=RED_NOTE)
ax.text(1505.5, 888.5,
        "M + N = 3 + 4 = 7 implementations of a single protocol",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color=PURPLE_NOTE)

fig.savefig(r'/Users/aleksandrdrobiazkin/IdeaProjects/ai-agent-architecture/book/images/fig_mcp_nxm.png', dpi=150, bbox_inches='tight')
