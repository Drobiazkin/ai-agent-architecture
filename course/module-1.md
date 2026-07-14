<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Module 1 — The Substrate by Hand: In Depth

*A companion to "Module 1" in the course overview (README.md). This is the most Python-heavy module after Module 7—keep `python-primer.md` open; every snippet comes with a syntax walkthrough. The work happens in Jupyter (`uv run jupyter lab`): the notebook here is a lab journal, a cell is an experiment.*

## 1.1 The tensor vocabulary of Appendix A—in a notebook

The goal: run every operation of §A.3 of the book by hand and *see the shapes*. A starter set of cells:

```python
import torch

x = torch.randn(1000, 4096)          # "the block's input": seq × d_model, random numbers ~N(0,1)
W = torch.randn(4096, 4096)          # the projection's weight matrix

y = x @ W                            # matmul; @ is the matrix-multiplication operator
print(x.shape, "@", W.shape, "->", y.shape)   # torch.Size([1000, 4096]) -> [1000, 4096]

# broadcast: add a row vector to every row of the table
b = torch.randn(4096)
print((x + b).shape)                 # [1000, 4096]—b got "stretched" across the rows

# batched matmul: the heads as a batch axis
h, d_head = 32, 128
Q = torch.randn(h, 1000, d_head)
K = torch.randn(h, 1000, d_head)
scores = Q @ K.transpose(-2, -1)     # transpose(-2,-1)—swap the LAST TWO axes = Kᵀ per head
print(scores.shape)                  # [32, 1000, 1000]—there it is, seq² per head (§1.4 of the book)

# the same operation via einsum—check it against the letter-by-letter reading in §A.3
scores2 = torch.einsum("hqd,hkd->hqk", Q, K)
print(torch.allclose(scores, scores2))   # True—this is ONE AND THE SAME contraction
```

**Syntax walkthrough** (→ primer sections): `import torch`—§9; `x.shape`—a tuple attribute holding the shape, read as `seq × d_model` from §1.4 of the book; `@`—the overloaded matmul operator (Java has no operator overloading; Python does, and NumPy/PyTorch stand on it); the negative axis indices in `transpose(-2, -1)`—"from the end," like the slices in §3 of the primer; `torch.allclose(a, b)`—an element-wise comparison with a tolerance (floats are not compared with `==`).

**Self-check exercise:** for every line, write down the expected result shape on paper *before running it*, then compare. Got it wrong—go back to the rule `(a×b)·(b×c)→a×c` from §1.4 of the book.

## 1.2 The token calculator

We're pricing your own corpus. The tokenizer is `tiktoken` (fast, local) as an approximation; the exact numbers for your provider come from its token-counting API:

```python
# uv add tiktoken
import glob, tiktoken

enc = tiktoken.get_encoding("o200k_base")     # a ~200k vocabulary; check the exact encoder against your model
stats = []
for path in glob.glob("../corpus/*.md"):
    text = open(path).read()
    n_tok, n_chars = len(enc.encode(text)), len(text)
    stats.append((path, n_tok, n_chars / n_tok))   # the third number is characters per token

total = sum(n for _, n, _ in stats)
print(f"documents: {len(stats)}, total tokens: {total}")
print(f"characters/token (median): {sorted(s[2] for s in stats)[len(stats)//2]:.2f}")

for price_in in (0.25, 1.0, 3.0):             # $/1M input—three tiers
    print(f"corpus indexing at ${price_in}/M: ${total * price_in / 1e6:.4f}")
```

**Syntax walkthrough:** `for _, n, _ in stats`—tuple unpacking with `_` for the fields you don't need (§3 of the primer); `sorted(...)[len(stats)//2]`—the median via a sort, `//`—integer division; `:.2f` and `:.4f` in f-strings—the "two/four decimal places" format (§2).

**Fertility and the price multiplier:** take one document and translate a paragraph into English (with the model). The book (§1.2) defines fertility as the average number of tokens **per word**, so it is computed for each language separately: `len(enc.encode(text)) / len(text.split())`—for ru and for en (≈ 1 for English, noticeably higher for Cyrillic). The ratio `len(enc.encode(ru)) / len(enc.encode(en))` is no longer fertility but the **ru/en cost multiplier**: a consequence of fertility, but with the differing word counts of the translation mixed in. That multiplier is exactly what a Russian-language system costs on your own text.

## 1.3 A GPT block following Raschka—type it by hand

The guide is chapters 3–4 of his book; here there is only the self-attention skeleton, so that you know where you're headed (type it yourself, don't copy—that's the rule of the exercise). There is no training in Module 1—chapters 3–4 take you exactly as far as a forward pass on untrained weights; the training loop and the optimizer come further along in his book (chapter 5; Raschka introduces the data loading earlier—check the exact numbers against your edition's table of contents), and you'll fine-tune by hand in Module 7. The block here is an object to take apart, not a generator of meaningful text:

```python
import torch.nn as nn

class CausalSelfAttention(nn.Module):                # nn.Module—the base class of every layer
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()                            # ≈ super(); mandatory
        self.n_heads, self.d_head = n_heads, d_model // n_heads
        self.Wq = nn.Linear(d_model, d_model, bias=False)   # this is the very "projection" of §1.4 of the book
        self.Wk = nn.Linear(d_model, d_model, bias=False)
        self.Wv = nn.Linear(d_model, d_model, bias=False)
        self.Wo = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x):                             # forward = the "forward pass"; called as layer(x)
        B, T, C = x.shape                             # batch, seq, d_model
        q = self.Wq(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)  # → B,h,T,d_head
        k = self.Wk(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        v = self.Wv(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) / self.d_head ** 0.5      # step 2 of the trace in §1.4 of the book
        mask = torch.tril(torch.ones(T, T, dtype=torch.bool, device=x.device))
        att = att.masked_fill(~mask, float("-inf"))   # the causal mask: the future is not visible
        att = torch.softmax(att, dim=-1)              # step 3
        out = (att @ v).transpose(1, 2).reshape(B, T, C)          # step 4: assemble the heads
        return self.Wo(out)                           # step 5
```

