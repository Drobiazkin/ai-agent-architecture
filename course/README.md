<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Practicum: AI Agents by Hand
## A Companion Course to *The Architecture of AI Agents and LLM Systems*

**Aleksandr Drobiazkin**

*This edition: July 2026. Check the tool versions (Spring AI 1.x, LangChain4j 1.x, vLLM, RAGAS) against the current releases before you start a module—the APIs of young frameworks change between minor versions.*

> The book gives you the theory and the decisions; the practicum gives you muscle memory. There is **no** retelling of the theory here—every module opens with a pointer to "what to read in the book," and from there on it is hands only: code, measurements, artifacts. If the wording of an exercise is unclear, that is a signal to go back to the chapter it names, not to hunt for the explanation here.

> The audience is the book's: a senior/principal with distributed systems behind them (JVM, k8s, Kafka, Postgres, Keycloak), moving into AI engineering. Java is the primary language of the product modules; Python gets picked up from zero wherever the industrial stack does not live without it (the substrate, evals, fine-tuning).

**A note on tools.** This course was written in Russian and translated into English by its author. Software assisted: an assistant (Claude, Anthropic) reviewed drafts, flagged errors and inconsistencies, and proposed alternative wordings. Every claim, every decision, and every sentence as published was chosen, written or rewritten, and verified by the author, who takes responsibility for all of it. The model is a tool, not a party: it holds no authorship and no rights, and Anthropic is not affiliated with this course and has not reviewed it. The full statement is in the NOTICE file at https://github.com/Drobiazkin/ai-agent-architecture.

---

## How to pair this with the book

**The recommended mode is parallel, in steps of "a part of the book → a module of practice."** Not "after the book," and not "chapter → exercise":

- **Why not after the book.** 26 chapters of theory with no practice—by the capstone half of Part I will have evaporated. Alternating theory and practice (interleaving) sets each rung of the ladder while it is still fresh; the practice of Module 3 is the best way to *really* read Chapter 9.
- **Why not chapter by chapter.** Meaningful artifacts (a RAG pipeline, a saga agent) do not assemble out of a single chapter; chop the practice into 26 pieces and you get a tutorial instead of engineering.
- **The rhythm of a module:** read a part of the book (1–2 weeks in the background) → do the module (the bulk of the time) → close the Definition of Done → a short retro memo: what of the theory *did not work* in your hands, what surprised you. Where your experience diverges from the book is the most valuable thing the practicum gives you.

If you have already read the book cover to cover, the course works that way too: ignore the "Read" column—the pointers in the exercises will take you back to the right sections precisely where you need them.

| Module | The practice topic | Read in the book | Time (at ~15 h/week) |
|---|---|---|---|
| 0 | The rig | The preface | one evening |
| 1 | The substrate by hand (Python/PyTorch from scratch) | Part I (Chapters 1–2) + Appendix A | 3 weeks |
| 2 | The interface: a contract with the model | Part II (Chapters 3–5) | 1.5 weeks |
| 3 | RAG on your own stack | Part III (Chapters 6–9) | 3 weeks |
| 4 | Agents and orchestration | Part IV (Chapters 10–14) | 3–4 weeks |
| 5 | MCP and the JVM frameworks | Part V (Chapters 15–16) | 2 weeks |
| 6 | Production: evals, observability, security, cost | Part VI (Chapters 17–20) | 3 weeks |
| 7 | Models of your own: QLoRA and vLLM | Part VII (Chapters 21–23) | 3–4 weeks |
| 8 | The capstone | Part VIII + Appendices C, D | 3–4 weeks |

~5.5–6 months in total. The order matters more than the dates; the book's running principle—"do not climb the ladder before the simple thing has provably hit its limit"—applies to working through the course too.

