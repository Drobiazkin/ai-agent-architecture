<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Glossary

*Terms marked (→ Chapter N) get a section of their own in the chapter named.*

**The model and its internals**
- **Token**—the smallest unit the model operates on: a subword from the BPE vocabulary, not a character and not a word. The unit of billing and of limits. (→ Chapter 1)
- **Embedding**—a dense vector of fixed dimensionality that encodes meaning; closeness in meaning ≈ closeness of vectors (cosine). One word, two different things: the internal vector of a token inside the model itself, and the vector of a whole fragment produced by a separate embedding model for search; they live on different hardware and are not interchangeable (§1.3). (→ Chapter 1)
- **Attention**—the mechanism that lets each token "look" at the others in a weighted way while computing its own representation; the core of the transformer. (→ Chapter 1)
- **Transformer**—the attention-based neural-network architecture that modern LLMs are built from.
- **Dense model**—a model in which every parameter is active for every token.
- **MoE (Mixture of Experts)**—a sparse model in which a router activates only a subset of experts per token; large total size at small active compute. (→ Chapter 1)
- **KV-cache**—the cache of attention keys/values, kept so they need not be recomputed during autoregression; the biggest consumer of memory after the weights. (→ Chapter 1)
- **Prefill / Decode**—the two phases of inference: processing the prompt in parallel and generating sequentially. (→ Chapter 1)
- **Logits**—the model's raw (pre-softmax) scores for every token in the vocabulary.
- **Temperature / Top-p / Top-k**—decoding parameters that control how random the token choice is; the "determinism knob." (→ Chapter 1)
- **Context window**—the maximum number of tokens the model processes at once; a finite budget. (→ Chapter 1)
- **Hallucination**—a confidently generated but false statement; a consequence of predicting plausibility rather than truth. (→ Chapter 1)
- **RoPE (Rotary Position Embedding)**—encoding position by rotating the Q/K vectors: attention sees relative positions; the basis of context-extension techniques. (→ Chapter 1)
- **TTFT / TPOT**—time-to-first-token and time-per-output-token: the two components of generation latency, corresponding to the prefill and decode phases. (→ Chapter 2)
- **Reasoning model**—a model trained (with RLVR) to spend compute on a long internal chain of reasoning before it answers; the reasoning is billed as output tokens. (→ Chapter 13)

**Interface**
- **Prompt**—the model's input; in production, not the text of the query but the whole assembled context.
- **System prompt**—the part of the prompt that sets the invariant of behavior; a soft contract. (→ Chapter 3)
- **Few-shot**—setting format and behavior by examples placed right in the prompt.
- **Context engineering**—the discipline of assembling the right content into the window at every step. (→ Chapter 4)
- **Structured output**—forcing the model onto an output schema (JSON/grammar). (→ Chapter 5)
- **Prompt caching**—caching the static prefix of the prompt for the sake of cost and latency.
- **Constrained (grammar) decoding**—masking the tokens the grammar disallows at each step of generation; guarantees the structure of the output (not its correctness). (→ Chapter 5)

**Grounding**
- **RAG (Retrieval-Augmented Generation)**—feeding retrieved data into the context instead of, or in addition to, parametric knowledge. (→ Chapter 6)
- **Bi-encoder**—a model that encodes query and document independently (fast retrieval).
- **Cross-encoder / Reranker**—a model that scores the [query, document] pair jointly (precise rescoring). (→ Chapter 7)
- **Chunking**—splitting documents into fragments for indexing. (→ Chapter 7)
- **Hybrid search**—combining dense (vector) and sparse (BM25) search. (→ Chapter 7)
- **ANN / HNSW**—approximate nearest-neighbor search and its popular index structure. (→ Chapter 8)
- **BM25**—the classic sparse (lexical) ranking function: TF-IDF with frequency saturation and length normalization; the lexical half of hybrid search. (→ Chapter 7)
- **RRF (Reciprocal Rank Fusion)**—merging several ranked lists by reciprocal ranks; the standard way to combine dense and sparse results. (→ Chapter 7)
- **GraphRAG**—retrieval over a knowledge graph (entities, relations, communities) rather than over independent fragments. (→ Chapter 7)
- **Faithfulness**—the answer's fidelity to the retrieved context (whether anything was made up); an axis of quality orthogonal to the quality of retrieval. (→ Chapters 6, 9)