**Syntax walkthrough:** `class CausalSelfAttention(nn.Module)`—inheritance (§6 of the primer); `self.Wq = nn.Linear(...)`—fields are created in the constructor by assignment; `view(...)`—a reshape without copying (the "plumbing" from §A.3 of the book); `d_head ** 0.5`—`**` is exponentiation, here the √d_head from step 2 of the trace; `~mask`—an element-wise logical NOT; `float("-inf")`—the very −∞ of logit masking (§5.3 of the book—yes, it's one and the same trick!).

**The module's DoD check**—in writing, with the line numbers of *your* code: where T×T (O(n²)) is born, and which tensors would have to be recomputed without a KV-cache (§1.6 of the book). The right answer points at the line with `q @ k.transpose(...)` and at k/v as the cacheable ones.

## 1.4 An MoE layer in place of the FFN

```python
class MoEFFN(nn.Module):
    def __init__(self, d_model: int, d_ff: int, n_experts: int = 4, top_k: int = 2):
        super().__init__()
        self.router = nn.Linear(d_model, n_experts)   # §1.5 of the book: the router is just a linear layer
        self.experts = nn.ModuleList(
            nn.Sequential(nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model))
            for _ in range(n_experts))
        self.top_k = top_k

    def forward(self, x):
        logits = self.router(x)                              # B,T,n_experts
        weights, idx = torch.topk(logits, self.top_k, dim=-1)  # the top-k experts for EVERY token
        weights = torch.softmax(weights, dim=-1)
        out = torch.zeros_like(x)
        for k in range(self.top_k):                          # teaching-grade (slow) routing
            for e in range(len(self.experts)):
                sel = idx[..., k] == e                       # a mask of the tokens that picked expert e
                if sel.any():
                    out[sel] += weights[..., k][sel].unsqueeze(-1) * self.experts[e](x[sel])
        return out
```

**A counting exercise:** `sum(p.numel() for p in moe.parameters())`—total; active = the router + top_k experts. Compare against a dense FFN with the same d_ff; FLOPs/token—by 2·(parameters in play) from §23.4 of the book. **Walkthrough:** `ModuleList(... for _ in range(...))`—a generator in the constructor (§3, §12 of the primer); `idx[..., k]`—`...` means "all the preceding axes"; `x[sel]`—boolean indexing: select rows by a mask.

## 1.5 Decoding strategies: the experiment from §1.7 of the book

50 runs of a single JSON-extraction task at T=0 and T=1 (Ollama, locally—free):

```python
import json, httpx

PROMPT = "Extract JSON {\"city\": str, \"days\": int} from the text. Text: \"We are going to Kazan for 3 days\". JSON only."

def run(temp: float, n: int = 50) -> tuple[int, set[str]]:
    valid, contents = 0, set()
    for _ in range(n):
        r = httpx.post("http://localhost:11434/api/generate", timeout=120,
                       json={"model": "qwen3:4b", "prompt": PROMPT, "stream": False,
                             "options": {"temperature": temp}})
        text = r.json()["response"].strip()
        try:
            json.loads(text); valid += 1; contents.add(text)
        except json.JSONDecodeError:
            pass
    return valid, contents

for t in (0.0, 1.0):
    v, c = run(t)
    print(f"T={t}: valid {v}/50, unique answers {len(c)}")
```

**Walkthrough:** `-> tuple[int, set[str]]`—the function returns a tuple, and the caller unpacks it as `v, c = run(t)` (§3, §5 of the primer); `try/except json.JSONDecodeError: pass`—"catch and ignore" (§7); `set` accumulates only the unique answers—the size of the set is the measure of spread. What to expect: T=0 will give a `len(c)` greater than 1—nondeterminism lives below sampling; why—§2.4 of the book.

## 1.6 The KV-cache: calculation versus measurement

The calculation follows the formula in §1.6 of the book (for your own local model, take the parameters from `ollama show qwen3:8b`):

```python
def kv_bytes(n_layers, n_kv_heads, d_head, seq, bytes_per=2):   # 2 bytes = FP16
    return 2 * n_layers * n_kv_heads * d_head * seq * bytes_per # the leading factor 2—K and V

print(f"{kv_bytes(36, 8, 128, 8192) / 2**20:.0f} MiB for 8k of context")
```

The measurement: `ollama ps` before and after a request with a short (~50 tokens) and a long (paste in a document of several thousand tokens) context—the difference in occupied memory is the price of the KV. Explain the divergence from the calculation in writing (cache quantization? GQA—n_kv_heads smaller than the number of heads?—both factors are named in §1.6 of the book).

## 1.7 The DoD checklist

- [ ] The operation-vocabulary notebook: shapes predicted before running, einsum matched matmul (`allclose`).
- [ ] The token calculator: a table over the corpus + fertility for ru and en + the ru/en cost multiplier + the cost of indexing at three tiers.
- [ ] Your own GPT block assembled (per Raschka, chapters 3–4) + **a written analysis of O(n²)/KV with references to the lines of your own code**.
- [ ] MoE: a total/active/FLOPs table against dense + the recommendation memo (the module's artifact).
- [ ] Decoding: the shares of valid JSON at T=0/T=1 and the conclusion about nondeterminism at T=0.
- [ ] The KV-cache: calculation, measurement, an explanation of the divergence.
