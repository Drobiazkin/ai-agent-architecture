<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Module 0 — The Rig: In Depth

*A companion to "Module 0" in the course overview (README.md). What's here: the commands, the configs, and the skeletons; the goals and the DoD are in the overview.*

> **The skeleton rule.** Everything below is a working starting point as of this edition (July 2026). Verify image tags and dependency versions before you `pull`: with young tools, a minor version breaks the API. If a command fails—that is the course's first assignment: read the error and fix the rig yourself; that is exactly the point of Module 0.

## 0.1 The project directory

One repository for the whole course—the end-to-end domain grows module by module instead of being recreated from scratch:

```
support-assistant/
├── infra/
│   ├── docker-compose.yml      # Postgres+pgvector, Keycloak
│   └── initdb/                 # 01-extensions.sql, 02-app-user.sh
├── app-springai/               # skeleton #1 (Java, Spring AI)
├── app-lc4j/                   # skeleton #2 (Java, LangChain4j)
├── py/                         # the Python track (Modules 1, 3, 6, 7)
├── corpus/                     # 30–50 policy documents
└── .env                        # keys and passwords—IN .gitignore FROM THE FIRST COMMIT
```

```bash
git init support-assistant && cd support-assistant
printf '.env\n*.iml\n.idea/\ntarget/\nbuild/\n__pycache__/\n.venv/\n' > .gitignore
git add .gitignore && git commit -m "rig: scaffolding"
```

## 0.2 The infrastructure: docker-compose

`infra/docker-compose.yml`—Postgres with pgvector, and Keycloak. Langfuse is installed separately (below, §0.5): its official compose drags in a ClickHouse/Redis/MinIO of its own, and splicing that in here means going to war with someone else's updates.

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16        # Postgres 16 + the vector extension
    environment:
      POSTGRES_USER: assistant                 # the schema OWNER. The image makes this role a superuser—see below
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: assistant
      APP_DB_PASSWORD: ${APP_DB_PASSWORD}      # the application role's password; initdb/02-app-user.sh creates the role
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./initdb:/docker-entrypoint-initdb.d   # runs on the FIRST start of an empty volume
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U assistant"]
      interval: 5s
      retries: 10

  keycloak:
    image: quay.io/keycloak/keycloak:26.2      # check the current tag
    command: start-dev                          # dev mode: http, no external DB
    environment:
      KC_BOOTSTRAP_ADMIN_USERNAME: admin
      KC_BOOTSTRAP_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
    ports: ["8081:8080"]

volumes:
  pgdata:
```

`infra/initdb/01-extensions.sql`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

`infra/initdb/02-app-user.sh`—the role the application serves requests under (`chmod +x` is mandatory; the entrypoint executes a `.sh` as a script, while a `.sql` cannot substitute environment variables—which is why the password arrives through the shell):

```bash
#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
  CREATE ROLE app_user LOGIN PASSWORD '${APP_DB_PASSWORD}';
  GRANT USAGE ON SCHEMA public TO app_user;
SQL
```

**Why a second role—not bureaucracy, but the one thing that will make Module 3's RLS work at all.** The Postgres image makes the role from `POSTGRES_USER` (`assistant` for us) a superuser, and a superuser bypasses row-level security—per-row access filtering by the database's own machinery—unconditionally: the policy is written, but it applies to not a single row. `FORCE ROW LEVEL SECURITY`, which Module 3 turns on for the table, does not close this hole—FORCE removes the exemption for the table's *owner*, but not for a superuser. It fails toward open access: the protection looks configured and silently does nothing. Hence the split from day one: `assistant`—the schema owner, the migrations, and the corpus loading; `app_user`—what the application reads data with, on behalf of the user. `app_user` gets its rights on the tables in Module 3 (§3.2)—the moment the tables exist and are filled, because §3.3 already switches the application over to that role. From there the rule holds to the end of the course: **every new table grants `app_user` its rights in the same place the table is created** (Module 4—`saga_steps`, `tickets`, `pending_actions`; Module 5—the notifications log). From Module 3 on, the application connects under no other role, so a table without a grant simply does not exist as far as it is concerned.

Startup and verification:

```bash
cd infra
printf 'POSTGRES_PASSWORD=dev-only-pass\nKEYCLOAK_ADMIN_PASSWORD=dev-only-admin\nAPP_DB_PASSWORD=dev-only-app\n' >> ../.env
docker compose --env-file ../.env up -d
docker compose ps                          # both healthy/running
psql postgresql://assistant:dev-only-pass@localhost:5432/assistant \
  -c "SELECT extversion FROM pg_extension WHERE extname='vector';"   # version ≥ 0.7
psql postgresql://assistant:dev-only-pass@localhost:5432/assistant \
  -c "SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname IN ('assistant','app_user');"
