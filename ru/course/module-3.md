<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Модуль 3 — RAG на своём стеке: детализация

*Спутник задания «Модуль 3» из `ai-agent-practice-course.md`. Порядок разделов = порядок пунктов задания. Правило скелетов — как в module-0.md: версии сверяй, работоспособность доказывает стенд.*

Сквозная дисциплина модуля — из гл. 9 книги: **ни одной ступени лестницы без замера на золотом наборе**. Поэтому структура такая: схема (§3.1) → ingestion (§3.2) → naive baseline (§3.3) → золотой набор и метрики (§3.4) — и только потом улучшения (§3.5–3.6), каждое против baseline.

## 3.1 Схема данных

```sql
CREATE TABLE documents (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    path       text UNIQUE NOT NULL,
    title      text NOT NULL,
    clearance  int  NOT NULL DEFAULT 0,      -- гриф доступа: 0 — всем, 1 — операторам, 2 — руководству
    created_at timestamptz DEFAULT now()
);

CREATE TABLE chunks (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id bigint NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    seq         int    NOT NULL,             -- порядок чанка в документе
    content     text   NOT NULL,
    embedding   vector(1024) NOT NULL,       -- 1024 = размерность bge-m3; сменишь эмбеддер — пересоздашь колонку и ПЕРЕИНДЕКСИРУЕШЬ ВСЁ (§7.6 книги)
    tsv         tsvector GENERATED ALWAYS AS (to_tsvector('russian', content)) STORED
);

-- ANN-индекс (§8.3): m и ef_construction — стартовые, крутить будешь осознанно
CREATE INDEX chunks_embedding_hnsw ON chunks
    USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- полнотекстовый — для hybrid-ступени §3.5
CREATE INDEX chunks_tsv_gin ON chunks USING gin (tsv);
```

Гриф на `documents`, а не на `chunks`, — доступ определяется документом; в выборках он доезжает до чанка джойном (и в §3.7 ляжет в RLS-политику).

## 3.2 Ingestion

Чанкинг для регламентов — по заголовкам, с ограничением размера. Стартовое правило из §7.6 книги: смысловые границы важнее равных кусков (там же размер — 256–1024 токена, отправная точка 512 с перекрытием 25%). Прикидка курса под русские регламенты — числа наши, в книге их нет: 300–500 токенов ≈ 900–1500 символов, что и даёт `max_chars=1200` ниже. Проверь на своём корпусе токен-калькулятором из М1:

```python
# py/ingest.py — запускается: uv add httpx psycopg[binary] && uv run python ingest.py
import glob, re, httpx, psycopg

def chunk(md: str, max_chars: int = 1200) -> list[str]:
    parts = re.split(r"(?=^#{1,3} )", md, flags=re.M)          # режем по заголовкам
    out = []
    for p in parts:
        p = p.strip()
        while len(p) > max_chars:                               # длинные секции — дорезаем по абзацам
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

# ingest идёт под ВЛАДЕЛЬЦЕМ схемы (assistant) — ему нужен INSERT; боевой ретрив ходит под app_user (§3.7)
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

**Разбор синтаксиса** (ссылки — на разделы `python-primer.md`):
- `def chunk(md: str, max_chars: int = 1200) -> list[str]:` — типы-подсказки и параметр по умолчанию (§5 праймера); вызывать можно `chunk(text)` или `chunk(text, max_chars=800)`.
- `re.split(r"(?=^#{1,3} )", md, flags=re.M)` — модуль `re` ≈ Pattern/Matcher одним вызовом; `r"..."` — raw-строка (как не экранировать `\` в Java-регэкспах мечталось); `(?=...)` — lookahead, режет *перед* заголовком, не съедая его.
- `p[:cut]` и `p[cut:]` — срезы: «до cut» и «от cut до конца» (§3).
- `if p: out.append(p)` — truthiness: «если строка непуста» (§2).
- `zip(pieces, embed(pieces))` и `enumerate(...)` — параллельный обход и обход с индексом (§4); `for seq, (c, e) in ...` — распаковка кортежа прямо в заголовке цикла.
- `with psycopg.connect(...) as conn:` — try-with-resources (§8): закрытие соединения гарантировано.
- `.fetchone()[0]` — первая колонка первой строки результата (≈ `rs.next(); rs.getLong(1)`).

Проверка: `SELECT count(*) FROM chunks;` — при 30–50 документах жди порядка 150–400 чанков. Меньше — чанки слишком крупные; сильно больше — фрагментация (§7.6, страдает связность).

**Проставь грифы — сейчас, не в §3.7.** Загрузчик выше колонку `clearance` не трогает, значит весь корпус приезжает с умолчанием `0` («видно всем»). На таком корпусе RLS §3.7 нечего фильтровать, а тест «пользователь с `clearance = 0` не получает документ с грифом 2» проверяет пустоту и зеленеет ни о чём:

```sql
-- 3-5 документов под гриф; бери темы, где ограничение осмысленно (эскалация, персональные данные)
UPDATE documents SET clearance = 2 WHERE path LIKE '%eskalac%' OR path LIKE '%pers-dan%';
SELECT clearance, count(*) FROM documents GROUP BY clearance ORDER BY clearance;  -- нужно ≥ 2 уровня
```

Гриф проставляется здесь ещё и потому, что Путь B §3.3 переливает в свою таблицу только открытую часть корпуса — а «открытая часть» определена лишь после того, как грифы расставлены.

**Выдай права роли приложения — здесь, до первого чтения из кода.** Всё выше сделано владельцем (`assistant`), а с §3.3 приложение подключается под `app_user`: стенд М0 (§0.2) завёл роль и дал ей только `USAGE ON SCHEMA public` — прав на таблицы у неё нет, потому что на М0 таблиц ещё не было. Теперь они есть и наполнены:

```sql
-- Владелец (assistant) выдаёт роли приложения право читать корпус. Писать в него app_user не должен:
-- ingest и миграции идут под владельцем, боевой ретрив — только читает.
GRANT SELECT ON documents, chunks TO app_user;
```

Правило на весь курс, а не на этот раздел: **таблицу заводит владелец — права `app_user` выдаются там же, где заводится таблица.** С §3.3 приложение не ходит ни под кем другим, поэтому таблица без гранта для него не существует. М4 (`saga_steps`, `tickets`, `pending_actions`) и М5 (журнал уведомлений) следуют тому же правилу — грант стоит рядом с их DDL. Пропустишь — получишь `ERROR: permission denied for table …` в первом же разделе, который читает данные из кода.

## 3.3 Ступень 0: Naive RAG (baseline)

Два пути, но **не равноправных**: лестница §3.5–3.6 и RLS §3.7 живут на Пути A, потому что стоят на схеме §3.1. Путь B — короткая вылазка, чтобы увидеть `QuestionAnswerAdvisor` в работе; почему он на курсовую схему не ложится — ниже. Начинай с Пути A.

**Путь A — своими руками (SQL top-k → промпт).** Ретрив:

```sql
-- $1 — вектор вопроса (тем же bge-m3!), оператор <=> — косинусное РАССТОЯНИЕ (меньше = ближе)
SET hnsw.ef_search = 40;                       -- кандидатов при обходе графа; recall/латентность (§8.3)
SELECT c.id, d.title, c.content, 1 - (c.embedding <=> $1) AS cos_sim
FROM chunks c JOIN documents d ON d.id = c.document_id
ORDER BY c.embedding <=> $1
LIMIT 5;
```

Промпт генерации — минимальный честный шаблон (обособление недоверенного контента — привычка с М2):

```
Ответь на вопрос пользователя ТОЛЬКО по приведённым фрагментам регламентов.
Если ответа во фрагментах нет — скажи «в регламентах не найдено» и ничего не выдумывай.
<fragments>{top-5 чанков, каждый с заголовком документа}</fragments>
Вопрос: {вопрос}
```

**Путь B — Spring AI, на отдельной таблице.** `PgVectorStore` (BOM 1.0.0 из М0) работает только со своим контрактом таблицы: `(id, content, metadata json, embedding vector(N))`. Имена колонок **зашиты в код**, ручки для их переименования не существует — настраиваются только `schemaName`, `vectorTableName`, `idType`, `distanceType`, `indexType`, `dimensions`. Поиск он делает как `SELECT *, embedding <=> ? AS distance FROM {table}`, а маппер строк читает у каждой строки колонку `metadata`. В `chunks` из §3.1 колонки `metadata` нет вовсе, поэтому `table-name: chunks` — заведомо сломанный конфиг: при `initialize-schema: false` расхождение не всплывает на старте, запрос падает при первом же обращении советника. Так что Путь B поднимаем на **отдельной** таблице под его контракт:

```sql
-- Путь B: учебная таблица под контракт PgVectorStore; DDL своей версии сверь с её schema.sql в jar
CREATE TABLE spring_ai_chunks (
    id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content   text,
    metadata  json,
    embedding vector(1024)                                  -- та же bge-m3
);
CREATE INDEX ON spring_ai_chunks USING hnsw (embedding vector_cosine_ops);

