# The Architecture of AI Agents and LLM Systems

**An engineering book on building LLM systems you actually control — free, open, and written for engineers who ship.**

*by Aleksandr Drobiazkin · English and Russian editions*

**Contact:** [aleksandr.drobiazkin@gmail.com](mailto:aleksandr.drobiazkin@gmail.com) · [LinkedIn](https://www.linkedin.com/in/aleksandr-drobiazkin-501bab263)

[![License: CC BY-SA 4.0](https://img.shields.io/badge/Text-CC%20BY--SA%204.0-blue.svg)](LICENSE)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-green.svg)](LICENSE-CODE)

Patterns, approaches, and engineering for enterprise automation — 8 parts, 26 chapters, 5 appendices, ~258 pages in print, plus a hands-on companion course. No hype, no "prompt tips," no vendor marketing. Mechanisms, trade-offs, and numbers.

---

## Why this book exists

There is a version of the next decade where building anything intelligent means renting it, one API call at a time, from three companies — and where the engineers who build on top of that stack cannot explain what happens between their JSON request and the answer that comes back.

That is not a licensing problem. It is a **competence** problem, and it is the only one you can actually solve.

**Digital independence is not about refusing to use hosted models. It is about never being unable to leave.** An engineer who knows how attention scales, what a KV-cache costs, when a retrieval pattern beats fine-tuning, how to serve an open model on their own hardware, and what an eval suite has to prove before a release ships — that engineer *chooses* their stack. An engineer who knows only an SDK gets whatever the pricing page decides next quarter.

This book was written to move as many people as possible from the second group into the first. That is the whole cause. It is why the book is free, why it stays free, why it is CC BY-SA, and why the entire Part VII exists to teach you to fine-tune, serve, and pre-train models yourself — the chapters a vendor would never write for you.

If that outcome is worth something to you, [there's a way to help](#support-the-work).

---

## What's inside

The material is organized as a **pattern language**. Every significant pattern arrives with a fixed template — Context, Problem, Forces, Solution, Mechanics, Example, Resulting Context, When to Use / When Not To, Related Patterns, Sources. The template is the discipline's common inheritance — Alexander to the Gang of Four to Chris Richardson's *Microservices Patterns*, which is where this book's exposition takes its cue; the last four rubrics are this book's additions. Named for reference only: neither Chris Richardson nor Manning Publications is affiliated with this book, has reviewed it, or endorses it. Nothing is asserted without the mechanism underneath it.

| Part | What it covers |
|---|---|
| **I. The model as a component** | Tokenization, embeddings, attention, dense vs. MoE, the generation loop, decoding strategies, context-window failure modes, hallucination — plus the economics: cost, latency, determinism, reliability, hosted vs. self-host |
| **II. The interface to the model** | Prompt engineering as contract design; context engineering and its pattern catalog; structured output and constrained decoding |
| **III. Grounding: RAG** | The retrieval-pattern ladder (naive → hybrid → reranking → GraphRAG → agentic → adaptive), vector indexes and ANN internals, chunking, and RAG evaluation |
| **IV. Action: agents** | The agent as a distributed system; the pattern catalog (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer); tool calling as contract; memory and reasoning strategies; multi-agent systems and a full failure taxonomy |
| **V. Integration** | Model Context Protocol (MCP) end to end; assembling the stack on the JVM |
| **VI. Production** | Building an eval system; observability and OpenTelemetry GenAI conventions; security — prompt injection, the lethal trifecta, defense in depth; cost and latency engineering |
| **VII. Your own models** | Fine-tuning (LoRA, QLoRA, DoRA, RLHF/DPO, distillation); deploying open models (PagedAttention, continuous batching, quantization, speculative decoding); pre-training and scaling laws |
| **VIII. Synthesis** | A reference architecture, organizational adoption and governance, and a full worked example with an architecture decision record package |

**Appendices:** the linear-algebra substrate · a pattern index · the anatomy of a single agent trajectory · an architect's preflight checklist · a consolidated bibliography.

Sources are cited at the point of use, not dumped at the end. Facts that can date carry a year. Where the industry is still in motion, the text says so instead of guessing.

## Who it's for

The engineer who already designs distributed systems — sagas, orchestration and choreography, DDD, event-driven architecture, security — and wants LLMs and agents in that toolbox **as architectural components, not as magic**.

It does not re-teach programming or distributed systems. It explains what in the LLM world maps onto patterns you already know, what is genuinely new, and — most usefully — **where the analogies break down**.

## Read it

| Format | Path |
|---|---|
| Markdown, one file per chapter | [`book/`](book/) |
| Single-file HTML | build it — see [`build/README.md`](build/README.md) |
| PDF | build it — see [`build/README.md`](build/README.md) |

**Russian edition / Русская версия** — the full book and course in [`ru/`](ru/) (Markdown source, HTML, PDF). Both editions are the author's own; see [`PROVENANCE.md`](PROVENANCE.md).

Diagrams are Mermaid and render natively on GitHub. The English edition's figures are generated from source — the scripts are in [`tools/figures/`](tools/figures/); they are English recreations of the Russian edition's figures. Every figure is plotted from published data, with the source named in the figure itself.

## The companion course

[`course/`](course/) is a hands-on practicum that turns the book into a working system: nine modules from a local model on your own hardware through RAG, agents with saga discipline, MCP, evals, fine-tuning, and a capstone architecture. Every module has a Definition of Done you can check yourself. A Python primer is included for JVM engineers.

---

## Support the work

This book took a very long time to write and it is given away in full — no paywall, no email gate, no "premium tier," no sponsor deciding which chapter is too honest to publish. **It stays that way.**

If it saved you a week of research, prevented one production incident, made an architecture review go quietly, or taught you something a course would have charged for — you can fund the next revision:

| | Address |
|---|---|
| **Bitcoin** | `bc1qprm2x8rafkw5qqpnt5vprrww5q6wdkmkpcysjl` |
| **Ethereum** (ERC-20) | `0x238017d8E60645890FcE7db5E81f75aefdbE391A` |
| **USDT** (TON) | `UQCexQpgOlcJ0mNR3wtdy5kwr8N5kRofztFFrNv-xag7Z59v` |
| **Tron** (TRC-20) | `TBDQhRiFUGJjQJB996SsMP58sYfJmUH99d` |
| **Solana** | `2P7qnD6LDMmQBgNx9vvMV3QPNQmSYhdqSfMkNZn3Pipt` |

**What it funds:** keeping the book current in a field that reshapes itself every six months — new chapters, revised numbers, re-verified sources, and the compute to actually test what gets claimed. Every revision lands here, free, for everyone.

**Non-financial support matters just as much** — and is genuinely more valuable than a small donation: star the repo, fix an error, open an issue when something is wrong, translate a chapter, or hand the book to an engineer who needs it. Corrections are the highest-value contribution there is: an error found is an error a thousand readers never hit.

> [!IMPORTANT]
> **Please check where you are sending from.** The receiving exchange rejects transfers originating from sanctioned platforms, and rejected funds can be frozen or lost — this is a practical warning, not a political statement.
>
> Do not send from: **Garantex, Grinex, Bitpapa, Suex, Chatex, Cryptex, PM2BTC, HTX (formerly Huobi), Rapira, ABCEX, Exnode (Exnode Pay), USDKG, EXMO, Aifory Pro, Nobitex, Wallex, Bitpin, Ramzinex** — or any platform designated under the **UN Security Council** sanctions list, the **OFAC** list (U.S. Department of the Treasury), or the **EU consolidated financial sanctions** list.
>
> Sending from a mainstream, compliant exchange or a self-custodial wallet is fine. If in doubt, use a self-custodial wallet.

---

## License

| What | License |
|---|---|
| Prose, figures, `mermaid` diagrams | [CC BY-SA 4.0](LICENSE) |
| Fenced code blocks, `tools/`, `build/` | [MIT](LICENSE-CODE) |
| Third-party assets embedded in the built HTML | their own — see [`NOTICE`](NOTICE) |

**The boundary is exactly the fence.** A triple-backtick block tagged with a language (`python`, `java`, `sql`, `bash`, `yaml`, `xml`, `json`) is MIT, comments inside it included. Everything else is CC BY-SA 4.0 — the prose, the tables, the formulas, and the `mermaid` blocks, which are diagrams that happen to be written as text. Every source file under `book/` and `course/` carries that split as an SPDX header, so it travels with the file if you take a single chapter.

**In plain terms:** read it, print it, teach from it, translate it, quote it, build a course on it — commercially or not. Two conditions: **credit the author**, and if you publish something built on the text, **publish it under the same license**. The book cannot be taken closed. That is the point of ShareAlike, and it is the license doing the same job the book argues for: what is open stays open.

**One asymmetry worth knowing before you reuse this.** CC BY-SA 4.0 accepts incoming material under CC BY, CC0, the public domain, and CC BY-SA 4.0 itself — but it accepts **nothing** under a NonCommercial (NC) or NoDerivatives (ND) license. Dropping an NC-licensed figure into a translated chapter breaks the license outright, not merely its spirit: §2(a)(5)(B) forbids adding restrictions this license does not carry. Nothing of the sort is incorporated here.

Attribution: **Aleksandr Drobiazkin** — © 2026. The dates on which the manuscripts existed in a given state are cryptographically attested; see [`PROVENANCE.md`](PROVENANCE.md).

## Contributing

Corrections, precision, and sourced counter-evidence are all welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). The bar is the book's own: **the source is the only oracle.** Claims about mechanism need a primary reference; numbers need somewhere they can be checked.