#  assistant | t | t   ← bypasses RLS; the application must not connect under it
#  app_user  | f | f   ← this is what the application will connect under from Module 3 on
psql postgresql://app_user:dev-only-app@localhost:5432/assistant -c "SELECT current_user;"  # the role logs in
```

If `app_user` is not in the output, the volume already existed—and `initdb` only runs on an empty one: `docker compose --env-file ../.env down -v && docker compose --env-file ../.env up -d` (at Module 0 there is nothing to lose). Skipping this step quietly is not an option—Module 3 will either hit a missing role or, worse, run under `assistant` with no filtering whatsoever.

Keycloak: open `http://localhost:8081`, log in as admin, create the realm `assistant`—the roles and clients are needed in Module 3 (RLS) and Module 5 (OAuth on MCP); an empty realm is enough for now.

**Gotcha, macOS/Colima:** Keycloak and Postgres together ask for ~2 GB; if containers are dying on OOM, raise the Docker Desktop memory (Settings → Resources) to 4+ GB.

## 0.3 Local models: Ollama

```bash
# macOS: brew install ollama && brew services start ollama
# Linux:  curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:4b        # the "small" one—fast iterations, cheap runs
ollama pull qwen3:8b        # the "medium" one—the course's main workhorse
ollama pull bge-m3          # the embedder for Module 3 (multilingual, 1024 dimensions)
ollama run qwen3:4b "Answer in one word: are you working?"
```

Ollama listens on `http://localhost:11434` and serves two APIs: its own (`/api/generate`, `/api/embed`) and an OpenAI-compatible one (`/v1/...`)—the second one lets frameworks work with a local model "as if it were a provider." Checking without code:

```bash
curl -s http://localhost:11434/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model": "qwen3:4b",
  "messages": [{"role": "user", "content": "ping"}]
}' | head -c 400
```

The model choice is a guide, not dogma: look at what fits in your memory. The course's estimate (the arithmetic is ours; the book does not have it): weights ≈ parameters × bytes per parameter, and 4 bits is 0.5 bytes plus the quantization constants, for ≈ 0.5–0.6 bytes per parameter in total. What the book gives is not this arithmetic but the inference-quantization formats themselves—AWQ/GPTQ, FP8, INT8 (§22.6)—and the formula for the size of the KV-cache, the second consumer of memory after the weights (§1.6). 8B at Q4 ≈ 5 GB—comfortable on 16 GB of RAM.

## 0.4 A hosted provider: the key and the spending limit

The order of operations matters more than the provider:

1. Create a key in the provider's console.
2. **The limit first, the first call second**: set a monthly hard limit ($10–20/month is enough for the course—$30–60 is budgeted for all of it) and an alert at 50%.
3. The key goes only into `.env`: `LLM_API_KEY=...`; in configs, through `${LLM_API_KEY}`. Check that `.env` is in `.gitignore` **before** you put the key there.

Course rule #5 ("spend little") is enforced by the default routing: everything that can run on Ollama runs on Ollama; hosted goes where an assignment compares quality or needs frontier capabilities.

## 0.5 Observability: Langfuse self-hosted

The official way (the compose file lives in their repository and is updated along with the product):

```bash
git clone https://github.com/langfuse/langfuse.git ~/langfuse
cd ~/langfuse
docker compose up -d          # brings up web + worker + ClickHouse + Redis + MinIO + Postgres
```

Open `http://localhost:3000`, create an organization/project, and save the `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` pair into `.env`. Wiring it up from code is Module 2's assignment (item 5); at Module 0 a live UI is enough.

**Gotcha:** the Langfuse v3 stack is the heaviest piece of the rig (another ~2–3 GB). If resources are tight, bring it up only from Module 2, when you actually need it.

## 0.6 Java skeleton #1: Spring Boot + Spring AI

Generating the project (or the same thing with a mouse at start.spring.io):

```bash
mkdir app-springai && cd app-springai          # the Initializr archive is flat: pom/src land right here
curl -s https://start.spring.io/starter.tgz \
  -d type=maven-project -d javaVersion=21 -d bootVersion=3.5.0 \
  -d groupId=ru.course -d artifactId=app-springai -d dependencies=web \
  | tar -xzf -
cd ..
```

In `pom.xml`—the Spring AI BOM and the Ollama starter (the artifacts come from the docs for your version; in 1.0 GA the starters are named `spring-ai-starter-model-*`):

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.ai</groupId>
      <artifactId>spring-ai-bom</artifactId>
      <version>1.0.0</version>   <!-- check the current one; the Module 2 / Module 5 assignments depend on it -->
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
<dependencies>
  <dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-ollama</artifactId>
  </dependency>
</dependencies>
```

`src/main/resources/application.yml`:

```yaml
spring:
  ai:
    ollama:
      base-url: http://localhost:11434
      chat:
        options:
          model: qwen3:4b
          temperature: 0.0
```

The smoke test—a CommandLineRunner with `ChatClient` (the central abstraction that Modules 2 and 5 are built on):

```java
@SpringBootApplication
public class App {
    public static void main(String[] args) { SpringApplication.run(App.class, args); }