-- Наполнение. Эмбеддинги уже посчитаны в §3.2 тем же bge-m3 — переливаем их, а не считаем заново.
-- Только открытая часть корпуса (clearance = 0): RLS §3.7 на эту таблицу не распространяется,
-- грифованному в ней не место. Выполняется владельцем (assistant), как и DDL выше.
INSERT INTO spring_ai_chunks (content, metadata, embedding)
SELECT c.content, json_build_object('document_id', c.document_id, 'seq', c.seq), c.embedding
FROM chunks c JOIN documents d ON d.id = c.document_id
WHERE d.clearance = 0;

-- Роль app_user заведена стендом М0 (§0.2). Советник только читает — INSERT ему не нужен.
GRANT SELECT ON spring_ai_chunks TO app_user;
```

```yaml
spring:
  datasource:                           # общий DataSource приложения — и для Пути A, и для Пути B
    url: jdbc:postgresql://localhost:5432/assistant
    username: app_user                  # НЕ assistant: под суперпользователем RLS §3.7 не отфильтрует ничего
    password: ${APP_DB_PASSWORD}        # уже в .env стенда с М0 (§0.2)
  ai:
    vectorstore:
      pgvector:
        initialize-schema: false        # схему держим свою — DDL выше, владельцем
        table-name: spring_ai_chunks    # ОТДЕЛЬНАЯ от chunks §3.1: см. абзац выше
        dimensions: 1024
```

`initialize-schema: false` здесь не вкусовщина, а следствие роли: у `app_user` нет прав создавать таблицы, и попытка советника «поднять схему самому» упрётся в отказ. Схему и данные кладёт владелец — блоком выше.

Советник поверх `ChatClient`:

```java
ChatClient rag = builder
    .defaultAdvisors(QuestionAnswerAdvisor.builder(vectorStore)
        .searchRequest(SearchRequest.builder().topK(5).build())
        .build())            // сигнатуры builder'а — сверь с BOM из М0
    .build();
```

Цена честности: грифы и RLS §3.7 на `spring_ai_chunks` не распространяются — это стенд советника, а не боевой ретрив. Именно поэтому переливка выше берёт только `clearance = 0`: копия корпуса в таблице без политики — это обход RLS, сделанный своими руками. Проверено на стенде: без фильтра `app_user` читает через `spring_ai_chunks` тот самый грифованный чанк, который в `chunks` ему политика не отдаёт. Так утечка и заводится в проде — не дырой в политике, а второй копией данных рядом с ней. И учти, что переливка — **снимок**, а не представление: поднимешь гриф документу после неё (в §3.7 или позже) — копия останется открытой. Закончил смотреть на советника — `DROP TABLE spring_ai_chunks;`, это учебная таблица и жить дольше вылазки ей незачем. Хочешь Spring AI поверх курсовой схемы — придётся либо приводить §3.1 к контракту (`metadata json` — тот же тип, что в DDL выше, а `document_id`/`seq`/`clearance` внутрь неё — тогда политика §3.7 и RRF-запрос §3.5 переписываются на `metadata->>'document_id'`), либо писать свой `VectorStore`. Оба варианта — за рамками модуля, но осознай развилку: это и есть цена чужой абстракции поверх своей схемы.

## 3.4 Золотой набор и замер baseline

`py/golden.yaml` — 50 пар, из них 5–7 «без ответа в корпусе» (проверка честного отказа):

```yaml
- q: "В какой срок оформляется возврат товара ненадлежащего качества?"
  expected_chunk_substr: "14 дней"        # якорь для hit rate: подстрока нужного чанка
  answer: "Возврат оформляется в течение 14 дней с момента обращения."
