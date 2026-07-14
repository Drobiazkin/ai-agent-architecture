<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Module 8 — Capstone: In Depth

*A companion to "Module 8" in the course overview (README.md). There is almost no code here—everything was built in Modules 2–7; the capstone is assembly, acceptance, and evidence. The new work is integration and documentation, and it is harder than it looks.*

## 8.1 Assembling the end-to-end scenario (Chapter 26)

The target flow for a single request:

```
user → gateway (Module 6: authentication, quota, routing §6.7, PII on the way out §6.8)
   → agent (Module 4: harness, budgets, progress detection)
      → retrieval (Module 3: hybrid + rerank, RLS by Keycloak roles)
      → tools over MCP (Module 5: scopes, token exchange)
      → human-gate (Module 4) on createTicket and on any write
   → answer + a full trace in Langfuse (Module 6)
```

The assembly order runs from the gateway inward (each step is checked by its own smoke test from the corresponding module):
1. Every client goes through the gateway (the Module 6 DoD already required it; check that nothing has broken off since).
2. The Module 4 agent gets its tools *only* through its own MCP client to the Module 5 server (§5.1 already moved the harness onto it; check on the assembled system that no direct service calls are left—otherwise scopes and pinning protect nothing).
3. The RLS context flows from the user's JWT through token exchange down to the SQL (`SET LOCAL`)—verify with a trace that the clearance in the span matches the role.
4. The human-gate sits on every irreversible tool (mark them in the description—as `createTicket` does in Module 5—and add an automated test: "an irreversible tool is never called without a gate").
5. Optional: the field extractor from Module 7 (through vLLM, or results captured earlier)—as a cheap first step in the classification pipeline.

## 8.2 Acceptance #1: the preflight checklist (Appendix D)

Work through all 27 items. The honesty rules:
- an item is closed = there is an **artifact** (a test, a dashboard, a config, a document)—"done in my head" does not count;
- an item is not closed = **a risk accepted in writing**: why it is acceptable for a training rig and what production would require (this is fine: some of the D items are overkill for a rig—but a decision has to be a decision, not a default).

The output: an "item → artifact/risk" table in the capstone README.

## 8.3 Acceptance #2: your own "Appendix C"

Capture a full trace of one representative conversation (2–3 turns with retrieval, a tool, and the gate):
1. **The sequence flow**—reconstruct a diagram at the level of Appendix C (mermaid) from the Langfuse spans.
2. **The span tree**—a screenshot or an export, with durations.
3. **A table of tokens and cost by turn**—in / out / cached, the cost of each call, the total for the conversation.

Compare against the book's reference: where is your conversation more expensive or slower (the reference runs ~$0.0065 and turn-1 ≈ 7.8 s—your numbers will be different, and what is interesting is *why*: a different model? no cache? an extra agent turn?). A difference you can explain is a sign of understanding; a difference you cannot explain is material for analysis.

## 8.4 Acceptance #3: the ADR package

8–12 decisions in the §26.3 format, your own counterpart to §26.4. The mandatory minimum: the forks you *actually walked through* in the modules (you have the numbers, so the ADR will be honest):

| ADR | The fork | Numbers from the module |
|---|---|---|
| Model and routing | the §6.7 cascade | route shares, error costs |
| The rung on the RAG ladder | where you stopped | the Module 3 table |
| Workflow vs agent | step by step through the scenario | the Module 4 §4.5 table |
| Where the human-gate goes | irreversible actions | the Module 4 gate metrics |
| OWASP risks → countermeasures | the Module 6 red-team | the attack report |
| Self-host vs hosted | the Module 7 extractor | the break-even note |
| The PII containment loop | points and thresholds | the Module 6 recall/precision |

The quality check on the package comes from the DoD in the course overview: a colleague (or you, a month from now) reads it with no spoken commentary.

## 8.5 The final run

1. **The full Module 6 red-team** against the assembled system (not the components)—the attacks from §6.4 plus one new one, invented for your own build (the composition "MCP tool + gate + retrieval").
2. **The eval gate** green on every set (the Module 3 questions, the Module 4 tools).
3. **Module 4 chaos** on the assembled saga—both scenarios.
4. A day of "operations": 30–50 varied requests, and in the evening a walk through the dashboards (cost per user, route shares, gate metrics) as a production review.

## 8.6 The DoD checklist

- [ ] The Chapter 26 scenario is assembled; every module's smoke tests are green on the assembled system.
- [ ] Appendix D: 27 items—an artifact or a written risk for each, the table in the README.
- [ ] Your own "Appendix C": sequence + span tree + cost table, with the divergences from the reference explained.
- [ ] An ADR package of 8–12 decisions, each with numbers from the modules.
- [ ] The final run: red-team, eval gate, chaos—green; the day of operations reviewed.

That is the graduation: a system you can *defend*—with numbers, traces, and decisions—not merely show.
