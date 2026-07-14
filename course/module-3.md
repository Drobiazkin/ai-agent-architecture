<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Module 3 — RAG on Your Own Stack: In Depth

*A companion to the "Module 3" assignment in the course overview (README.md). The order of the sections = the order of the assignment's items. The skeleton rule is the one from module-0.md: verify the versions; what proves it works is the rig.*

The discipline running through the module comes from Chapter 9 of the book: **not one rung of the ladder without a measurement on the golden set**. Hence the structure: schema (§3.1) → ingestion (§3.2) → naive baseline (§3.3) → the golden set and the metrics (§3.4)—and only then the improvements (§3.5–3.6), each against the baseline.

## 3.1 The data schema

```sql
CREATE TABLE documents (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    path       text UNIQUE NOT NULL,
    title      text NOT NULL,
    clearance  int  NOT NULL DEFAULT 0,      -- clearance: 0—everyone, 1—operators, 2—management
    created_at timestamptz DEFAULT now()
);

CREATE TABLE chunks (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id bigint NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    seq         int    NOT NULL,             -- the chunk's position in the document
    content     text   NOT NULL,
    embedding   vector(1024) NOT NULL,       -- 1024 = the dimensionality of bge-m3; switch the embedder and you recreate the column and REINDEX EVERYTHING (§7.6 of the book)
    tsv         tsvector GENERATED ALWAYS AS (to_tsvector('russian', content)) STORED
);

-- the ANN index (§8.3 of the book): m and ef_construction are starting points; you'll tune them deliberately
CREATE INDEX chunks_embedding_hnsw ON chunks
    USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- full-text—for the hybrid rung, §3.5
CREATE INDEX chunks_tsv_gin ON chunks USING gin (tsv);
```

The clearance sits on `documents`, not on `chunks`—the document decides access; in queries it reaches the chunk through a join (and in §3.7 it goes into the RLS policy).

## 3.2 Ingestion

Chunking for policy documents goes by headings, with a size cap. The starting rule comes from §7.6 of the book: meaning boundaries matter more than equal pieces (the same section puts the size at 256–1024 tokens, with 512 and 25% overlap as the point of departure). The course's estimate for Russian-language policies—our numbers, not the book's: 300–500 tokens ≈ 900–1500 characters, which is where the `max_chars=1200` below comes from. Check it on your own corpus with the token calculator from Module 1:

```python
# py/ingest.py—run with: uv add httpx psycopg[binary] && uv run python ingest.py
import glob, re, httpx, psycopg

def chunk(md: str, max_chars: int = 1200) -> list[str]:
    parts = re.split(r"(?=^#{1,3} )", md, flags=re.M)          # split on the headings
    out = []
    for p in parts:
        p = p.strip()
        while len(p) > max_chars:                               # long sections—cut them down further on paragraphs
            cut = p.rfind("\n\n", 0, max_chars)
            cut = cut if cut > 0 else max_chars
            out.append(p[:cut]); p = p[cut:].strip()
        if p: out.append(p)
    return out

def embed(texts: list[str]) -> list[list[float]]:
    r = httpx.post("http://localhost:11434/api/embed",
                   json={"model": "bge-m3", "input": texts}, timeout=120)
    r.raise_for_status()
    return r.json()["embeddings"]

# ingest runs as the schema's OWNER (assistant)—it needs INSERT; production retrieval runs as app_user (§3.7)
with psycopg.connect("postgresql://assistant:dev-only-pass@localhost/assistant") as conn:
    for path in glob.glob("../corpus/*.md"):
        text = open(path).read()
        title = text.splitlines()[0].lstrip("# ")
        doc_id = conn.execute(
            "INSERT INTO documents(path, title) VALUES (%s, %s) RETURNING id",
            (path, title)).fetchone()[0]
        pieces = chunk(text)
        for seq, (c, e) in enumerate(zip(pieces, embed(pieces))):
            conn.execute("INSERT INTO chunks(document_id, seq, content, embedding) VALUES (%s,%s,%s,%s)",
                         (doc_id, seq, c, str(e)))
    conn.commit()
```