- q: "Какой номер телефона у генерального директора?"
  expected_chunk_substr: null              # ответа в корпусе НЕТ — эталон поведения: отказ
  answer: "в регламентах не найдено"
```

**Hit rate ретрива** (свой скрипт — метрика ступени ретрива, до генерации):

```python
# py/eval_retrieval.py: для каждого q — эмбеддинг → top-k из БД → нашлась ли подстрока
anchored = [g for g in golden if g["expected_chunk_substr"]]   # вопросы «без ответа в корпусе» не про ретрив
n = len(anchored)                                              # знаменатель — только они, иначе hit@5 занижен
hits = sum(any(g["expected_chunk_substr"] in c for c in topk(g["q"], k=5))
           for g in anchored)
print(f"hit@5 = {hits}/{n} = {hits/n:.0%}")
```

**Разбор синтаксиса:** это одна агрегация в стиле stream-конвейера (§3 праймера; по-русски такую конструкцию часто зовут «свёрткой» в смысле fold/reduce — третье значение слова из §A.3 книги, не контракция). Изнутри наружу: `подстрока in c` — оператор принадлежности; `any(... for c in topk(...))` — «хоть один чанк содержит якорь» (≈ `anyMatch`); внешний `sum(... for g in golden if ...)` — считает истинные по всем вопросам с якорем (`True` арифметически равен 1 — поэтому sum считает попадания; ≈ `filter(...).count()`); `if g[...]` в конце — фильтр «пропусти вопросы без ответа» (у них якорь `None`, он ложен). `f"...{hits/n:.0%}"` — f-строка с форматом «проценты без знаков после запятой» (§2).

**Генеративные метрики — RAGAS** (faithfulness, answer relevancy; судья — на дешёвом ярусе, правило курса №5):

```python
# uv add ragas datasets — API RAGAS меняется, сверь с установленной версией
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
result = evaluate(dataset, metrics=[faithfulness, answer_relevancy])  # dataset: q/answer/contexts
```

Числа baseline запиши в таблицу §3.9 **до** любых улучшений — иначе улучшения не с чем сравнивать, и модуль превращается в карго-культ.

## 3.5 Ступень 1: Hybrid (BM25-класс + RRF)

Полнотекстовая ветка уже готова (колонка `tsv`). Слияние — RRF прямо в SQL (формула и мини-пример — §7.3 книги):

```sql
WITH vec AS (
    SELECT id, row_number() OVER (ORDER BY embedding <=> $1) AS r
    FROM chunks ORDER BY embedding <=> $1 LIMIT 50
), fts AS (
    SELECT id, row_number() OVER (ORDER BY ts_rank(tsv, q) DESC) AS r
    FROM chunks, websearch_to_tsquery('russian', $2) q
    WHERE tsv @@ q
    ORDER BY ts_rank(tsv, q) DESC LIMIT 50   -- ORDER BY нужен и у САМОГО запроса: LIMIT без него режет произвольные 50
)
SELECT COALESCE(v.id, f.id) AS id,
       COALESCE(1.0/(60 + v.r), 0) + COALESCE(1.0/(60 + f.r), 0) AS rrf
FROM vec v FULL OUTER JOIN fts f USING (id)
ORDER BY rrf DESC LIMIT 5;
```

Замер тем же скриптом §3.4. Ожидание (не гарантия): hybrid добирает вопросы с точными токенами — номера приказов, артикулы, аббревиатуры; проверь на своих «точных» вопросах отдельно.

## 3.6 Ступень 2: Reranking

Cross-encoder поверх top-50 гибридной выдачи. Путь (а) — свой микросервис (первый Python-сервис стенда):

```python
# py/reranker/main.py — uv add fastapi uvicorn sentence-transformers
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import CrossEncoder

