<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# The Architecture of AI Agents and LLM Systems
## Patterns, Approaches, and Engineering for Enterprise Automation

**Aleksandr Drobiazkin**

*This edition: July 2026. Sources reflect late 2025–mid-2026 (OWASP Agentic 2026, MCP under the Linux Foundation, the EU AI Act). Facts that can date are tagged with a year; where the industry is still in motion, the text hedges explicitly.*

---

# Preface

## Who this book is for

This book is addressed to the engineer who already knows how to design distributed systems—sagas, orchestration and choreography, DDD, event-driven architecture, security—and wants to add LLMs and agents to that toolbox **as architectural components**, not as magic. It does not rehash the fundamentals of programming or distributed systems; instead it explains what in the LLM world maps onto the distributed patterns you already know, what is genuinely new—and where the analogies break down.

## How this book is organized

The book fleshes out a structured learning path in depth: the path's stages become the book's parts.

The material is organized as a **pattern language**. A pattern is a named solution to a recurring problem in a particular context (the term goes back to Christopher Alexander; in software it was cemented by the Gang of Four and, for distributed systems, by Chris Richardson). Every significant pattern follows a single template:

> **Pattern template**
> - **Context**—the situation in which the problem arises.
> - **Problem**—the question the pattern answers.
> - **Forces**—competing concerns (latency vs. accuracy, cost vs. quality, autonomy vs. control).
> - **Solution**—the pattern itself.
> - **Mechanics**—how it works under the hood.
> - **Example**—a concrete implementation on a mainstream stack (e.g., Java/Spring, PostgreSQL, Kubernetes).
> - **Resulting Context**—what the pattern buys you and what you pay for it.
> - **When to Use / When Not To.**
> - **Related Patterns.**
> - **Sources**—the books and papers it draws on, for going deeper.

Terms are set in **bold on first appearance** and collected in the Glossary. Some terms carry so much weight that they get an article-length section of their own inside the relevant chapter (for example, "Attention," "Retrieval-Augmented Generation," "Prompt Injection").

The third tier of terminology support is the **In the Margins** block at the end of each chapter: short explanations of terms and mechanisms the chapter *uses* but that are unpacked elsewhere in the book—or outside it entirely. The in-text marker is an ordinary footnote; each explanation ends with correlation tags: "→ §N.M"—where the topic is covered in full; "⇐ Glossary"—there is a glossary entry; "≠"—a false friend (the term does not mean what intuition suggests). A footnote without tags is a self-contained definition with nowhere else in the book to point. Only prose counts as a use of a term; diagram labels do not get markers. The block's rule: no more than a dozen footnotes per chapter—anything that needs more deserves the Glossary or an article-length section.

**A convention on sources.** Wherever the text presents someone else's result, the end of the section cites the primary source (paper or book) where it can be verified and pursued further. Each topic is covered deeply enough in the text that the reference reads as a logical *continuation*, not a stub.

**Diagrams** are in Mermaid (they render in GitHub, VS Code, Obsidian, and mermaid.live).

**Structure.** The material unfolds across eight parts (twenty-six chapters) with five appendices: A—the linear-algebra substrate; B—a pattern index; C—the anatomy of a single trajectory (an end-to-end walkthrough of one request); D—the architect's preflight checklist; E—a consolidated bibliography.

**Scope.** The book concentrates on text-based LLM systems: multimodality (images, audio, video) comes up only where it intersects the core material (multimodal RAG, Chapter 7); voice agents and computer use stay outside the frame. The reason is not that these areas are immature (by mid-2026, browser and computer-use agents are a working replacement for RPA automation) but a separation of layers: both voice and UI control are *I/O modalities* on top of the same agent architecture this book dissects. Their specifics—the VAD/ASR/TTS pipeline and real-time latency in voice, coordinate grounding and resilience to layout changes in computer use—deserve dedicated sources; the foundation—the loop, tools, memory, security—is here. For a maturity yardstick on computer use, look to WebArena-class benchmarks (§17.5).

**On the format.** The pattern template above is the discipline's common inheritance, not this book's invention: Christopher Alexander gave it Context → Problem → Forces → Solution (*A Pattern Language*, 1977), the Gang of Four fixed it for software (*Design Patterns*, 1994), and Chris Richardson carried it into distributed systems (*Microservices Patterns*, 2018) — which is where this book's exposition takes its cue, so that every concept arrives not as a bare claim but with context, mechanics, an example, trade-offs, and connections to other patterns. Mechanics, Example, When to Use / When Not To, and Sources are this book's additions. Those names appear here for reference only: neither Chris Richardson nor Manning Publications is affiliated with this book, has reviewed it, or endorses it.