    @Bean
    CommandLineRunner hello(ChatClient.Builder builder) {
        return args -> System.out.println(
            builder.build().prompt().user("Say exactly one word: hello").call().content());
    }
}
```

`./mvnw spring-boot:run` → the model's answer in the console.

**Wire up the hosted provider right now**—the Module 0 DoD (§0.10) requires a "hello" through the hosted API as well: the hosted starter next to the ollama starter plus a separate profile (three lines of yml with the `${LLM_API_KEY}` from §0.4); you switch with `--spring.profiles.active=hosted`. The course's working model stays Ollama; comparing provider quality is Module 2's assignment.

## 0.7 Java skeleton #2: LangChain4j

A second empty project (`app-lc4j`, the same start.spring.io without the AI dependencies); in `pom.xml`:

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j</artifactId>
  <version>1.0.1</version>   <!-- check it; the 0.x and 1.x APIs are incompatible -->
</dependency>
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-ollama</artifactId>
  <version>1.0.1</version>
</dependency>
```

The smoke test (the low-level API; AiServices with `@Tool` is Module 5 material):

```java
var model = OllamaChatModel.builder()
        .baseUrl("http://localhost:11434")
        .modelName("qwen3:4b")
        .temperature(0.0)
        .build();
System.out.println(model.chat("Say exactly one word: hello"));
```

The same DoD minimum applies here as in §0.6: **the hosted provider gets wired up now**—a second dependency (`langchain4j-open-ai` or your provider's module) and a second model builder next to `OllamaChatModel`, with the key from `${LLM_API_KEY}`. The default stays Ollama.

Why two skeletons from day one: Module 5 compares composition styles (Advisors versus AiServices)—and the comparison is honest only if both projects live on the same rig with the same models.

## 0.8 The Python track: uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # or brew install uv
mkdir py && cd py && uv init --python 3.12
uv add torch jupyter pytest
uv run python -c "import torch; print(torch.__version__, torch.backends.mps.is_available())"

mkdir tests
printf 'def test_torch_imports():\n    import torch\n\n    assert torch.__version__\n' > tests/test_smoke.py
uv run pytest    # 1 passed, exit code 0—THAT is a green run
```

**About an empty `pytest`.** A run without a single test is NOT green: pytest prints `no tests ran` and returns code **5** (`EXIT_NOTESTSCOLLECTED`), not 0—0 means "all tests passed," 1 means "there were failures." `uv run` passes the code through as is, so for the shell (`$?`) and for CI such a run is red. Hence `tests/test_smoke.py` above: the DoD requires a green `pytest`, and green it is only with a real test. Remember the number 5—CI arrives as early as Module 3 (the RLS tests) and Module 6 (the eval gate), and one day the pipeline will go red exactly like this: the tests were not collected (wrong `rootdir`, wrong filename prefix), and it looks "as if nothing ran at all."

A phrasebook for the Java developer: `pyproject.toml` ≈ `pom.xml`, `uv add` ≈ adding a dependency, `uv run` ≈ `mvn exec`, `pytest` ≈ JUnit, type hints ≈ generics without the compiler checking them (`mypy` does the checking; wire it in if you like).

**The language itself comes from the primer, `course/python-primer.md`** ("Python for the Java Developer": every construct through a contrast with Java). The plan is in there too, §14: evening 1—sections 1–5 plus the first script over `corpus/` (the course's hello world); evening 2—sections 6–12 plus the first `pytest`. From there on, every Python snippet in the modules comes with a "Syntax walkthrough" block that links back to the primer—no separate Python book is needed; the reference to grow into is the official tutorial at docs.python.org.

## 0.9 The corpus for the end-to-end domain

30–50 support-desk policy documents in `corpus/` (markdown). If you have no real ones, synthesize them and **proofread them** (the rule: a generated document that has not been proofread does not go into the corpus, or Module 3's golden set will be measuring retrieval quality against hallucinations):

```bash
ollama run qwen3:8b "Напиши внутренний регламент службы поддержки интернет-магазина:
«Возврат товара ненадлежащего качества». Структура: область действия, сроки,
пошаговая процедура оператора, исключения. 400-600 слов, деловой стиль." > corpus/vozvrat-nq.md
```

Vary the topics (returns, delivery, payment, escalation, personal data, warranty…)—Module 3 needs both pairs of documents close in subject matter (a check on the reranker) and "questions with no answer in the corpus."

## 0.10 The DoD checklist

```bash
docker compose -f infra/docker-compose.yml ps               # postgres, keycloak: Up
psql ...  -c "SELECT extname FROM pg_extension;"            # vector is in place
psql ...  -c "SELECT rolname,rolsuper FROM pg_roles WHERE rolname='app_user';"   # exists, rolsuper=f—otherwise RLS in Module 3 is dead
curl -s localhost:11434/v1/models | head -c 200             # Ollama answers
(cd app-springai && ./mvnw -q spring-boot:run)              # "hello" from Ollama
(cd app-lc4j     && ./mvnw -q spring-boot:run)              # "hello" from Ollama
(cd py && uv run pytest; echo "exit=$?")                    # 1 passed, exit=0 (not 5!)
ls corpus | wc -l                                           # ≥ 30
```

Plus two items with no commands: the spending limit at the hosted provider is set (a screenshot into the decision journal); `.env` is not in git (`git check-ignore .env` returns the path). Both skeletons must answer "hello" through the hosted API as well (as the overview's DoD requires)—that will verify the key, the limits, and the configuration of both frameworks before they are needed under pressure in Modules 2 and 5.