app = FastAPI()
model = CrossEncoder("BAAI/bge-reranker-v2-m3")   # мультиязычный; качается при первом старте

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

**Разбор синтаксиса:** `class Req(BaseModel)` — pydantic-модель: одновременно DTO и валидация, как Jackson + Bean Validation в одном классе (§13 праймера) — FastAPI сам распарсит JSON тела в `Req` и вернёт 422 при несоответствии; `@app.post("/rerank")` — декоратор-регистрация обработчика, читается как `@PostMapping` (§10); `[(r.query, p) for p in r.passages]` — list comprehension, строит пары «вопрос-пассаж» (§3); `sorted(..., key=lambda x: -x[1])` — сортировка по убыванию второго элемента пары (§5); `ranked[:r.top_k]` — срез первых top_k (§3).

`uv run uvicorn reranker.main:app --port 8090`; из Java — обычный HTTP-вызов top-50 → top-5.

**Путь (б) — hosted rerank-API** (из API-вариантов книга называет Cohere Rerank, §7.4). Контракт тот же — top-50 на вход, top-5 на выход, — меняется только реализация: вместо своего HTTP-вызова на `localhost:8090` вызов провайдера с ключом из `.env` (никаких ключей в коде — правило М0), и тайм-аут обязателен так же. Замер — тем же скриптом §3.4, и здесь он интереснее: сравни p50/p99 своего реранкера против сетевого round-trip до провайдера и цену за 1000 запросов. Выбор пути на итог модуля не влияет — влияет на строку «Стоимость/запрос» в таблице §3.9.

**Финальный шаг ступени (общий для обоих путей) — сборка:** оформи конвейер Java-сервисом `RetrievalService` (эмбеддинг вопроса → hybrid-SQL §3.5 → HTTP-реранкер → top-5, всё под RLS §3.7) — его будут переиспользовать харнесс М4 (инструмент `search_kb`) и MCP-сервер М5; без этой сборки они повиснут на разрозненных скриптах (и тайм-аут на вызов: правило книги — сетевой вызов без тайм-аута не существует). Замер: hit@5 после реранка + латентность ступени. Реранкер латентность добавляет — проход cross-encoder идёт по каждому кандидату; книга (§7.4) считает эту плату терпимой ровно потому, что кандидатов десятки, а не тысячи. Это утверждение про твой стенд не доказано — зафиксируй p50/p99 в таблицу и посмотри, терпимо ли оно у тебя.

## 3.7 RBAC на ретриве: Row-Level Security

Гриф уже в схеме; включаем принудительное применение на уровне БД (§8.7 книги — фильтрация *до* выдачи, а не после):

```sql
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks FORCE ROW LEVEL SECURITY;   -- снимает исключение с ВЛАДЕЛЬЦА таблицы; суперпользователя не касается — см. ниже

CREATE POLICY chunks_by_clearance ON chunks
    USING (EXISTS (SELECT 1 FROM documents d
                   WHERE d.id = chunks.document_id
                     AND d.clearance <= current_setting('app.clearance')::int));

```

Ни `CREATE ROLE`, ни `GRANT` здесь нет — и это не забывчивость. Роль завёл стенд М0 (§0.2, `initdb/02-app-user.sh`, секрет — `APP_DB_PASSWORD` в `.env`), права на `documents` и `chunks` она получила в §3.2, как только таблицы наполнились. Раздел добавляет ровно одно: политику поверх уже выданного доступа.

> **Почему заводить роль здесь второй раз НЕЛЬЗЯ.** Повтор `CREATE ROLE app_user` — не «лишняя строка», а способ потерять весь раздел. `psql -c "…"` выполняет несколько statement'ов **одной неявной транзакцией**: `ERROR: role "app_user" already exists` откатывает блок ЦЕЛИКОМ — вместе с `ENABLE`, `FORCE` и политикой. Проверено на стенде: после такого прогона `pg_policies` для `chunks` пуст, `relrowsecurity = f`, а RLS-тесты падают. Через `psql -f` (и через heredoc по stdin — так подаёт SQL initdb-скрипт §0.2, поэтому там эта ловушка и не срабатывает) тот же блок ведёт себя иначе и хуже для CI: каждый statement коммитится сам, ошибка печатается, остальное проходит — и `psql` возвращает **0**, то есть красным прогон не станет. Разницу видно на двух командах: `psql -c "CREATE TABLE probe(x int); CREATE ROLE app_user;"` не оставляет `probe` вовсе, тот же текст по stdin — оставляет. Если роли всё-таки нет (том стенда пересоздан не по §0.2) — вернись в §0.2 и почини стенд там, а не дописывай `CREATE ROLE` сюда.

