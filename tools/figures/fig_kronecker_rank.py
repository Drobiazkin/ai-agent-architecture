"""Figure: Why the Kronecker product increases expressivity (Appendix A.5).

Left panel: same parameter budget, different achievable rank (LoRA vs KronA).
Right panel: achievable update rank on a log scale.
Self-contained: matplotlib + numpy only, DejaVu Sans (matplotlib default).
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------- palette
BLUE = "#2563eb"      # LoRA
PURPLE = "#7c3aed"    # KronA
SLATE = "#334155"     # formula text
GRAY = "#6b7280"      # secondary / footnote text
GRID = "#e9e9e9"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.8, 5.68))
fig.subplots_adjust(left=0.055, right=0.99, top=0.835, bottom=0.20, wspace=0.25)

fig.suptitle(
    "Why the Kronecker Product Increases Expressivity (§A.5)",
    fontsize=18, fontweight="bold", y=0.99, color="black",
)

# ------------------------------------------------------- left panel: text
ax1.set_title(
    "Same Parameter Budget — Different Rank",
    fontsize=16, fontweight="bold", pad=14,
)
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.axis("off")

ax1.text(0.5, 0.925, "Adapting a 4096 × 4096 matrix",
         ha="center", va="center", fontsize=14, color=GRAY)

ax1.text(0.0, 0.735, "LoRA (low rank):",
         ha="left", va="center", fontsize=15, fontweight="bold", color=BLUE)
ax1.text(0.0, 0.640, "ΔW = B·A,  rank(ΔW) ≤ r",
         ha="left", va="center", fontsize=13.5, color=SLATE)
ax1.text(0.0, 0.548,
         "r = 8  →  65,536 parameters,  rank ≤ 8",
         ha="left", va="center", fontsize=13.5, color=BLUE)

ax1.text(0.0, 0.375, "KronA (Kronecker product):",
         ha="left", va="center", fontsize=15, fontweight="bold", color=PURPLE)
ax1.text(0.0, 0.280,
         "ΔW = A ⊗ B,  rank(ΔW) = rank(A)·rank(B)",
         ha="left", va="center", fontsize=13.5, color=SLATE)
ax1.text(0.0, 0.188,
         "A, B each 64×64  →  8,192 parameters,  rank up to 4096",
         ha="left", va="center", fontsize=13.5, color=PURPLE)

ax1.text(0.0, 0.045,
         "Kronecker: ≈8× fewer parameters — yet an achievable rank\n"
         "orders of magnitude higher (within the structured family A⊗B).",
         ha="left", va="center", fontsize=12.5, color=GRAY,
         style="italic", linespacing=1.5)

# --------------------------------------------------- right panel: log bars
ax2.set_title("Achievable Update Rank", fontsize=16, fontweight="bold", pad=14)

labels = ["LoRA r=8\n(65.5K params)", "KronA 64⊗64\n(8.2K params)"]
ranks = np.array([8, 4096])
colors = [BLUE, PURPLE]

bars = ax2.bar([0, 1], ranks, width=0.55, color=colors, alpha=0.85, zorder=3)

ax2.set_yscale("log")
ax2.set_ylim(1, 8500)
ax2.set_xticks([0, 1])
ax2.set_xticklabels(labels, fontsize=13)
ax2.tick_params(axis="y", labelsize=13)
ax2.set_ylabel("Achievable rank of update ΔW (log)", fontsize=14)
ax2.grid(True, which="both", axis="y", color=GRID, linewidth=0.8, zorder=0)
ax2.set_axisbelow(True)

for x, r in zip([0, 1], ranks):
    ax2.text(x, r * 1.05, f"rank {r}", ha="center", va="bottom",
             fontsize=16, fontweight="bold", color="#1f2937")

# ------------------------------------------------------------- footnote
fig.text(
    0.5, 0.005,
    "A low-rank factorization caps the update's rank at r; "
    "the Kronecker product multiplies the ranks of its factors.\n"
    "KronA (Edalati/Tahaei et al., 2022) replaces LoRA's low-rank product "
    "with A⊗B.",
    ha="center", va="bottom", fontsize=12.5, color=GRAY, linespacing=1.4,
)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_kronecker_rank.png",
            dpi=150, bbox_inches='tight')
