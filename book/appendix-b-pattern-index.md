<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Appendix B. Pattern Index

Every pattern in the book in a single list, for reference. The full card (Context → Problem → Forces → Solution → Mechanics → Resulting Context → When → Related → Sources) is in the section listed.

**Resilience and call economics**

| Pattern | Problem it solves | Where |
|---|---|---|
| Model Routing / Cascade | Pay frontier prices only for frontier tasks | §2.2, §20.3 |
| Fallback Model | Survive a provider outage or degradation | §2.5 |
| AI Gateway | Apply policies (access, budgets, PII, audit) to every call at once | §25.3 |

**Managing context and output**

| Pattern | Problem | Where |
|---|---|---|
| Context Compaction | A long session won't fit the window; truncate and you lose the decisions | §4.4 |
| Sliding Window · Externalized State · Context Caching | Mini-patterns for the window budget | §4.4 (catalog) |
| Retrieval-based Memory (episodic/semantic/procedural) | State beyond the window, retrieving what's relevant | §4.5 |
| Validate-then-Retry (Reask) | Invalid output with no access to the logits | §5.5 |
| Two-step generate-then-format | A rigid schema strangles reasoning | §5.5 |

**Retrieval (RAG)**

| Pattern | Problem | Where |
|---|---|---|
| Naive RAG | The baseline: ground the answer in a corpus | §7.2 |
| Hybrid Search | Semantic search is blind to exact terms, lexical search to meaning | §7.3 |
| Reranking | The right document came back, just not in the top-k | §7.4 |
| Query transformation (rewriting, HyDE, decomposition) | A user's question ≠ a good search query | §7.5 |
| GraphRAG | Questions about relationships, not about similarity | §7.7 |
| Agentic RAG | One search pass isn't enough | §7.8 |
| Adaptive RAG | Not every query needs the expensive pipeline | §7.9 |

**Agents and orchestration**

| Pattern | Problem | Where |
|---|---|---|
| Prompt Chaining | A fixed sequence of steps | §11.2 |
| Routing | Heterogeneous input with distinguishable categories | §11.3 |
| Parallelization (Sectioning / Voting) | Independent parts; reliability through redundancy | §11.4 |
| Orchestrator-Workers | The decomposition is known only at runtime | §11.5 (demo—Preface) |
| Evaluator-Optimizer | Iterative quality when a criterion exists | §11.6 |
| Human-in-the-Loop Gate | An irreversible action from a nondeterministic component | §10.6 |

**Reasoning strategies** (loop mechanisms, not cards): ReAct—§13.3; Plan-and-Execute—§13.4; Reflection/Reflexion—§13.5; Tree-of-Thought—§13.6. Coordinating multi-agent systems (supervisor / handoff / network / hierarchical)—§14.2.

**Organizational**

| Pattern | Problem | Where |
|---|---|---|
| Prompt Registry | Prompts need the lifecycle of code | §25.2 |
| AI Gateway (governance role) | See above | §25.3 |

Cross-cutting defenses (not cards, but named practices): isolating untrusted content—§4.6; the rule of two and taint-tracking—§12.5; the dual-LLM/quarantine loop and the execution sandbox—§19.6; autonomy levels L0–L3—§10.7.

---