**A note on tools.** This book was written in Russian and translated into English by its author. Software assisted: an assistant (Claude, Anthropic) reviewed drafts, flagged errors and inconsistencies, and proposed alternative wordings. Every claim, every decision about structure, every source, and every sentence as published was chosen, written or rewritten, and verified by the author, who takes responsibility for all of it. The model is a tool, not a party: it holds no authorship and no rights, and Anthropic is not affiliated with this book and has not reviewed it. The full statement is in the NOTICE file at https://github.com/Drobiazkin/ai-agent-architecture.

---

## Demonstrating the format: the Orchestrator-Workers pattern

To show the catalog's depth right away, here is one pattern in full. It belongs in Part IV (Agents) but appears here as a specimen. Its structure is a close relative of the orchestrated saga, with the coordinator replaced by a language model.

> ### Pattern: Orchestrator-Workers
>
> **Context.** The automation task does not decompose into a fixed set of steps up front: the number and nature of the subtasks depend on the input. "Handle an incoming customer request," for example, may take one action (answer from the knowledge base) or five (check the order, consult policy, process a refund, notify the warehouse, reply to the customer)—and which ones is unknown until the request arrives.
>
> **Problem.** How do you execute a task whose decomposition is known only at runtime, while preserving reliability, observability, and the ability to roll back—the properties saga orchestration routinely provides?
>
> **Forces.**
> - A static graph (a workflow) is predictable and cheap, but it cannot handle dynamic decomposition.
> - A fully autonomous single agent handles the dynamics, but it is harder to control and debug.
> - Organizations demand auditing, idempotency, and compensations—regardless of who decided on a step: a human, a state machine, or an LLM.
>
> **Solution.** Introduce an **LLM orchestrator** that analyzes the task at runtime, dynamically generates a list of subtasks, and hands them out to **workers** (each worker is a separate LLM or tool call with a narrow responsibility). The orchestrator gathers the workers' results and synthesizes them into the final output. Architecturally this is **Saga orchestration** (in Richardson's terms), with two differences: (1) the coordinator is nondeterministic, and (2) the set and order of steps are determined dynamically rather than by a predefined state machine.
>
> **Mechanics.**
> ```mermaid
> flowchart TB
>   In["Incoming task"] --> Orch["LLM orchestrator<br/>runtime decomposition"]
>   Orch --> Plan["Subtask list (dynamic)"]
>   Plan --> W1["Worker 1<br/>tool/LLM"]
>   Plan --> W2["Worker 2"]
>   Plan --> W3["Worker N"]
>   W1 --> Synth["Orchestrator: result synthesis"]
>   W2 --> Synth
>   W3 --> Synth
>   Synth --> Out["Result"]
>   W2 -.failure.-> Comp["Compensation + retry/escalation"]
>   Comp -.-> Orch
> ```
> The orchestrator keeps a **step log** (much like an orchestrator-based saga log). Every worker step is made **idempotent** (keyed by task), given a **timeout**, and paired with a defined **compensation** in case of failure. An **iteration limit/budget** is mandatory; otherwise the orchestrator can loop forever (the coordinator's nondeterminism is a source of nontermination risk for the control loop—a failure mode that deterministic orchestration simply does not have).
>
> **Example.** Handling a customer request: at execution time the orchestrator identifies the necessary subtasks (check order status, consult policy, process a refund, notify the warehouse) and distributes them across workers. The step log, per-task idempotency keys, and compensating operations are implemented with standard saga-orchestration machinery. Irreversible subtasks (charging money, sending a notification) go through human confirmation (human-in-the-loop).
>
> **Resulting Context.** The pattern delivers the flexibility of dynamic decomposition while preserving auditing, idempotency, and rollback. The price: a nondeterministic plan (two runs on the same input can produce different decompositions, which complicates testing—see the Trajectory Evaluation pattern), higher cost (every worker is a model call), and latency.
>
> **When to Use.** The task genuinely requires dynamic decomposition, the number of subtasks varies, and there are reliability/audit requirements. **When Not To.** If the decomposition is fixed, take a static workflow (the Prompt Chaining pattern / a deterministic graph): it is cheaper, more predictable, and easier to debug. Do not add complexity before the task proves you need it.
>
> **Related Patterns.** Prompt Chaining (the static alternative); Routing (a special case—the orchestrator only picks a branch); Evaluator-Optimizer (for checking step quality); Human-in-the-Loop Gate (for irreversible actions, §10.6); Trajectory Evaluation (how to test a nondeterministic plan).
>
> **Sources.** Anthropic, "Building Effective Agents" (2024)—the orchestrator-workers pattern. Chris Richardson, *Microservices Patterns* (2018), Chapter 4—saga orchestration, compensating transactions, idempotency. V. Dibia, *Designing Multi-Agent Systems* (2025)—supervisor/handoff orchestration.

That is what every pattern in this book looks like. Now for the full plan—and the foundations.

---