**The rules of the course.**
1. **Every module ends in an artifact** (a repository, a measurement, a memo)—not "read it and understood it."
2. **Measure everything.** A claim without a number is an opinion; opinions are not handed in here.
3. **Keep a decision journal**—a mini-ADR at every fork (the format is §26.3 of the book). By the capstone this will be a habit rather than an exercise.
4. **One and the same end-to-end domain** across every module—an internal support assistant (as in Chapter 26): a knowledge base of policies, orders, tickets. Every module grows the same project instead of building a toy from scratch.
5. **Spend little.** Local models through Ollama are free; keep the hosted API within ~$30–60 for the whole course (the limits are the first thing you set up in Module 0); run the LLM judge and the RAGAS passes on a cheap tier of models; the GPU is rented by the hour in Module 7 only (~$10–25).
6. **The canonical term comes before the analogy.** An analogy is scaffolding: it helps you get in, and it comes down once the building stands. In ADRs, retro memos, and code use the canonical names (ReAct, Orchestrator-Workers, chaos engineering, automation complacency, RRF)—they are what the literature is searchable by and what your colleagues understand; conversational labels do not travel into artifacts. Where the course offers an analogy, the canonical name is given first.

**The modules in depth.** This file is the navigator: goals, exercises, DoD. The step-by-step commands, docker-compose, code skeletons, and configs live in the `course/` directory: one file per module (`module-0.md` … `module-8.md`) plus `python-primer.md` (the language through a contrast with Java; the modules' Python snippets carry syntax walkthroughs that link back to it). The code in the in-depth files is skeleton code: check the dependency versions and signatures against the releases (see the edition stamp above), and what proves it works is your own rig, not the text of the course.

---

## Module 0 — The Rig (One Evening)

**The goal:** install everything people trip over later, now. **In depth:** `course/module-0.md`—a ready docker-compose, the commands, project skeletons.

1. **The Java stack:** JDK 21, Spring Boot 3.x + Spring AI (BOM), LangChain4j—two empty skeleton projects that compile.
2. **The Python stack:** `uv` (an environment/package manager—venv and pip in one), Python 3.12, `uv add torch jupyter pytest`. The language itself comes from the primer `course/python-primer.md` ("Python for the Java Developer," through a contrast with Java, 2 evenings on the plan in §14 of the primer); from there on it works as a reference: the modules' Python snippets carry "Syntax walkthrough" blocks that link back to its sections.
3. **Models:** Ollama + two local models (a small ~1–4B and a medium ~8B, qwen3/llama for example), and a key for one hosted provider **with a spending limit set**.
4. **Data:** Postgres 16 + pgvector (docker-compose), Keycloak (you already have it), a corpus for the end-to-end domain—30–50 real policy documents (or synthesize them with an LLM and proofread). Here too: **two DB roles**—`assistant` (the schema owner; the Postgres image makes it a superuser) and `app_user`, the one the application reads data under. The split is set up now and pays off in M3: a superuser bypasses RLS silently, and without the second role the whole M3 policy is decoration.
5. **Observability:** Langfuse self-hosted—needed from Module 2 on; it goes up as a **separate** compose from their repository (it does not get pasted into the rig's `docker-compose.yml`: it drags in its own ClickHouse/Redis/MinIO), ~2–3 GB on top of the rig.

**DoD:** both skeletons answer "hello" through Ollama and through the hosted API; the `app_user` role exists and is NOT a superuser (`rolsuper = f`); `pytest` is green on the Python project's smoke test (an empty run does not count: 0 collected tests give exit code 5, not 0); the spending limit is set.

---

## Module 1 — The Substrate by Hand (Python/PyTorch from Scratch)

**Read:** Chapters 1–2, Appendix A. **The goal:** stop seeing magic in the model; and, along the way, working PyTorch. **In depth:** `course/module-1.md`.

1. **The tensor vocabulary of Appendix A—in a notebook.** Run every operation of §A.3 of the book by hand: shape/broadcast, matmul, batched matmul, `einsum("bhqd,bhkd->bhqk", Q, K)` on random tensors—check the dimensions against the trace in §1.4 of the book. That is what "PyTorch from scratch" means here: a vocabulary of nine operations.
2. **A token calculator** (Java or Python): over your own corpus—the distribution of tokens per document, the cost of indexing/queries at 2–3 price tiers. Russian against English: measure fertility (§1.2 of the book) on your own texts.
3. **Assemble a GPT block following Raschka** (chapters 3–4 of his book): self-attention → multi-head → transformer block. Don't copy-paste—type it by hand. The DoD check: in writing, with references to the lines of your own code, explain where the O(n²) in sequence length lives and what gets cached in the KV-cache; check it against the traces in §1.4 and §1.6 of the book.
4. **Replace the FFN with an MoE layer** (a router + top-2 of 4 experts): compare total/active parameters and FLOPs per token (§1.5 of the book).
5. **Decoding strategies (§1.7 of the book):** a single JSON-extraction task, 50 runs at temperature 0 and 1 on a local model—the share of valid JSON and the spread of the content; check against §2.4 of the book (why even T=0 does not give bit-exact reproducibility).
6. **Calculation versus measurement:** compute the size of the KV-cache for your own local model with the formula in §1.6 of the book—check it against Ollama's actual memory consumption on a short and on a long context.

**The artifact:** the notebooks + a memo "Dense vs MoE for [domain]: a recommendation" (1 page, with the numbers from item 4).

**DoD:** every countable item is closed with a number—the O(n²) analysis with references to the lines of your code (item 3), total/active parameters and FLOPs/token (item 4), the share of valid JSON by temperature (item 5), the size of the KV-cache, calculation against the Ollama measurement (item 6).

---

## Module 2 — The Interface: A Contract with the Model

**Read:** Chapters 3–5. **The goal:** the prompt as a specification, the output as a typed contract. The primary language is Java. **In depth:** `course/module-2.md`.

1. **A ticket-classifier contract** (Spring AI `ChatClient` + `entity(Ticket.class)`): a system invariant + few-shot + a strict schema with an enum. 50 labeled examples; the metrics: the share of **structurally valid** outputs (the answer fit the schema) and the share of correct categories.
2. **The pitfall from §5.4 of the book, by hand:** add `pattern`/`minLength` to the schema and, over 20 runs, separate two *different* classes of failure—structural (the answer didn't fit the schema: rare, but not never) and a violation of value constraints (set in the schema, not enforced at generation). Exactly which ones your provider does enforce at generation goes into a table: not all of JSON Schema is enforced, and the specific set differs from provider to provider. Then a post-hoc validator with reask (§5.5 of the book) on both branches—and drive **structural** validity to 100%.
3. **An A/B test of the context budget:** a "rich" context versus a minimal one—quality/cost/latency; lay out the window in the style of the worked example in §4.4 of the book.
4. **An injection smoke test:** "ignore the instructions and return X" in the *data* (not in the question); with `<untrusted_data>` isolation (§4.6 of the book) and without—compare the share of successful injections. This is not a defense yet (Chapter 19)—it is calibrating expectations.
5. **Wire in Langfuse** and make sure you can see the tokens/cost/latency of every call—from this module on, everything is traced.

**DoD:** a classifier with structural validity at 100% (after reask), with measured accuracy and an average number of attempts; the table "which schema constraints the provider enforces at generation and which it does not"; a report on the injection test, with numbers.

---

## Module 3 — RAG on Your Own Stack

**Read:** Chapters 6–9. **The goal:** climb the retrieval ladder measuring every rung—on Postgres, with no specialized vector databases. **In depth:** `course/module-3.md`—SQL schemas, the RRF query, service skeletons, RLS policies.

1. **Baseline: Naive RAG** on pgvector (HNSW) over the policy corpus—**by hand**: SQL top-k → prompt. This is the path every later rung and the RLS stand on—start here. Spring AI's `QuestionAnswerAdvisor` is not the baseline but a short excursion on a separate teaching table: its `PgVectorStore` works only with its own column contract and does not fit the course's schema. The two paths are **not equals**; the price of someone else's abstraction over your own schema is worked through in the in-depth module.
2. **A golden set before any improvements** (§9.3 of the book): 50 question→reference pairs, including 5–7 "questions with no answer in the corpus." Measure the baseline: retrieval hit rate (your own script: the share of questions where the needed chunk landed in the top-k) and the generative faithfulness / answer relevancy from RAGAS (this is Python: a small eval script, your second pass at the language).
3. **The hybrid rung:** tsvector/BM25 + RRF fusion (in SQL or in code)—measured against the baseline (§7.3 of the book).
4. **The rerank rung:** a cross-encoder over the top-50. Two paths to choose from: (a) a Python microservice, FastAPI + bge-reranker (which also gives you the first Python service in your rig's production), (b) a hosted rerank API. Measure it (§7.4 of the book).
5. **RBAC at retrieval** (§8.7 of the book): the clearance sits on the **document** (access is decided by the document and reaches the chunk through a join) + **Row-Level Security** in Postgres, with the roles taken from the Keycloak token. The application connects as `app_user` from M0—under a superuser the policy filters nothing, and silently. The tests: the fuse "we are NOT connected as a superuser" (without it the rest go green for the wrong reason); a low-privilege user gets no protected chunk under any query; recall with the filter on has not dropped (§8.6 of the book).
6. **Deletion and tombstones (§8.3 of the book):** delete a document "at the subject's request"—confirm it is gone from the results, and look at what physically remains in the index.

**DoD:** a table of metrics by rung of the ladder (naive → hybrid → +rerank) on the golden set; all three RLS tests in CI (the fuse included); the pipeline assembled into `RetrievalService`—M4 and M5 reuse it; a memo "which rung I stopped at and why" (a mini-ADR, with the alternatives rejected).

---

## Module 4 — Agents and Orchestration

**Read:** Chapters 10–14. **The goal:** the agent as a distributed system—that is your head start; make it explicit. **In depth:** `course/module-4.md`.

1. **Your own harness: the ReAct loop by hand** (plain Java, no framework, ~150 lines): Thought → Action → Observation over 2–3 tools (KB search from M3, order status—a stub). What you are writing is the **harness** (§10.2 of the book)—the deterministic half of the agent: assembling the context, parsing the calls, executing them, the state, the budgets. Get a feel for it before a framework hides it from you; agent = LLM core + this code of yours.
2. **Limits and progress detection** (§10.5 of the book): an iteration/token budget + a repeated signature (tool + a hash of the arguments) → abort with escalation. The test: a tool that returns a useless answer—the agent stops instead of spinning.
3. **Orchestrator-Workers (§11.5 of the book), with reliability coming from saga discipline.** The canonical pattern is Orchestrator-Workers (Anthropic); Richardson's saga here is the implementation discipline for its mechanics (a step log, step idempotency by key, timeouts, compensations)—with two differences the book names outright: the coordinator is nondeterministic and the plan is dynamic. Implement it on your own saga table (more transparent for teaching purposes; eventuate-tram remains an option). Then a **chaos experiment** (chaos engineering—the canonical name in reliability engineering, Netflix, principlesofchaos.org; fault injection—the general technique; the book covers the mechanics of partial failures in §10.4–10.6 without introducing the name): kill a worker after its side effect but before the saga completes—rolling forward is idempotent (no second ticket appeared), rolling back compensates what was done; both scenarios as automated tests.
4. **A Human-in-the-Loop Gate per the pattern card in §10.6 of the book:** a review queue, a decision card (what/why/a preview), a safe timeout, a journal, metrics (the approval share, the time to decide). Then simulate **automation complacency**—the canonical name for the degradation of human oversight (Parasuraman & Riley, 1997; colloquially, rubber-stamping): approve everything without looking, 30–50 actions—the gate's metric must detect it (the share → 100%, the time to decide → seconds).
5. **Workflow versus agent** on one task (§10.3, §11.8 of the book): the same task as a fixed chain and as an autonomous loop—cost/latency/predictability, and the conclusion for production.
6. **Failure analysis with MAST** (§14.4 of the book): take 3 failed trajectories from your own logs and classify them against the taxonomy.

**DoD:** an Orchestrator-Workers agent with a green chaos test (chaos engineering); a gate with a working automation-complacency metric; a comparison table of workflow/agent; 3 failure analyses with MAST; 10–20 labeled tasks "request → expected tool"—they go into the M6 eval gate (the "correct tool" check is §17.5 of the book; the eval gate itself, §17.8 of the book).

---

## Module 5 — MCP and the JVM Frameworks

**Read:** Chapters 15–16. **The goal:** integration as a standard, and both styles of the JVM stack by hand. **In depth:** `course/module-5.md`.

1. **An MCP server on Spring AI** (server-side tools via `@McpTool`—the Spring AI 1.1+ branch; on 1.0 GA it is `@Tool` + `MethodToolCallbackProvider`, check against the BOM version from M0): `search_kb`, `get_order_status`, `create_ticket`—wrappers over M3/M4. On ticket creation the third parameter is not optional: `createTicket(category, summary, stepKey)`—the saga's step key (item 3 of M4) reaches the effect only through the tool's signature, and the harness substitutes it before the call, overwriting whatever the model wrote. Connect it to any MCP host (Claude Desktop/CLI) and watch "someone else's" model call your tools—there the model invents the key and there is no deduplication: that is the price of the demo.
2. **Your own MCP client** (`spring-ai-starter-mcp-client`)—the module's second half, not an optional extra: move the M4 harness onto tools **only** through it, removing the direct service calls. Someone else's host is a black box: tool approval, `tools/list`, and the loading of procedures live inside it and cannot be touched by hand. With your own client your harness becomes a full-fledged host (the roles are laid out in §15.2 of the book), and hanging off that link are the pinning (item 6), the skill measurement (item 7), and the M8 assembly.
3. **OAuth on MCP** through Keycloak (§15.7 of the book): the server as an OAuth Resource Server; the test—a call with no token or with the wrong scope is rejected. Then the agent-identity step (§15.7 of the book, Deep Dive): instead of passing the user's token straight through—**token exchange** (RFC 8693; in Keycloak it is enabled on the client) with the scope narrowed; in the Langfuse spans, both subjects: who initiated (the user) and what executed (the agent as an NHI). Your Keycloak expertise meets a new perimeter.
4. **The same assistant on LangChain4j AiServices** (an interface + `@Tool` + `@MemoryId`): compare it against Spring AI's Advisors style—§16.3 of the book by hand; a two-page memo "what composes where."
5. **Blocking the event loop under load** (§16.5 of the book): call the model in a blocking way inside a WebFlux handler under load (wrk/gatling)—watch it degrade; move it onto boundedElastic/virtual threads—compare p99.
6. **A rug pull by hand** (§15.7 of the book; the canonical MCP-security term for swapping a tool's definition after it has been approved): in this threat model the attacker is the **server**, so you play the server when you swap the definition, and you put the countermeasure on the opposite side. Change the description of an approved tool—record that the host did not notice; bolt on pinning of the approved descriptions by hash **in your own MCP client** (item 2). The measure itself comes from §15.7 of the book ("Pin approved tool descriptions by hash"); it does not name the side—the course derives that from §15.2 of the book and Appendix D: the trust boundary is the host, the server is potentially untrusted.
7. **Skills and code execution (§12.6 of the book).** (a) Package the procedure "how to escalate a ticket" as a **skill**: a directory with a `SKILL.md` (the name + description in the header, the instructions in the body, the letter template as a separate file). Implement the three-stage loading **in your own M4 harness**: a skill is host mechanics, not MCP-server mechanics—it cannot be wired in through a server, and in someone else's host you cannot touch it. Measure progressive disclosure through your own harness's Langfuse, three numbers: the procedure baked into the system prompt; the skill wired in but the question is not about escalation; the question is about escalation. The same directory in Claude Desktop is an optional "have a look with your own eyes": no numbers come off it—your Langfuse does not see into someone else's host. (b) **Code mode**: the task "close every ticket older than 30 days with a notification"—first as a tool-calling loop (N turns), then as a single generated script over file wrappers around the same tools; compare tokens, turns, and latency. The sanitary rule: generated code executes only in a container with no route out (§19.6 of the book)—"no network out" ≠ "no network at all."

**DoD:** a secured OAuth MCP server with token exchange that an external host connects to; the M4 harness goes for its tools only through its own MCP client, with no direct service calls left (the M8 assembly link); a memo comparing the two frameworks; a p99 chart before/after moving the blocking call off; the rug pull reproduced and caught by hash pinning in your own client (a green test); the measurement "skill versus a baked-in prompt" (three numbers) and "code mode versus the loop," with numbers.

---

## Module 6 — Production: Evals, Observability, Security, Cost

**Read:** Chapters 17–20 (+ the Deep Dive on the classifier in §2.2 and the PII containment loop, §25.4). **The goal:** turn the rig into a system you can trust. **In depth:** `course/module-6.md`.

1. **The eval gate in CI** (§17.8 of the book): the golden set from M3 + deterministic checks (schema validity, the correct tool) + an LLM judge with a rubric; miss the threshold and the build goes red. The tool is DeepEval (Python) or promptfoo (Node/TS, YAML config).
2. **Judge biases by hand** (§17.4 of the book): 20 pairs of answers, each in both orders—measure your judge's position bias; compute the judge's kappa against your own labels (§9.4 of the book). An uncalibrated judge means the numbers cannot be trusted.
3. **Sample size** (§17.7 of the book): use the formula to work out how many examples it takes to distinguish 90% from 85%—compare that with your own set and write down honestly that your 50 catch only crude regressions.
4. **A red team against the checklist in §19.7 of the book:** an indirect injection through a document in the RAG corpus (an exfiltration instruction inside a policy), the composition "a read + an outbound call" (§12.5 of the book, the lethal trifecta), an attempt to get around RBAC through the prompt. Every attack becomes a test, every breach becomes a fix (isolation, a taint rule, a gate).
5. **Traces and cost:** check the agent's span tree in Langfuse against Appendix C; attribute cost by feature/user (§18.5 of the book); the cache experiment—move the system prompt into a cacheable prefix and confirm the economics of §20.2 of the book with a measurement.
6. **A thin LLM gateway (§20.6 of the book):** route every model call through a single egress point—routing, a quota that degrades instead of returning a 500, token accounting per caller. Not a full governance layer (§25.3 of the book), but the minimum control point that the capstone (M8) reuses as a ready-made gateway.
7. **The routing classifier with a measured failure (§2.2 of the book, Deep Dive):** routing in the gateway—"simple → local/cheap, hard → strong" (the classifier: start with a heuristic, then a cheap LLM call with structured output). Calibrate the threshold against the matrix of error costs, not against accuracy. The main experiment is the **silent failure**: slip in a category of requests that wasn't in your labeling and show—with a number by route in Langfuse—that without an offline eval you did not notice the drift; then set up an alert on the distribution of routes.
8. **The PII containment loop (§25.4 of the book):** detection on the way into the index and on the way out of the gateway—Presidio (or your own cascade of regex + NER; for Russian, take a Russian-language NER model). 30 labeled fragments with Russian entities (names, phone numbers, INN): measure recall and precision; record separately that the English-language default silently lets Cyrillic names through. Shift the threshold toward recall on the outbound direction—and look with your own eyes at what the answers turn into when you over-insure (the price of a false positive).

**DoD:** CI fails on a slipped-in prompt regression; a red-team report (attacks → breaches → fixes → a green re-run); a cost-per-user dashboard; every model call goes through the thin gateway; the router with an alert on drift, and the PII containment loop with measured recall and precision (by entity instances, not by types).

---

## Module 7 — Models of Your Own: QLoRA and vLLM

**Read:** Chapters 21–23. **The goal:** take "your own model" from the decision through to serving. This is a Python module (the HF stack) + your own infrastructure. **In depth:** `course/module-7.md`.

1. **The decision frame, honestly** (§21.1 of the book): walk Prompt → RAG → Fine-tune through your own domain in writing; if the conclusion is "no fine-tuning needed," that is the right conclusion—carry on fine-tuning the training task deliberately, as an exercise.
2. **QLoRA on 7–8B** (Unsloth or PEFT/TRL, a rented GPU or Colab): the task is extracting ticket fields into strict JSON; 500–1000 examples (synthesis + proofreading). The starting hyperparameters are in §21.8 of the book.
3. **Forgetting—measure it:** before/after on your own task AND on a general benchmark (a subset of MMLU through lm-evaluation-harness)—see the trade-off (§21.8 of the book); add a replay share of general data and repeat.
4. **vLLM (k8s, or docker/k3s on the rented GPU host):** deploy the base model + your own LoRA adapter (multi-LoRA, §21.3 of the book); take throughput/latency at concurrency 1/8/32—learn the trade-off of §22.8 of the book on your own hardware; compute $/1M tokens of your own serving against hosted (§2.6 of the book, break-even by hand).
5. **(Opt.) Pre-training in miniature:** nanoGPT on a tiny corpus—purely to get a feel for the price of C≈6ND (§23.4 of the book) at toy scale.

**DoD:** an adapter that beats the base model on the target task, with the forgetting documented; a vLLM deployment with measurements; the memo "when my self-host pays for itself," with numbers.

---

## Module 8 — Capstone

**Read:** Chapters 24–26, Appendices C and D. **The goal:** assemble everything into one system and sign it off to yourself against the book's standards. **In depth:** `course/module-8.md`.

Assemble the end-to-end scenario of Chapter 26 on your own rig: the M6 gateway (limits, attribution) → saga orchestration → RAG with RBAC → tools over MCP → a human-gate on writes → evals in CI → traces and cost.

**Acceptance—through three artifacts of the book:**
1. **The preflight checklist (Appendix D)**—work through every item; every item without a check mark is a risk accepted in writing.
2. **The trace of a single request**—capture your own "Appendix C": the sequence flow, the span tree, a table of tokens/cost; compare against the book's reference—what is more expensive/slower in yours, and why.
3. **The ADR package** (8–12 decisions in the format of §26.3 of the book)—your own counterpart to §26.4 of the book: the model, the rung on the RAG ladder, workflow/agent step by step, where the human-gate goes, which OWASP risks are covered by what.

**DoD:** the system survives the M6 red team, checklist D is closed, the ADR package reads for a colleague with no spoken commentary from you.

---

## The Python track (a summary)

Python gets picked up not through a separate course but wherever the industrial stack leaves no alternative:
- **M0**—the environment (uv, pytest, pyproject) + the syntax from the primer `course/python-primer.md` (a Java↔Python contrast, 2 evenings);
- **M1**—PyTorch: the tensor vocabulary of Appendix A, attention/GPT by hand (the core of the track);
- **M3**—eval scripts (RAGAS) and the first microservice (FastAPI + a reranker);
- **M6**—eval tooling in Python (DeepEval; promptfoo is Node/TS, off the Python track);
- **M7**—the HF stack (transformers, PEFT/TRL, datasets)—the densest Python module.

By the end of the course that is a working reading/writing level in the ML ecosystem—the goal "know the common stack" gets closed along the way, without an abstract "Python course."

## How this relates to the earlier roadmap

This practicum replaces roadmap v2: its theoretical half has been absorbed into the book entirely (deeper, and with the facts corrected—the roadmap still carries "~40% of retrieval misses" and "the judge ≈85%": the first one the book did not retract but kept as a floating estimate of 30–40% with an explicit caveat that it traces back to no single primary source (§6.5 of the book), the second was dropped completely), the exercises have been kept and strengthened (DoD, measurements, acceptance against Appendix D), and the mapping "phases → parts of the book" has become explicit. The "new → familiar" analogies are scattered through the book at specific points (for example, the "Analog in distributed systems" column in the failure taxonomy of §14.4 of the book)—they are not duplicated here.