**Syntax walkthrough** (the references point at sections of `python-primer.md`):
- `def chunk(md: str, max_chars: int = 1200) -> list[str]:`—type hints and a default parameter (§5 of the primer); you can call it as `chunk(text)` or as `chunk(text, max_chars=800)`.
- `re.split(r"(?=^#{1,3} )", md, flags=re.M)`—the `re` module ≈ Pattern/Matcher in a single call; `r"..."`—a raw string (the one you kept wishing for while escaping `\` in Java regexes); `(?=...)`—a lookahead, which cuts *before* the heading without eating it.
- `p[:cut]` and `p[cut:]`—slices: "up to cut" and "from cut to the end" (§3).
- `if p: out.append(p)`—truthiness: "if the string is not empty" (§2).
- `zip(pieces, embed(pieces))` and `enumerate(...)`—a parallel walk and a walk with an index (§4); `for seq, (c, e) in ...`—tuple unpacking right in the loop header.
- `with psycopg.connect(...) as conn:`—try-with-resources (§8): the connection is guaranteed to close.
- `.fetchone()[0]`—the first column of the first row of the result (≈ `rs.next(); rs.getLong(1)`).

The check: `SELECT count(*) FROM chunks;`—with 30–50 documents, expect on the order of 150–400 chunks. Fewer means the chunks are too coarse; a great deal more means fragmentation (§7.6 of the book—coherence suffers).

**Set the clearances—now, not in §3.7.** The loader above never touches the `clearance` column, so the whole corpus arrives with the default `0` ("visible to everyone"). On a corpus like that the RLS of §3.7 has nothing to filter, and the test "a user with `clearance = 0` does not get a document at clearance 2" checks an empty set and goes green about nothing:

```sql
-- 3–5 documents get a clearance; pick topics where a restriction makes sense (escalation, personal data)
UPDATE documents SET clearance = 2 WHERE path LIKE '%eskalac%' OR path LIKE '%pers-dan%';
SELECT clearance, count(*) FROM documents GROUP BY clearance ORDER BY clearance;  -- you need ≥ 2 levels
```

The clearance gets set here for one more reason: Path B of §3.3 copies only the open part of the corpus into its own table—and "the open part" exists only once the clearances are in place.

**Grant the application role its rights—here, before the first read from code.** Everything above was done by the owner (`assistant`), and from §3.3 on the application connects as `app_user`: the Module 0 rig (§0.2) created the role and gave it nothing but `USAGE ON SCHEMA public`—it has no rights on the tables, because at Module 0 there were no tables yet. Now there are, and they are populated:

```sql
-- The owner (assistant) grants the application role the right to read the corpus. app_user must not write to it:
-- ingest and the migrations run as the owner; production retrieval only reads.
GRANT SELECT ON documents, chunks TO app_user;
```

A rule for the whole course, not just this section: **the owner creates the table—`app_user`'s rights are granted in the same place the table is created.** From §3.3 on, the application connects as nobody else, so a table without a grant does not exist for it. Module 4 (`saga_steps`, `tickets`, `pending_actions`) and Module 5 (the notification log) follow the same rule—the grant sits next to their DDL. Skip it and you get `ERROR: permission denied for table …` in the very first section that reads data from code.

## 3.3 Rung 0: Naive RAG (baseline)

Two paths, but **not equal ones**: the ladder of §3.5–3.6 and the RLS of §3.7 live on Path A, because they stand on the schema of §3.1. Path B is a short excursion to see `QuestionAnswerAdvisor` at work; why it does not fit the course schema—below. Start with Path A.

**Path A—by hand (SQL top-k → prompt).** Retrieval:

```sql
-- $1—the question's vector (from the same bge-m3!); the <=> operator is cosine DISTANCE (smaller = closer)
SET hnsw.ef_search = 40;                       -- candidates during the graph traversal; recall/latency (§8.3 of the book)
SELECT c.id, d.title, c.content, 1 - (c.embedding <=> $1) AS cos_sim
FROM chunks c JOIN documents d ON d.id = c.document_id
ORDER BY c.embedding <=> $1
LIMIT 5;
```

The generation prompt—a minimal, honest template (isolating untrusted content is a habit from Module 2):

```
Answer the user's question ONLY from the policy fragments provided.
If the answer is not in the fragments, say "not found in the policies" and invent nothing.
<fragments>{the top-5 chunks, each with its document title}</fragments>
Question: {question}
```

**Path B—Spring AI, on a table of its own.** `PgVectorStore` (BOM 1.0.0 from Module 0) works only with its own table contract: `(id, content, metadata json, embedding vector(N))`. The column names are **baked into the code**, and no knob exists to rename them—the only configurable things are `schemaName`, `vectorTableName`, `idType`, `distanceType`, `indexType`, `dimensions`. It runs its search as `SELECT *, embedding <=> ? AS distance FROM {table}`, and the row mapper reads a `metadata` column off every row. `chunks` from §3.1 has no `metadata` column at all, which makes `table-name: chunks` a config broken by construction: with `initialize-schema: false` the mismatch does not surface at startup—the query fails the first time the advisor is called. So we stand Path B up on a **separate** table built to its contract:

```sql
-- Path B: a teaching table built to the PgVectorStore contract; check the DDL of your own version against its schema.sql in the jar
CREATE TABLE spring_ai_chunks (
    id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content   text,
    metadata  json,
    embedding vector(1024)                                  -- the same bge-m3
);
CREATE INDEX ON spring_ai_chunks USING hnsw (embedding vector_cosine_ops);

-- Populating it. The embeddings were already computed in §3.2 with the same bge-m3—we copy them over rather than recompute.
-- Only the open part of the corpus (clearance = 0): the RLS of §3.7 does not extend to this table,
-- and restricted material has no business in it. Run by the owner (assistant), like the DDL above.
INSERT INTO spring_ai_chunks (content, metadata, embedding)
SELECT c.content, json_build_object('document_id', c.document_id, 'seq', c.seq), c.embedding
FROM chunks c JOIN documents d ON d.id = c.document_id
WHERE d.clearance = 0;

-- The app_user role was created by the Module 0 rig (§0.2). The advisor only reads—it needs no INSERT.
GRANT SELECT ON spring_ai_chunks TO app_user;
```

```yaml
spring:
  datasource:                           # the application's shared DataSource—for Path A and for Path B alike
    url: jdbc:postgresql://localhost:5432/assistant
    username: app_user                  # NOT assistant: as a superuser, the RLS of §3.7 will filter nothing
    password: ${APP_DB_PASSWORD}        # already in the Module 0 rig's .env (§0.2)
  ai:
    vectorstore:
      pgvector:
        initialize-schema: false        # we keep a schema of our own—the DDL above, as the owner
        table-name: spring_ai_chunks    # SEPARATE from chunks of §3.1: see the paragraph above
        dimensions: 1024
```

`initialize-schema: false` here is not a matter of taste but a consequence of the role: `app_user` has no rights to create tables, and the advisor's attempt to "stand the schema up itself" runs into a refusal. The owner lays down the schema and the data—in the block above.

The advisor on top of `ChatClient`:

```java
ChatClient rag = builder
    .defaultAdvisors(QuestionAnswerAdvisor.builder(vectorStore)
        .searchRequest(SearchRequest.builder().topK(5).build())
        .build())            // the builder's signatures—check against the BOM from Module 0
    .build();
```

The price of honesty: clearances and the RLS of §3.7 do not extend to `spring_ai_chunks`—this is a rig for the advisor, not production retrieval. That is exactly why the copy above takes only `clearance = 0`: a copy of the corpus in a table with no policy is an RLS bypass you built with your own hands. Verified on the rig: without the filter, `app_user` reads through `spring_ai_chunks` the very restricted chunk that the policy withholds from it in `chunks`. That is how a leak gets started in production—not through a hole in the policy but through a second copy of the data sitting next to it. And bear in mind that the copy is a **snapshot**, not a view: raise a document's clearance after it (in §3.7 or later) and the copy stays open. Done looking at the advisor—`DROP TABLE spring_ai_chunks;`; it is a teaching table and has no business outliving the excursion. If you want Spring AI on top of the course schema, you will have to either bring §3.1 to the contract (`metadata json`—the same type as in the DDL above, with `document_id`/`seq`/`clearance` inside it—at which point the policy of §3.7 and the RRF query of §3.5 get rewritten onto `metadata->>'document_id'`), or write a `VectorStore` of your own. Both are outside the module's scope, but take in the fork: this is precisely the price of someone else's abstraction on top of your own schema.

## 3.4 The golden set and measuring the baseline

`py/golden.yaml`—50 pairs, 5–7 of them "with no answer in the corpus" (a check on the honest refusal):

```yaml
- q: "What is the deadline for processing a return of defective goods?"
  expected_chunk_substr: "14 days"        # the anchor for hit rate: a substring of the chunk you need
  answer: "A return is processed within 14 days of the request."
- q: "What is the CEO's phone number?"
  expected_chunk_substr: null              # there is NO answer in the corpus—the reference behavior is a refusal
  answer: "not found in the policies"
```

**Retrieval hit rate** (your own script—a metric of the retrieval rung, before generation):

```python
# py/eval_retrieval.py: for each q—embedding → top-k from the DB → was the substring found
anchored = [g for g in golden if g["expected_chunk_substr"]]   # the "no answer in the corpus" questions are not about retrieval
n = len(anchored)                                              # the denominator is only them, otherwise hit@5 is understated
hits = sum(any(g["expected_chunk_substr"] in c for c in topk(g["q"], k=5))
           for g in anchored)
print(f"hit@5 = {hits}/{n} = {hits/n:.0%}")
```

**Syntax walkthrough:** this is one aggregation in the style of a stream pipeline (§3 of the primer; in Russian this construction often goes by the name «свёртка» in the fold/reduce sense—the word's third meaning from §A.3 of the book, not contraction). From the inside out: `substring in c`—the membership operator; `any(... for c in topk(...))`—"at least one chunk contains the anchor" (≈ `anyMatch`); the outer `sum(... for g in golden if ...)`—counts the true ones across every question with an anchor (`True` is arithmetically equal to 1—which is why sum counts the hits; ≈ `filter(...).count()`); the `if g[...]` at the end—the filter "skip the questions with no answer" (their anchor is `None`, which is falsy). `f"...{hits/n:.0%}"`—an f-string with the format "percent, no decimal places" (§2).

**Generative metrics—RAGAS** (faithfulness, answer relevancy; the judge runs on the cheap tier, course rule #5):

```python
# uv add ragas datasets—the RAGAS API moves, check against your installed version
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
result = evaluate(dataset, metrics=[faithfulness, answer_relevancy])  # dataset: q/answer/contexts
```

Write the baseline numbers into the table of §3.9 **before** any improvements—otherwise there is nothing to compare the improvements against, and the module turns into cargo cult.

## 3.5 Rung 1: Hybrid (BM25-class + RRF)

The full-text branch is already in place (the `tsv` column). The fusion is RRF right in the SQL (the formula and a miniature example—§7.3 of the book):

```sql
WITH vec AS (
    SELECT id, row_number() OVER (ORDER BY embedding <=> $1) AS r
    FROM chunks ORDER BY embedding <=> $1 LIMIT 50
), fts AS (
    SELECT id, row_number() OVER (ORDER BY ts_rank(tsv, q) DESC) AS r
    FROM chunks, websearch_to_tsquery('russian', $2) q
    WHERE tsv @@ q
    ORDER BY ts_rank(tsv, q) DESC LIMIT 50   -- the ORDER BY is needed on the query ITSELF too: without it, LIMIT cuts an arbitrary 50
)
SELECT COALESCE(v.id, f.id) AS id,
       COALESCE(1.0/(60 + v.r), 0) + COALESCE(1.0/(60 + f.r), 0) AS rrf
FROM vec v FULL OUTER JOIN fts f USING (id)
ORDER BY rrf DESC LIMIT 5;
```

Measure with the same script from §3.4. The expectation (not a guarantee): hybrid picks up the questions with exact tokens—directive numbers, SKUs, abbreviations; check it on your own "exact" questions separately.

## 3.6 Rung 2: Reranking

A cross-encoder over the top-50 of the hybrid output. Path (a)—a microservice of your own (the rig's first Python service):

```python
# py/reranker/main.py—uv add fastapi uvicorn sentence-transformers
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import CrossEncoder

app = FastAPI()
model = CrossEncoder("BAAI/bge-reranker-v2-m3")   # multilingual; downloads on first start

class Req(BaseModel):
    query: str
    passages: list[str]
    top_k: int = 5

@app.post("/rerank")
def rerank(r: Req):
    scores = model.predict([(r.query, p) for p in r.passages])
    ranked = sorted(zip(r.passages, scores.tolist()), key=lambda x: -x[1])
    return {"passages": [p for p, _ in ranked[:r.top_k]]}
```

**Syntax walkthrough:** `class Req(BaseModel)`—a pydantic model: DTO and validation at once, like Jackson + Bean Validation in a single class (§13 of the primer)—FastAPI parses the body's JSON into `Req` itself and returns a 422 on a mismatch; `@app.post("/rerank")`—a decorator that registers the handler, reads like `@PostMapping` (§10); `[(r.query, p) for p in r.passages]`—a list comprehension, builds the "question-passage" pairs (§3); `sorted(..., key=lambda x: -x[1])`—a sort descending by the second element of the pair (§5); `ranked[:r.top_k]`—a slice of the first top_k (§3).

`uv run uvicorn reranker.main:app --port 8090`; from Java it is an ordinary HTTP call, top-50 → top-5.

**Path (b)—a hosted rerank API** (of the API options the book names Cohere Rerank, §7.4). The contract is the same—top-50 in, top-5 out—only the implementation changes: instead of your own HTTP call to `localhost:8090`, a call to the provider with a key from `.env` (no keys in code—the Module 0 rule), and a timeout is just as mandatory. Measure with the same script from §3.4, and here it is more interesting: compare the p50/p99 of your own reranker against the network round-trip to the provider, and the price per 1000 requests. The choice of path does not affect the module's outcome—it affects the "Cost/request" row in the table of §3.9.

**The rung's final step (common to both paths)—the assembly:** wrap the pipeline in a Java service, `RetrievalService` (question embedding → the hybrid SQL of §3.5 → the HTTP reranker → top-5, all of it under the RLS of §3.7)—the Module 4 harness (the `search_kb` tool) and the Module 5 MCP server will reuse it; without this assembly they will hang off scattered scripts (and a timeout on the call: the book's rule is that a network call without a timeout does not exist). Measure: hit@5 after the rerank + the rung's latency. The reranker does add latency—the cross-encoder pass runs over every candidate; the book (§7.4) considers that price tolerable precisely because the candidates number in the dozens, not the thousands. That claim is not proven for your rig—record p50/p99 in the table and see whether it is tolerable for you.

## 3.7 RBAC at retrieval: Row-Level Security

The clearance is already in the schema; now we turn on forced enforcement at the database level (§8.7 of the book—filtering *before* the output, not after):

```sql
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks FORCE ROW LEVEL SECURITY;   -- lifts the exemption for the table's OWNER; it does not touch the superuser—see below

CREATE POLICY chunks_by_clearance ON chunks
    USING (EXISTS (SELECT 1 FROM documents d
                   WHERE d.id = chunks.document_id
                     AND d.clearance <= current_setting('app.clearance')::int));

```

There is neither a `CREATE ROLE` nor a `GRANT` here, and that is not forgetfulness. The role was created by the Module 0 rig (§0.2, `initdb/02-app-user.sh`; the secret is `APP_DB_PASSWORD` in `.env`), and it received its rights on `documents` and `chunks` in §3.2, as soon as the tables were populated. This section adds exactly one thing: a policy on top of access that has already been granted.

> **Why creating the role a second time here is FORBIDDEN.** A repeated `CREATE ROLE app_user` is not "an extra line" but a way to lose the whole section. `psql -c "…"` runs several statements in **one implicit transaction**: `ERROR: role "app_user" already exists` rolls the block back ENTIRELY—along with the `ENABLE`, the `FORCE`, and the policy. Verified on the rig: after a run like that, `pg_policies` for `chunks` is empty, `relrowsecurity = f`, and the RLS tests fail. Through `psql -f` (and through a heredoc on stdin—which is how the §0.2 initdb script feeds its SQL, and why the trap does not spring there) the same block behaves differently, and worse for CI: every statement commits on its own, the error is printed, the rest goes through—and `psql` returns **0**, so the run will not go red. The difference shows up in two commands: `psql -c "CREATE TABLE probe(x int); CREATE ROLE app_user;"` leaves no `probe` at all, while the same text over stdin leaves one. If the role really is missing (the rig's volume was recreated outside §0.2), go back to §0.2 and fix the rig there rather than bolting a `CREATE ROLE` on here.

**Which role the application connects as is not a deployment detail—it is the whole point of the section.** The Module 0 rig creates the `assistant` role through `POSTGRES_USER`, and the postgres image makes that role a superuser (`rolsuper=t`, `rolbypassrls=t`). A superuser bypasses row-level security unconditionally and silently: the policy is created, `ENABLE` and `FORCE` are set, you can write the tests—and the output is not filtered at all. `FORCE ROW LEVEL SECURITY` does not save you here: it lifts the exemption for the table's **owner**, not for the superuser.

Measured on the course rig (`pgvector/pgvector:pg16`, the schema of §3.1 and the policy above—verbatim, a corpus with clearances 0 and 2 from §3.2): as `app_user` with `app.clearance=0`, the output holds only clearance-0 chunks—the restricted documents are filtered out; with `app.clearance=2` both groups come back, which is to say the filter did not eat the legitimate output. As `assistant`, the same query with `app.clearance=0` returns **both** groups—there is no filtering at all, even though the policy is created and `ENABLE` and `FORCE` are set. Repeat this contrast yourself: it is the proof that the policy is applied rather than decorating the schema. Two mandatory steps follow:

- **the application connects as `app_user`**—in both Java skeletons, `spring.datasource.username: app_user` and `password: ${APP_DB_PASSWORD}` (the config is the one in §3.3); the variable already sits in the Module 0 rig's `.env` (§0.2), and there is no need to create it again;
- **`assistant` stays the owner of the schema and the migrations**—the ingest of §3.2 runs as it too (the loader needs INSERT); production retrieval never runs as it.

**Why have `FORCE` at all, then, if `app_user` is not the owner.** Because it insures a different case, and the boundary of its effect is something you want to know before production rather than after an incident. Measured on the same rig, three roles against two states of the flag:

| The role the application runs as | `FORCE` off | `FORCE` on |
|---|---|---|
| `app_user`—neither owner nor superuser | filters | filters |
| the table's owner (not a superuser) | **does not filter** | filters |
| a superuser (`assistant`) | **does not filter** | **does not filter** |

Read it by rows: `app_user` gets filtered either way—it does not need the flag; for the table's owner the policy without `FORCE` is not applied at all, and that is who needs the flag desperately; nothing holds a superuser back. Hence the rule: keep `FORCE` on—"the application runs as the schema's owner" is the most common production configuration, and there it is exactly the difference between a working policy and a decoration; but you cannot make it stand in for the right role. No flag saves you from a superuser—only not connecting as one does.

Remember the failure class, not just this case: access control that *looks* configured fails silently and in the direction of **opening** access. That is exactly why §8.7 of the book makes access control **at retrieval, not at generation** an invariant, and praises RLS for the very fact that access is forced in the database rather than in application code (which you can forget to write). The first test below therefore checks not the policy but that the policy is applied at all.

The Java side: the clearance level comes out of the Keycloak token (the role claim from the `assistant` realm, Module 0) and is set **in the same transaction** as the query:

```java
// jdbc—on the DataSource of §3.3, which is to say as app_user. As assistant this set_config will run
// without an error and restrict nothing: a superuser sails past the policy (see the table above).
// SET LOCAL takes no bind parameters (Postgres syntax)—so we use the set_config function:
jdbc.queryForObject("SELECT set_config('app.clearance', ?, true)",   // true = until the end of the transaction (the SET LOCAL effect)
                    String.class, String.valueOf(clearanceFromJwt));
```

Mandatory tests (in CI; they stay through to the capstone):
1. **the fuse:** from the application's connection, `SELECT rolsuper OR rolbypassrls FROM pg_roles WHERE rolname = current_user` must return `false`. Without it the two tests below go green for a false reason—they cannot tell "the policy worked" from "nobody applied the policy";
2. a user with `clearance=0` does not get a chunk of a document at clearance 2—neither through a direct question nor through a request to "quote me all the policies";
3. recall on the golden set with RLS on has not dropped for a high-privilege user (the filter did not eat the legitimate output, §8.6 of the book).

## 3.8 Deletion and the tombstone

The "right to deletion" scenario (§8.3 + §25.4 of the book):

```sql
-- LIKE, not exact equality: the loader of §3.2 puts the result of glob("../corpus/*.md") into path,
-- which is to say '../corpus/vozvrat-nq.md'—with the prefix. An exact comparison gives DELETE 0, and all three
-- observations below will hang off an empty operation.
DELETE FROM documents WHERE path LIKE '%vozvrat-nq.md';   -- the chunks go with it, by cascade
```

Then three observations: (1) a query from the golden set that used to land in this document no longer returns it; (2) `SELECT pg_relation_size('chunks_embedding_hnsw');`—the index size **has not shrunk**: the HNSW graph still holds tombstone nodes; (3) after `REINDEX INDEX chunks_embedding_hnsw;` the size drops, and there is a latency spike for the duration of the rebuild—catch it in your measurement. The conclusion goes into a mini-ADR: how often to rebuild the index at your own rate of deletions.

## 3.9 The results table and the mini-ADR

The table template (every number from one and the same golden set):

| Rung | hit@5 | faithfulness | answer rel. | p50, ms | p99, ms | Cost/request |
|---|---|---|---|---|---|---|
| Naive (baseline) | | | | | | |
| + Hybrid RRF | | | | | | |
| + Reranker | | | | | | |

A mini-ADR, "which rung I stopped at," in the §26.3 format: context (the numbers from the table) → decision → consequences → **rejected alternatives** (the remaining rungs of the ladder and why their gain does not pay for its price). The fourth element is no formality here: "which rung I stopped at" *is* the decision to reject the remaining rungs, and without it the ADR records not a choice but a fact. Almost every example in §26.4 of the book shows this block—10 ADRs out of 12; the only ones without it are ADR-10 (observability) and ADR-11 (cost and latency), both of which break off at "Consequences." Check yourself against any of the other ten. The canonical trap the ADR has to close explicitly: an improvement of 2–3 pp on a set of 50 questions is noise (§17.7 of the book; you'll apply the sample-size formula in Module 6—an honest caveat is enough here).

## 3.10 The DoD checklist

- [ ] The table of §3.9 is filled in for all three rungs, every row from the same golden set.
- [ ] The 5–7 "questions with no answer"—the share of honest refusals is measured (naive usually hallucinates on at least some of them—record it).
- [ ] The RLS tests (all three from §3.7) are green in CI—including the fuse "the application is connected as a NON-superuser": without it the other two prove nothing.
- [ ] The tombstone observation is written down in numbers (index size before/after REINDEX).
- [ ] The mini-ADR is written and reads without spoken commentary.
- [ ] The pipeline is assembled into `RetrievalService` (§3.6)—the reuse point for Modules 4/5.
