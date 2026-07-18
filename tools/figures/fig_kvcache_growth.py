"""Figure: KV-cache growth is linear in context length; GQA cuts it by the
head-count ratio.

Exact values from the KV-cache size formula (§1.6):
    bytes = 2 (K and V) * n_layers * n_kv_heads * d_head * bytes_per_value * seq_len
Example configuration: 80 layers, d_head = 128, fp16 (2 bytes), batch = 1.
MHA: 64 KV heads -> 80 GiB at 32,768 tokens.  GQA: 8 KV heads -> 1/8 of MHA.
"""

from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Data (exact, from the formula) -----------------------------------------
N_LAYERS = 80
D_HEAD = 128
BYTES_FP16 = 2
GIB = 1024**3

def kv_cache_gib(seq_len, n_kv_heads):
    return 2 * N_LAYERS * n_kv_heads * D_HEAD * BYTES_FP16 * seq_len / GIB

seq = np.linspace(0, 32768, 200)
mha = kv_cache_gib(seq, 64)
gqa = kv_cache_gib(seq, 8)

marker_x = np.array([4096, 8192, 16384, 32768])
mha_pts = kv_cache_gib(marker_x, 64)   # 10, 20, 40, 80 GiB
gqa_pts = kv_cache_gib(marker_x, 8)    # 1.25, 2.5, 5, 10 GiB

# --- Style -------------------------------------------------------------------
RED = "#dc2626"
GREEN = "#059669"
GREY = "#666666"

fig, ax = plt.subplots(figsize=(15.4, 6.7))

# Shaded gap between the two curves (the memory saved by GQA)
ax.fill_between(seq, gqa, mha, color=RED, alpha=0.07, zorder=1)

# Dotted guides from the x-axis up to the MHA curve at each marker
for x, y in zip(marker_x, mha_pts):
    ax.plot([x, x], [0, y], linestyle=":", color="#999999", linewidth=1.2,
            zorder=2)

ax.plot(seq, mha, color=RED, linewidth=3.5, zorder=4,
        label="MHA — 64 KV heads", solid_capstyle="round")
ax.plot(seq, gqa, color=GREEN, linewidth=3.5, zorder=4,
        label="GQA — 8 KV heads", solid_capstyle="round")

ax.plot(marker_x, mha_pts, "o", color=RED, markersize=9, zorder=5)
ax.plot(marker_x, gqa_pts, "o", color=GREEN, markersize=9, zorder=5)

# Value labels on the MHA markers
for x, y in zip(marker_x, mha_pts):
    ax.annotate(f"{y:.0f} GB", (x, y), textcoords="offset points",
                xytext=(-4, 9), ha="right", fontsize=10, color=RED, zorder=6)

# Value label on the GQA endpoint
ax.annotate(f"{gqa_pts[-1]:.1f} GB", (marker_x[-1], gqa_pts[-1]),
            textcoords="offset points", xytext=(10, -5), ha="left",
            fontsize=12, color=GREEN, zorder=6)

# --- Axes --------------------------------------------------------------------
ax.set_title("KV-cache growth is linear in context length · "
             "GQA cuts it by a constant factor",
             fontsize=16, fontweight="bold", pad=14)
ax.set_xlabel("Context length, seq_len (tokens)", fontsize=14)
ax.set_ylabel("KV-cache size, GB (batch = 1)", fontsize=14)

ax.set_xlim(0, 36500)
ax.set_ylim(0, 84)
ax.set_xticks(np.arange(0, 35001, 5000))
ax.set_yticks(np.arange(0, 81, 10))
ax.tick_params(labelsize=13)

ax.grid(True, color="#cccccc", linewidth=0.8, alpha=0.45, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_linewidth(1.4)

ax.legend(loc="upper left", fontsize=14, frameon=False,
          handlelength=2.2, borderaxespad=0.6)

# --- Footnote ----------------------------------------------------------------
fig.text(0.005, -0.015,
         "Example configuration: 80 layers, d_head=128, fp16, batch=1.  "
         "Values are exact (formula §1.6).  "
         "GQA (8 KV heads) is an 8× reduction relative to MHA (64).",
         fontsize=11, color=GREY, ha="left", va="top")

fig.savefig(Path(__file__).resolve().parents[2] / "book" / "images" / "fig_kvcache_growth.png",
            dpi=120, bbox_inches='tight')
