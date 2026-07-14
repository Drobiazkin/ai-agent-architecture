<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Module 4 — Agents and Orchestration: In Depth

*A companion to "Module 4" in the course overview (README.md). Language: Java, no agent frameworks—the whole point of this module is to build the agent harness (§10.2 of the book) yourself, so that you can later recognize it inside any framework.*

## 4.1 Your own harness: the ReAct loop

The tool contract and the core of the loop (~150 lines including parsing; skeleton):

```java
public interface Tool {
    String name();
    String description();               // the MODEL reads this—the ACI contract, §12.3 of the book
    String execute(Map<String, String> args);
}

public final class AgentHarness {
    private final ChatClient chat;
    private final Map<String, Tool> tools;
    private final int maxSteps;         // iteration budget—§10.5; without it the loop never terminates

    public String run(String task) {
        var transcript = new StringBuilder(task);
        for (int step = 0; step < maxSteps; step++) {
            String out = chat.prompt().system(REACT_SYSTEM)     // format: Thought / Action / Final
                             .user(transcript.toString()).call().content();
            var action = parseAction(out);                       // Action: tool_name({"k":"v"})
            if (action.isEmpty()) return parseFinal(out);        // the model produced its final answer
            Tool tool = tools.get(action.get().name());
            String observation = (tool == null)
                ? "ERROR: no such tool " + action.get().name()   // the error goes INTO THE CONTEXT (§12.4)
                : safeExecute(tool, action.get().args());        // try/catch + timeout inside
            transcript.append("\n").append(out)
                      .append("\nObservation: ").append(observation);
        }
        throw new BudgetExceededException("steps > " + maxSteps); // escalate, don't fail silently
    }
}
```

Write REACT_SYSTEM yourself, following §13.3 of the book (the Thought→Action→Observation format, the tool list with descriptions, and the "one action per turn" requirement). Starter tools: `search_kb` (a wrapper around your Module 3 retrieval) and `get_order_status` (a stub with fixed data).

Notice, while you're writing it: *all* of the determinism is yours (parsing, dispatch, budgets, timeouts)—the model only proposes the next step. That's exactly what "agent = LLM core + harness" means.

## 4.2 Limits and progress detection (§10.5)

A step signature is the tool plus a hash of the normalized arguments; a repeat means no progress:

```java
record StepSignature(String tool, String argsHash) {}

private final Deque<StepSignature> recent = new ArrayDeque<>(3);

boolean isStuck(StepSignature s) {
    boolean repeat = recent.contains(s);
    if (recent.size() == 3) recent.removeFirst();
    recent.addLast(s);
    return repeat;
}
```

Hash the arguments with keys sorted and strings trimmed (otherwise `{"id":"123 "}` and `{"id":"123"}` count as "different" steps). The nontermination test: a stub tool that always returns "no data, try again"—the agent must stop and escalate within ≤ maxSteps, and the fact that it stopped on progress detection (not on budget) must be reported as a separate field of the result.

## 4.3 Orchestrator-Workers with saga discipline (§11.5)

Your own saga table (simpler and more transparent than eventuate-tram for teaching purposes; it remains an option):

```sql
CREATE TABLE saga_steps (
    saga_id     uuid    NOT NULL,
    step_no     int     NOT NULL,
    step_key    text    NOT NULL,      -- the step key: saga_id + the step's semantics; the same key travels on to the side effect
    status      text    NOT NULL CHECK (status IN ('STARTED','DONE','COMPENSATED')),
    payload     jsonb,
    updated_at  timestamptz DEFAULT now(),
    PRIMARY KEY (saga_id, step_no),
    UNIQUE (step_key)                  -- the log doesn't double up: one log row per step
);

-- The owner (assistant) creates the table, but the application walks it—and since §3.3 of Module 3
-- the application connects only as app_user. The grant sits next to the DDL, per the rule in §3.2 of
-- Module 3: a table without a grant does not exist for the application. The worker both writes the
-- log and re-reads it on restart—hence three privileges:
GRANT SELECT, INSERT, UPDATE ON saga_steps TO app_user;
```

The step key is carried by **the action itself**, not by the log. That is exactly where the book puts it: §10.4—"a step repeats, the side effect must not be duplicated → idempotent operations under a key"; §11.5—"idempotency of the worker step keyed by task"; Appendix D—"the agent's actions are idempotent on an operation key." `UNIQUE` on `saga_steps` forbids a duplicate *log row*—it will not save you from a second ticket. So the same `step_key` travels into the tickets table (the table itself is created by the DDL below; the rows in it are created by the saga, and it is the same table Module 5 draws tickets from for code mode):

```sql
CREATE TABLE tickets (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    step_key    text    NOT NULL UNIQUE,   -- THE SAME step key: a duplicate ticket is cut off HERE, not in the log
    category    text    NOT NULL,
    summary     text    NOT NULL,
    status      text    NOT NULL DEFAULT 'OPEN',
    created_at  timestamptz DEFAULT now()
);

-- The same rule (§3.2 of Module 3): the grant sits next to the DDL. A separate grant on the identity
-- column's sequence is not needed—it is served by the INSERT privilege on the table itself.
-- Verified on the rig.
GRANT SELECT, INSERT, UPDATE ON tickets TO app_user;
```

The key has to reach the effect through **the tool's signature**, or the link breaks silently. The ticket is created by `createTicket`, and on the Module 8 assembly (§8.1, step 2) that call goes *only* through the MCP client to the Module 5 server—there is nothing on the server side to derive the key from, since it knows nothing about the saga step. So the contract is `createTicket(category, summary, stepKey)` (Module 5 §5.1 holds the same triple). The name is spelled differently on the two sides, and that is not a discrepancy but two different conventions: `stepKey` is a Java method parameter, and the same name travels into the tool schema and onto the MCP wire; `step_key` is a column in SQL. Idempotency lives **inside** the tool:

```sql
INSERT INTO tickets (step_key, category, summary) VALUES (?, ?, ?)
ON CONFLICT (step_key) DO NOTHING RETURNING id;  -- nothing came back → the ticket already exists:
SELECT id FROM tickets WHERE step_key = ?;       --   return its id, don't create a second one
```

`step_key` is set by **the worker**, not by the model: it is deterministic (`saga_id` + the step's semantics), and the harness substitutes it before the call, overwriting whatever the model wrote in that field. The model does not invent idempotency keys—on a repeat of the step it will invent a new one, and the second ticket will go through just like the first.

The orchestrator (an LLM) produces the plan; every worker step executes by the protocol: `INSERT ... STARTED ON CONFLICT (step_key) DO NOTHING` into the log → `createTicket` with the same `step_key` **in its own transaction** → `UPDATE ... DONE` with the result in `payload`. Resolution on restart goes by the log: `DONE` → the step finished, the result is in `payload`; no row → the step never started; `STARTED` → **unknown** (the effect may or may not have landed), and the worker simply repeats the step—the unknown is resolved by the key on the action, not by the log. Compensation walks the DONE steps in reverse order, calling their compensating operations.

**A chaos experiment (chaos engineering / fault injection):** the kill point is *after* the side effect and *before* `DONE`:

```java
// fireOnce = AtomicBoolean.compareAndSet(true, false): armed by the test, fires ONCE
if (chaos.fireOnce("worker-after-effect")) throw new SimulatedCrashException();
```

**The injection firing once is what makes test (1) satisfiable at all, not an implementation detail.** The first run dies after the effect; the second passes straight through the point and drives the saga to `DONE`. Leave the flag permanently armed and the second run dies in the same place: `UPDATE ... DONE` never executes, `payload` stays `NULL`, and the second half of test (1) ("the saga reaches the end") is unreachable under any correct implementation of the protocol.

**Transaction boundaries are a precondition of the experiment, not a detail.** The ticket must commit **separately** from `UPDATE ... DONE`. Put the effect and the log in one transaction and `SimulatedCrashException` rolls back both: the restart sees clean state, `UNIQUE` never fires at all, and test (1) goes green having checked nothing. The window between the commit of the effect and the commit of `DONE` is exactly what the chaos test has to reproduce; you cannot close it with a transaction (the ticket lives in the DB, and in the general case—across a network), so you close it with the key.

Two automated tests: (1) roll forward—after two runs (the first killed at the injection point, the second passing straight through it) `SELECT count(*) FROM tickets WHERE step_key = ?` returns 1 (the duplicate is cut off by `UNIQUE` in `tickets`, not in the log), and the saga reaches the end with a non-empty `payload`; (2) rollback—the compensations ran for every DONE step and the domain state came back. Both green = a DoD item.

## 4.4 Human-in-the-Loop Gate (§10.6)

Implement it from the book's card: a `pending_actions` table (what / why / preview / deadline), a review-queue endpoint, the operator's decision, and a **safe timeout** (no decision by the deadline → reject, don't execute). You write the DDL yourself, but its grant follows the same rule from §3.2 of Module 3, right away and right there: `GRANT SELECT, INSERT, UPDATE ON pending_actions TO app_user;`—the queue is read and written by the application, and the application connects only under that role. The gate's metrics go into the same Langfuse spans: the approval rate and the median time to decide.

**The automation-complacency experiment** (Parasuraman & Riley, 1997; colloquially, rubber-stamping): approve 30–50 actions in a row without looking, with random pauses of 1–3 s. The alert has to fire on the pair of signals "approval rate → 100% while time to decide → seconds." If it didn't fire—now you know why (thresholds? the aggregation window?); fix it and repeat: this is an exercise on the *metric*, not on the operator's discipline.

## 4.5 Workflow vs agent (§10.3, §11.8)

One task ("a refund request: check the order → check the policy → create the ticket") in two implementations: a fixed chain of three calls, and your agent from §4.1 with the same tools. 20 runs each: cost, latency, success rate, the variance in the number of steps. The table plus the conclusion for production go into a mini-ADR (the book's hint: most "agents" in production are workflows with one or two points of autonomy).

## 4.6 Failure analysis with MAST (§14.4)

Pull three failed trajectories out of Langfuse (after §4.2 and §4.3 you have them) and classify them by the MAST taxonomy: the stage (specification / misalignment between agents / verification), the specific category, and what would have caught it earlier—the specification, the gate, or an eval. Half a page per trajectory; this is the groundwork for the post-mortem culture in Module 6.

## 4.7 DoD checklist

- [ ] The harness: ReAct over 2–3 tools, tool errors are returned into the context, budgets work.
- [ ] The nontermination test: stopping on progress detection (not only on budget)—green.
- [ ] The saga: both chaos tests (roll forward is idempotent—held by `UNIQUE (step_key)` on the tickets table, not on the log; rollback compensates) green in CI. The effect commits in a transaction separate from `DONE`—otherwise the test is green for the wrong reason.
- [ ] The gate: the queue, the timeout that turns into a rejection, the complacency alert fires on the simulation.
- [ ] The workflow vs agent table (20+20 runs) + a mini-ADR.
- [ ] 3 MAST analyses; 10–20 labeled "request → expected tool" pairs filed in `golden/tools.csv`—they go into the Module 6 eval gate.
