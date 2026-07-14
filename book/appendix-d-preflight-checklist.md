<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Appendix D. The Architect's Preflight Checklist

One page to read before an LLM system goes to production—the book distilled into a set of checks. Every item points to the section that justifies it; an unchecked box is a risk you took on deliberately, not one you forgot.

**Contracts**
- [ ] The feature's NFR specification is filled in: quality, latency, cost, degradation (§2.7)
- [ ] The output schema is declared, the post-hoc validator is on, reask is configured (§5.4–5.5)
- [ ] A timeout on every network call; retries with jitter; a fallback model or degradation (§2.5)
- [ ] The agent's actions are idempotent on an operation key (§2.5, §10.4)

**Context and data**
- [ ] Untrusted content is structurally isolated and marked as data (§4.6)
- [ ] The window budget is allocated explicitly and the reserve for the output is accounted for (§1.8); compaction and memory kick in at a threshold (§4.2, §4.4–4.5)
- [ ] PII is masked before indexing and before it reaches the provider; telemetry is redacted (§25.4, §18.6)
- [ ] The right to erasure can actually be honored everywhere the data settles (§25.4)

**Actions and security**
- [ ] The tool set is curated; risk metadata is filled in (§12.3, §12.5)
- [ ] Authorization runs with the user's permissions, at the point of execution (§12.5)
- [ ] The tools *as a set* have been checked against the lethal trifecta; the rule of two is satisfied or a gate is in place (§12.5, §19.4)
- [ ] Third-party MCP servers are untrusted: OAuth, pinning of approved tool descriptions (§15.7)
- [ ] A human gate on the irreversible; a gate timeout means a safe rejection (§10.6)
- [ ] Iteration and token limits per step and per task (§10.5)
- [ ] The defense-in-depth checklist has been worked through in full (§19.7), including the dual-LLM quarantine for high-risk loops and the sandbox for code execution (§19.6)

**Retrieval (if you have RAG)**
- [ ] Access control is applied at retrieval; recall has been checked with the filters on (§8.6–8.7)
- [ ] A re-indexing plan for when the embedder changes; a strategy for deleting from the index (§8.8, §8.3)

**Evaluation and observability**
- [ ] The golden set exists, is versioned, and includes "unanswerable questions" (§9.3)
- [ ] The judge is validated against humans (kappa) and its version is pinned (§17.4, §9.4)
- [ ] An eval gate sits in CI on changes to the prompt/model/tools (§17.8)
- [ ] Traces are written to semconv; cost is attributed by feature and tenant (§18.3–18.5, §20.6)
- [ ] The sample size behind release decisions is computed, not guessed (§17.7)

**Organization**
- [ ] The system is entered in the registry with a risk class and an owner (§25.2, §25.5)
- [ ] Prompts are in the registry, each with an owner and a link to the golden set (§25.2)
- [ ] Routes to providers are DPA-approved only, and go through the gateway (§25.3)
- [ ] HITL review is planned for as a workload; the rubber-stamping metric is on (§25.7, §10.6)
- [ ] The pilot has a baseline, a target lift, and a stopping criterion (§25.6)

---