**Agents**
- **Agent**—a system with an LLM as the decision-making core, acting in an observe→decide→act loop; always a pair, "LLM + harness." (→ Chapter 10)
- **Harness (agent harness)**—the deterministic application code around the model: it assembles the context, executes tool calls, carries the state of the loop, and enforces budgets and gates. (→ §10.2)
- **Workflow**—a predefined graph of steps with LLM calls (as opposed to an agent).
- **Tool calling / Function calling**—the mechanism in which the model produces a structured request to call a function and the harness executes it. (→ Chapter 12)
- **Code execution (code mode)**—presenting tools as a code API: the model writes code that composes the calls in a sandbox, instead of a sequence of JSON calls. (→ §12.6)
- **Skill (Agent Skills)**—a versioned artifact of procedural knowledge (SKILL.md: instructions + resources) with progressive disclosure; the model reads it, unlike a tool, which the harness executes. (→ §12.6)
- **ReAct**—the pattern that interleaves reasoning and action (Thought→Action→Observation). (→ Chapter 13)
- **Saga orchestration**—coordinating steps from a center, with compensations; the basis of the Orchestrator-Workers pattern.
- **Human-in-the-Loop Gate (human-gate)**—a deterministic gate requiring human confirmation before an irreversible or consequential agent action. (→ Chapter 10)

**Integration**
- **MCP (Model Context Protocol)**—an open standard (JSON-RPC) for connecting agents to tools and data. (→ Chapter 15)
- **A2A (Agent2Agent)**—an open protocol for agents to interact with one another (Agent Card, tasks with a lifecycle); complementary to MCP. (→ Chapter 15)

**Production**
- **Eval**—a measurable check on the quality of a probabilistic system; it replaces a boolean assert with a distribution. (→ Chapter 17)
- **LLM-as-judge**—using an LLM to score another LLM's output against a rubric. (→ Chapter 17)
- **Trajectory evaluation**—scoring every step of an agent's trajectory, not just the final answer. (→ Chapter 17)
- **Prompt Injection**—an attack that exploits the failure to separate instructions from data in a single channel. (→ Chapter 19)
- **Excessive Agency**—an agent holding an excess of permissions/functions/autonomy (agency—in this book these are synonyms, §10.7); an OWASP class of risks. (→ Chapter 19)
- **Guardrails**—deterministic checks on the input and the output around a probabilistic core. (→ Chapter 19)
- **Non-human identity (NHI)**—a machine account (service, bot, agent); the basis of an agent's identity and of delegating its authority. (→ §15.7)
- **Shadow AI**—using LLMs outside the organization's registry and perimeters: personal keys, extensions, "gray" automations. (→ §25.2)

**Serving and inference**
- **Quantization**—representing weights/activations/cache at reduced precision (int8, 4-bit, FP8/FP4) for the sake of memory and throughput. (→ Chapter 22)
- **PagedAttention**—organizing the KV-cache in pages, on the model of OS virtual memory: it removes fragmentation and lets common prefixes be shared. (→ Chapter 22)
- **Continuous batching**—dynamically slotting requests into the batch as slots free up; the main lever on accelerator utilization. (→ Chapter 22)
- **Speculative decoding**—a draft model proposes several tokens, the target model verifies them in one parallel pass; speeds up decode without changing the distribution. (→ Chapter 22)

**Training**
- **Fine-tuning**—further training of a model for form/style/schema (not for facts that change). (→ Chapter 21)
- **LoRA / QLoRA**—parameter-efficient fine-tuning with low-rank adapters (+ a 4-bit base). (→ Chapter 21)
- **DPO**—direct preference optimization; a replacement for classic RLHF. (→ Chapter 21)
- **Scaling laws**—empirical relationships tying quality to model size and data volume (Chinchilla). (→ Chapter 23)
- **RLHF**—reinforcement-learning fine-tuning against a reward model trained on human preferences. (→ Chapter 21)
- **RLVR**—RL on verifiable rewards (running tests, checking against a reference); the mechanism behind training reasoning models. (→ Chapter 13)
- **PPO / GRPO**—the RL algorithms for the optimization step in RLHF/RLVR: PPO with a separate value model to estimate advantage, GRPO with a group baseline in its place. (→ Chapters 13, 21)
- **Knowledge distillation**—training a compact "student" to reproduce the output distribution or the reasoning of a "teacher." (→ Chapter 21)

---
