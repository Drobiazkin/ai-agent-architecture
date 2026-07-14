"""IsoFLOP curves: Chinchilla scaling law -- optimal model size for a fixed
compute budget.  Schematic reproduction of the parametric loss law from
Hoffmann et al., 2022 ("Training Compute-Optimal Large Language Models").

Self-contained: matplotlib + numpy only, default DejaVu Sans font.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Chinchilla parametric loss law (Hoffmann et al., 2022) -----------------
E, A, B, ALPHA, BETA = 1.69, 406.4, 410.7, 0.34, 0.28


def loss(N, C):
    """Training loss for N parameters at compute budget C (FLOPs), D = C/6N."""
    D = C / (6.0 * N)
    return E + A / N**ALPHA + B / D**BETA


def n_optimal(C):
    """Analytic argmin of loss(N, C) over N."""
    coef = (ALPHA * A / (BETA * B)) ** (1.0 / (ALPHA + BETA))
    return coef * (C / 6.0) ** (BETA / (ALPHA + BETA))


BUDGETS = [
    (3e21, "#2563eb", "C = 3·10²¹"),   # C = 3*10^21
    (1e23, "#7c3aed", "C = 1·10²³"),   # C = 1*10^23
    (3e24, "#dc2626", "C = 3·10²⁴"),   # C = 3*10^24
]

N = np.logspace(8, 12, 800)

fig, ax = plt.subplots(figsize=(9.6, 6.2))
fig.subplots_adjust(left=0.075, right=0.985, top=0.845, bottom=0.150)

for C, color, label in BUDGETS:
    ax.plot(N, loss(N, C), color=color, lw=2.5, label=label,
            zorder=3, solid_capstyle="round")
    n_opt = n_optimal(C)
    ax.plot([n_opt], [loss(n_opt, C)], marker="o", color=color,
            ms=9.2, zorder=4)

ax.set_xscale("log")
ax.set_xlim(10**7.8, 10**12.2)
ax.set_ylim(1.9, 4.2)

ax.set_title(
    "Chinchilla scaling law: for a fixed compute budget\n"
    "there is an optimal model size (dots)",
    fontsize=13, fontweight="bold", pad=8,
)
ax.set_xlabel("Number of parameters N (log scale)", fontsize=12.5)
ax.set_ylabel("Training loss L (lower is better)", fontsize=12.5)

ax.grid(True, which="both", color="#b0b0b0", alpha=0.15, lw=0.9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(1.0)
ax.spines["bottom"].set_linewidth(1.0)
ax.tick_params(axis="both", which="major", labelsize=12)

ax.text(
    4.6e9, 3.27,
    "bigger budget →\nthe optimum shifts\ntoward a larger model",
    ha="center", va="center", fontsize=10.5, color="#374151",
    linespacing=1.2,
)

legend = ax.legend(
    title="Compute budget (FLOPs)", loc="upper right",
    fontsize=11, title_fontsize=11,
    framealpha=0.95, edgecolor="#d6d6d6",
)

fig.text(
    0.5, 0.006,
    "Schematic (parametric-law shape from Hoffmann et al., 2022). "
    "Too small a model underuses the budget;\n"
    "too large a model is starved of tokens (D = C / 6N). "
    "The minimum is the compute-optimal split of N and D.",
    ha="center", va="bottom", fontsize=10, color="#6b7280",
    linespacing=1.2,
)

fig.savefig(r'/Users/aleksandrdrobiazkin/IdeaProjects/ai-agent-architecture/book/images/fig_isoflop.png', dpi=150, bbox_inches='tight')
