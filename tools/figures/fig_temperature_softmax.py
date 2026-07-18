"""Figure: effect of temperature on the next-token distribution — softmax(logits / T).

Three side-by-side bar panels (T = 0.5 / 1.0 / 2.0) over the same eight
candidate tokens, showing how dividing the logits by T sharpens or flattens
the softmax distribution. Softmax is computed exactly; the logits are a
didactic example tuned so the displayed probabilities match the book text.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# Candidate next tokens for the prompt "The capital of France is —"
TOKENS = ["Paris", "city", "Lyon", "capital", "France", "—", "beautiful", "the"]

# Didactic logits (shift-invariant offsets relative to the top token)
LOGITS = np.array([0.0, -2.79, -3.49, -3.58, -4.40, -4.77, -5.17, -5.59])

LABEL_THRESHOLD = 0.02  # annotate a bar only if its probability is visible


def softmax(logits: np.ndarray, temperature: float) -> np.ndarray:
    z = logits / temperature
    e = np.exp(z - z.max())
    return e / e.sum()


PANELS = [
    # (temperature, bar color, side annotation, annotation xy in axes coords)
    (0.5, "#467aee", "sharpening\n(→ determinism)", (0.44, 0.94)),
    (1.0, "#2aa57f", None, None),
    (2.0, "#e14646", "flattening\n(→ diversity)", (0.50, 0.94)),
]

fig, axes = plt.subplots(1, 3, figsize=(13.4, 5.2), sharey=True)

x = np.arange(len(TOKENS))

for ax, (temperature, color, note, note_xy) in zip(axes, PANELS):
    probs = softmax(LOGITS, temperature)
    ax.bar(x, probs, width=0.72, color=color, zorder=3)

    for xi, p in zip(x, probs):
        if p >= LABEL_THRESHOLD:
            ax.text(xi, p + 0.018, f"{p:.2f}", ha="center", va="bottom",
                    fontsize=10.5, color="#333333")

    if note is not None:
        ax.text(*note_xy, note, transform=ax.transAxes, ha="left", va="top",
                fontsize=12, fontstyle="italic", color=color, linespacing=1.4)

    ax.set_title(f"Temperature T = {temperature}", fontsize=14.5,
                 fontweight="bold", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(TOKENS, rotation=35, ha="right", fontsize=11.5)
    ax.set_ylim(0, 1.0)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.tick_params(axis="y", labelsize=11.5)
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.8, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

axes[0].set_ylabel("Next-token probability", fontsize=12.5)

fig.suptitle("Effect of temperature on the next-token distribution"
             "  ·  softmax(logits / T)",
             fontsize=15.5, fontweight="bold", y=0.985)

fig.text(0.5, 0.012,
         "Example prompt: “The capital of France is —”.  "
         "The softmax computation is exact; the logit values are a didactic example.",
         ha="center", va="bottom", fontsize=11.5, color="#5a6472")

fig.subplots_adjust(left=0.055, right=0.99, top=0.83, bottom=0.20, wspace=0.12)

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_temperature_softmax.png", dpi=150, bbox_inches='tight')