**Под какой ролью подключается приложение — это не деталь развёртывания, а весь смысл раздела.** Стенд М0 заводит роль `assistant` через `POSTGRES_USER`, а образ postgres делает эту роль суперпользователем (`rolsuper=t`, `rolbypassrls=t`). Суперпользователь обходит row-level security (построчную фильтрацию на стороне БД) безусловно и молча: политика создана, `ENABLE` и `FORCE` выставлены, тесты можно писать — а выдача не фильтруется вообще. `FORCE ROW LEVEL SECURITY` здесь не спасает: он снимает исключение с **владельца** таблицы, а не с суперпользователя.

Замер на стенде курса (`pgvector/pgvector:pg16`, схема §3.1 и политика выше — дословно, корпус с грифами 0 и 2 из §3.2): под `app_user` с `app.clearance=0` выдача содержит только чанки грифа 0 — грифованные документы отфильтрованы; с `app.clearance=2` возвращаются обе группы, то есть легитимную выдачу фильтр не съел. Под `assistant` тот же запрос с `app.clearance=0` возвращает **обе** группы — фильтрации нет вообще, хотя политика создана, а `ENABLE` и `FORCE` выставлены. Повтори этот контраст у себя: он и есть доказательство, что политика применяется, а не украшает схему. Отсюда два обязательных шага:

- **приложение подключается под `app_user`** — в обоих Java-скелетах `spring.datasource.username: app_user` и `password: ${APP_DB_PASSWORD}` (конфиг — как в §3.3); переменная уже лежит в `.env` стенда с М0 (§0.2), заводить её заново не нужно;
- **`assistant` остаётся владельцем схемы и миграций** — под ним же идёт ingest §3.2 (загрузчику нужен INSERT); боевой ретрив под ним не ходит никогда.

**Зачем тогда `FORCE`, если `app_user` — не владелец.** Затем, что он страхует другой случай, и границу его действия надо знать до прода, а не после инцидента. Замер на том же стенде, три роли против двух состояний флага:

| Под какой ролью ходит приложение | `FORCE` выкл. | `FORCE` вкл. |
|---|---|---|
| `app_user` — ни владелец, ни суперпользователь | фильтрует | фильтрует |
| владелец таблицы (не суперпользователь) | **не фильтрует** | фильтрует |
| суперпользователь (`assistant`) | **не фильтрует** | **не фильтрует** |

Читается по строкам: `app_user` фильтруется в любом случае — ему флаг не нужен; владельцу таблицы политика без `FORCE` не применяется вовсе, и вот ему флаг жизненно нужен; суперпользователя не удерживает ничто. Отсюда правило: `FORCE` держи включённым — «приложение ходит под владельцем схемы» это самая частая прод-конфигурация, и там он и есть та разница между работающей политикой и декорацией; но подменить им правильную роль нельзя. От суперпользователя не спасает ни один флаг — только не подключаться под ним.

Запомни класс отказа, а не только этот случай: контроль доступа, который *выглядит* настроенным, отказывает бесшумно и в сторону **открытия** доступа. Ровно поэтому §8.7 книги ставит инвариантом контроль доступа **на ретриве, а не на генерации**, и хвалит RLS именно за то, что доступ форсится в БД, а не в коде приложения (которое можно забыть). Первый тест ниже проверяет поэтому не политику, а то, что политика вообще применяется.

Java-сторона: уровень допуска берётся из Keycloak-токена (клейм роли из realm `assistant`, М0) и выставляется **в той же транзакции**, что и запрос:

```java
// jdbc — на DataSource из §3.3, то есть под app_user. Под assistant этот set_config отработает
// без ошибки и не ограничит ничего: суперпользователь пройдёт мимо политики (см. таблицу выше).
// SET LOCAL не принимает bind-параметров (синтаксис Postgres) — используем функцию set_config:
jdbc.queryForObject("SELECT set_config('app.clearance', ?, true)",   // true = до конца транзакции (эффект SET LOCAL)
                    String.class, String.valueOf(clearanceFromJwt));
```

Обязательные тесты (в CI, останутся до капстоуна):
1. **предохранитель:** из соединения приложения `SELECT rolsuper OR rolbypassrls FROM pg_roles WHERE rolname = current_user` обязан вернуть `false`. Без него два теста ниже зеленеют по ложной причине — они не отличают «политика отработала» от «политику никто не применял»;
2. пользователь с `clearance=0` не получает чанк документа с грифом 2 — ни прямым вопросом, ни просьбой «процитируй все регламенты»;
3. recall на золотом наборе с включённым RLS для высокопривилегированного пользователя не упал (фильтр не съел легитимную выдачу, §8.6).

## 3.8 Удаление и tombstone

Сценарий «право на удаление» (§8.3 + §25.4 книги):

```sql
-- LIKE, а не точное равенство: загрузчик §3.2 кладёт в path результат glob("../corpus/*.md"),
-- то есть '../corpus/vozvrat-nq.md' — с префиксом. Точное сравнение даст DELETE 0, и все три
-- наблюдения ниже повиснут на пустой операции.
DELETE FROM documents WHERE path LIKE '%vozvrat-nq.md';   -- каскадом уйдут чанки
```

Затем три наблюдения: (1) запрос из золотого набора, попадавший в этот документ, его больше не возвращает; (2) `SELECT pg_relation_size('chunks_embedding_hnsw');` — размер индекса **не уменьшился**: в HNSW-графе остались вершины-надгробия (tombstone); (3) после `REINDEX INDEX chunks_embedding_hnsw;` размер упал, а latency-выброс на время перестройки — увидь его в замере. Вывод в мини-ADR: как часто перестраивать индекс при твоём темпе удалений.

## 3.9 Итоговая таблица и мини-ADR

Шаблон таблицы (все числа — с одного золотого набора):

| Ступень | hit@5 | faithfulness | answer rel. | p50, мс | p99, мс | Стоимость/запрос |
|---|---|---|---|---|---|---|
| Naive (baseline) | | | | | | |
| + Hybrid RRF | | | | | | |
| + Reranker | | | | | | |

Мини-ADR «на какой ступени остановился» — по формату §26.3: контекст (числа из таблицы) → решение → последствия → **отклонённые альтернативы** (остальные ступени лестницы и почему их прирост не окупает цену). Четвёртый элемент здесь не формальность: «на какой ступени остановился» — это и есть решение об отклонении остальных ступеней, и без него ADR фиксирует не выбор, а факт. Почти все примеры §26.4 книги показывают этот блок — 10 ADR из 12; без него идут только ADR-10 (наблюдаемость) и ADR-11 (стоимость и латентность), оба обрываются на «Следствиях». Сверься с любым из остальных десяти. Каноническая ловушка, которую ADR должен явно закрыть: улучшение на 2–3 п.п. при наборе в 50 вопросов — это шум (§17.7 книги; формулу размера выборки применишь в М6, здесь достаточно честной оговорки).

## 3.10 Чек-лист DoD

- [ ] Таблица §3.9 заполнена по трём ступеням, каждая строка — с того же золотого набора.
- [ ] 5–7 «вопросов без ответа» — доля честных отказов замерена (naive обычно галлюцинирует хотя бы на части — зафиксируй).
- [ ] RLS-тесты (все три из §3.7) зелёные в CI — включая предохранитель «приложение подключено НЕ суперпользователем»: без него остальные два ничего не доказывают.
- [ ] Tombstone-наблюдение записано числами (размер индекса до/после REINDEX).
- [ ] Мини-ADR написан и читается без устных комментариев.
- [ ] Конвейер собран в `RetrievalService` (§3.6) — точка переиспользования для М4/М5.
