<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Модуль 0 — Стенд: детализация

*Спутник задания «Модуль 0» из `ai-agent-practice-course.md`. Здесь — команды, конфиги и скелеты; цели и DoD — в навигаторе.*

> **Правило скелетов.** Всё ниже — рабочие заготовки на момент редакции (июль 2026). Теги образов и версии зависимостей сверяй перед `pull`: у молодых инструментов минорные версии ломают API. Если команда упала — это первое задание курса: прочитай ошибку и почини стенд сам, это и есть цель Модуля 0.

## 0.1 Каталог проекта

Один репозиторий на весь курс — сквозной домен наращивается модулями, а не пересоздаётся:

```
support-assistant/
├── infra/
│   ├── docker-compose.yml      # Postgres+pgvector, Keycloak
│   └── initdb/                 # 01-extensions.sql, 02-app-user.sh
├── app-springai/               # скелет №1 (Java, Spring AI)
├── app-lc4j/                   # скелет №2 (Java, LangChain4j)
├── py/                         # Python-дорожка (М1, М3, М6, М7)
├── corpus/                     # 30–50 документов-регламентов
└── .env                        # ключи и пароли — В .gitignore С ПЕРВОГО КОММИТА
```

```bash
git init support-assistant && cd support-assistant
printf '.env\n*.iml\n.idea/\ntarget/\nbuild/\n__pycache__/\n.venv/\n' > .gitignore
git add .gitignore && git commit -m "стенд: каркас"
```

## 0.2 Инфраструктура: docker-compose

`infra/docker-compose.yml` — Postgres с pgvector и Keycloak. Langfuse ставится отдельно (ниже, §0.5): его официальный compose тянет собственные ClickHouse/Redis/MinIO, и вклеивать его сюда — воевать с чужими обновлениями.

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16        # Postgres 16 + расширение vector
    environment:
      POSTGRES_USER: assistant                 # ВЛАДЕЛЕЦ схемы. Образ делает эту роль суперпользователем — см. ниже
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: assistant
      APP_DB_PASSWORD: ${APP_DB_PASSWORD}      # пароль роли приложения; её заводит initdb/02-app-user.sh
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./initdb:/docker-entrypoint-initdb.d   # выполняется при ПЕРВОМ старте пустого тома
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U assistant"]
      interval: 5s
      retries: 10

  keycloak:
    image: quay.io/keycloak/keycloak:26.2      # сверь актуальный тег
    command: start-dev                          # dev-режим: http, без внешней БД
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

`infra/initdb/02-app-user.sh` — роль, под которой приложение обслуживает запросы (`chmod +x` обязателен; entrypoint исполняет `.sh` как скрипт, а `.sql` не умеет подставлять переменные окружения — потому пароль и приходит через shell):

```bash
#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
  CREATE ROLE app_user LOGIN PASSWORD '${APP_DB_PASSWORD}';
  GRANT USAGE ON SCHEMA public TO app_user;
SQL
```

**Зачем вторая роль — не бюрократия, а единственное, что заставит работать RLS из М3.** Образ Postgres делает роль из `POSTGRES_USER` (у нас `assistant`) суперпользователем, а суперпользователь обходит row-level security — построчную фильтрацию доступа средствами самой БД — безусловно: политика написана, но не применяется ни к одной строке. `FORCE ROW LEVEL SECURITY`, который М3 включает на таблице, эту дыру не закрывает — FORCE снимает исключение с *владельца* таблицы, но не с суперпользователя. Отказ идёт в сторону открытия доступа: защита выглядит настроенной и молча не делает ничего. Поэтому разделение с первого дня: `assistant` — владелец схемы, миграции и загрузка корпуса; `app_user` — то, чем приложение читает данные под пользователем. Права на таблицы `app_user` получит в М3 (§3.2) — сразу, как таблицы появятся и наполнятся, потому что уже §3.3 переводит приложение на эту роль. Дальше правило держится до конца курса: **каждая новая таблица выдаёт права `app_user` там же, где заводится** (М4 — `saga_steps`, `tickets`, `pending_actions`; М5 — журнал уведомлений). С М3 приложение не ходит ни под какой другой ролью, поэтому таблица без гранта для него просто не существует.

Запуск и проверка:

```bash
cd infra
printf 'POSTGRES_PASSWORD=dev-only-pass\nKEYCLOAK_ADMIN_PASSWORD=dev-only-admin\nAPP_DB_PASSWORD=dev-only-app\n' >> ../.env
docker compose --env-file ../.env up -d
docker compose ps                          # оба healthy/running
psql postgresql://assistant:dev-only-pass@localhost:5432/assistant \
  -c "SELECT extversion FROM pg_extension WHERE extname='vector';"   # версия ≥ 0.7
psql postgresql://assistant:dev-only-pass@localhost:5432/assistant \
  -c "SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname IN ('assistant','app_user');"
#  assistant | t | t   ← обходит RLS, приложению под ней ходить нельзя
#  app_user  | f | f   ← под ней приложение и будет ходить с М3
psql postgresql://app_user:dev-only-app@localhost:5432/assistant -c "SELECT current_user;"  # роль логинится
```

Если `app_user` в выдаче нет — значит том уже существовал, а `initdb` отрабатывает только на пустом: `docker compose --env-file ../.env down -v && docker compose --env-file ../.env up -d` (на М0 терять нечего). Тихо пропустить этот шаг нельзя — М3 упрётся в отсутствующую роль либо, что хуже, поедет под `assistant` без всякой фильтрации.

Keycloak: открой `http://localhost:8081`, войди админом, создай realm `assistant` — роли и клиенты понадобятся в М3 (RLS) и М5 (OAuth на MCP), сейчас достаточно пустого realm.

**Гочка macOS/Colima:** Keycloak и Postgres вместе просят ~2 ГБ; если контейнеры умирают по OOM — подними память Docker Desktop (Settings → Resources) до 4+ ГБ.

## 0.3 Локальные модели: Ollama

```bash
# macOS: brew install ollama && brew services start ollama
# Linux:  curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:4b        # «маленькая» — быстрые итерации, дешёвые прогоны
ollama pull qwen3:8b        # «средняя» — основная рабочая на курсе
ollama pull bge-m3          # эмбеддер для М3 (мультиязычный, 1024 измерения)
ollama run qwen3:4b "Ответь одним словом: работаешь?"
```

Ollama слушает `http://localhost:11434` и отдаёт два API: своё (`/api/generate`, `/api/embed`) и OpenAI-совместимое (`/v1/...`) — второе позволяет фреймворкам работать с локальной моделью «как с провайдером». Проверка без кода:

```bash
curl -s http://localhost:11434/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model": "qwen3:4b",
  "messages": [{"role": "user", "content": "ping"}]
}' | head -c 400
```

Выбор моделей — ориентир, не догма: смотри, что влезает в твою память. Прикидка курса (арифметика наша, в книге её нет): веса ≈ параметры × байт на параметр, а 4 бита — это 0.5 байта плюс константы квантизации, итого ≈ 0.5–0.6 байта на параметр. Книга даёт не эту арифметику, а сами форматы инференс-квантизации — AWQ/GPTQ, FP8, INT8 (§22.6), — и формулу размера KV-кэша, второго потребителя памяти после весов (§1.6). 8B в Q4 ≈ 5 ГБ — комфортно на 16 ГБ RAM.

## 0.4 Hosted-провайдер: ключ и лимит расходов

Порядок действий важнее провайдера:

1. Заведи ключ в консоли провайдера.
2. **Сначала лимит, потом первый вызов**: установи месячный hard limit (для курса достаточно $10–20/мес — на весь курс заложено $30–60) и алерт на 50%.
3. Ключ — только в `.env`: `LLM_API_KEY=...`; в конфигах — через `${LLM_API_KEY}`. Проверь, что `.env` в `.gitignore`, **до** того как положить туда ключ.

Правило курса №5 («тратить мало») исполняется маршрутизацией по умолчанию: всё, что может работать на Ollama, — работает на Ollama; hosted — там, где задание сравнивает качество или требует фронтир-возможностей.

## 0.5 Наблюдаемость: Langfuse self-host

Официальный способ (compose живёт в их репозитории и обновляется вместе с продуктом):

```bash
git clone https://github.com/langfuse/langfuse.git ~/langfuse
cd ~/langfuse
docker compose up -d          # поднимет веб + воркер + ClickHouse + Redis + MinIO + Postgres
```

Открой `http://localhost:3000`, заведи организацию/проект, сохрани в `.env` пару `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`. Подключение из кода — задание М2 (п. 5); в М0 достаточно живого UI.

**Гочка:** стек Langfuse v3 — самый тяжёлый кусок стенда (ещё ~2–3 ГБ). Если ресурсы поджимают — подними его только с М2, когда реально понадобится.

## 0.6 Java-скелет №1: Spring Boot + Spring AI

Генерация проекта (или то же самое мышкой на start.spring.io):

```bash
mkdir app-springai && cd app-springai          # архив Initializr плоский: pom/src лягут прямо сюда
curl -s https://start.spring.io/starter.tgz \
  -d type=maven-project -d javaVersion=21 -d bootVersion=3.5.0 \
  -d groupId=ru.course -d artifactId=app-springai -d dependencies=web \
  | tar -xzf -
cd ..
```

В `pom.xml` — BOM Spring AI и стартер Ollama (артефакты — по документации твоей версии; в 1.0 GA стартеры называются `spring-ai-starter-model-*`):

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.ai</groupId>
      <artifactId>spring-ai-bom</artifactId>
      <version>1.0.0</version>   <!-- сверь актуальную; от неё зависят М2/М5 задания -->
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

Смоук-тест — CommandLineRunner с `ChatClient` (центральная абстракция, на которой построены М2/М5):

```java
@SpringBootApplication
public class App {
    public static void main(String[] args) { SpringApplication.run(App.class, args); }

    @Bean
    CommandLineRunner hello(ChatClient.Builder builder) {
        return args -> System.out.println(
            builder.build().prompt().user("Скажи ровно одно слово: привет").call().content());
    }
}
```

`./mvnw spring-boot:run` → в консоли ответ модели.

**Hosted-провайдера подключи уже сейчас** — DoD М0 (§0.10) требует ответ «привет» и через hosted API: hosted-стартер рядом с ollama-стартером плюс отдельный профиль (три строки yml с `${LLM_API_KEY}` из §0.4), переключение — `--spring.profiles.active=hosted`. Рабочая модель курса остаётся Ollama; сравнение качества провайдеров — задание М2.

## 0.7 Java-скелет №2: LangChain4j

Второй пустой проект (`app-lc4j`, тот же start.spring.io без AI-зависимостей), в `pom.xml`:

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j</artifactId>
  <version>1.0.1</version>   <!-- сверь; API 0.x и 1.x несовместимы -->
</dependency>
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-ollama</artifactId>
  <version>1.0.1</version>
</dependency>
```

Смоук-тест (низкоуровневый API; AiServices с `@Tool` — материал М5):

```java
var model = OllamaChatModel.builder()
        .baseUrl("http://localhost:11434")
        .modelName("qwen3:4b")
        .temperature(0.0)
        .build();
System.out.println(model.chat("Скажи ровно одно слово: привет"));
```

Здесь тот же DoD-минимум, что и в §0.6: **hosted-провайдер подключается сейчас** — вторая зависимость (`langchain4j-open-ai` или модуль твоего провайдера) и второй builder модели рядом с `OllamaChatModel`, ключ — из `${LLM_API_KEY}`. Дефолт остаётся Ollama.

Зачем два скелета с первого дня: М5 сравнивает стили композиции (Advisors против AiServices) — сравнение честное, только если оба проекта живут на одном стенде с одними моделями.

## 0.8 Python-дорожка: uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # или brew install uv
mkdir py && cd py && uv init --python 3.12
uv add torch jupyter pytest
uv run python -c "import torch; print(torch.__version__, torch.backends.mps.is_available())"

mkdir tests
printf 'def test_torch_imports():\n    import torch\n\n    assert torch.__version__\n' > tests/test_smoke.py
uv run pytest    # 1 passed, код возврата 0 — вот это зелёный прогон
```

**Про пустой `pytest`.** Прогон без единого теста зелёным НЕ является: pytest печатает `no tests ran` и возвращает код **5** (`EXIT_NOTESTSCOLLECTED`), а не 0 — 0 означает «все тесты прошли», 1 — «были падения». `uv run` пробрасывает код как есть, поэтому для shell (`$?`) и для CI такой прогон красный. Отсюда и `tests/test_smoke.py` выше: DoD требует зелёный `pytest`, а зелёный он только с реальным тестом. Запомни цифру 5 — CI появится уже в М3 (RLS-тесты) и М6 (eval-гейт), и однажды пайплайн покраснеет именно так: тесты не собрались (не тот `rootdir`, не тот префикс имени файла), а выглядит это «как будто ничего не запускалось».

Словарь соответствий для Java-разработчика: `pyproject.toml` ≈ `pom.xml`, `uv add` ≈ добавить dependency, `uv run` ≈ `mvn exec`, `pytest` ≈ JUnit, type hints ≈ дженерики без проверки компилятором (проверяет `mypy`, подключишь по желанию).

**Сам язык — по праймеру `course/python-primer.md`** («Python для Java-разработчика»: каждая конструкция через контраст с Java). План там же, §14: вечер 1 — разделы 1–5 + первый скрипт по `corpus/` (hello world курса), вечер 2 — разделы 6–12 + первый `pytest`. Дальше каждый Python-сниппет модулей идёт с блоком «Разбор синтаксиса» со ссылками на праймер — отдельная книга по Python не нужна; справочник на вырост — официальный туториал docs.python.org.

## 0.9 Корпус сквозного домена

30–50 документов-регламентов службы поддержки в `corpus/` (markdown). Если реальных нет — синтезируй и **вычитай** (правило: сгенерированный документ без вычитки в корпус не попадает, иначе золотой набор М3 будет мерить качество ретрива по галлюцинациям):

```bash
ollama run qwen3:8b "Напиши внутренний регламент службы поддержки интернет-магазина:
«Возврат товара ненадлежащего качества». Структура: область действия, сроки,
пошаговая процедура оператора, исключения. 400-600 слов, деловой стиль." > corpus/vozvrat-nq.md
```

Разнообразь темы (возвраты, доставка, оплата, эскалация, персональные данные, гарантия…) — в М3 понадобятся и близкие по теме пары документов (проверка реранкера), и «вопросы без ответа в корпусе».

## 0.10 Чек-лист DoD

```bash
docker compose -f infra/docker-compose.yml ps               # postgres, keycloak: Up
psql ...  -c "SELECT extname FROM pg_extension;"            # vector на месте
psql ...  -c "SELECT rolname,rolsuper FROM pg_roles WHERE rolname='app_user';"   # есть, rolsuper=f — иначе RLS в М3 мёртв
curl -s localhost:11434/v1/models | head -c 200             # Ollama отвечает
(cd app-springai && ./mvnw -q spring-boot:run)              # «привет» от Ollama
(cd app-lc4j     && ./mvnw -q spring-boot:run)              # «привет» от Ollama
(cd py && uv run pytest; echo "exit=$?")                    # 1 passed, exit=0 (не 5!)
ls corpus | wc -l                                           # ≥ 30
```

Плюс два пункта без команд: лимит расходов у hosted-провайдера установлен (скриншот в журнал решений); `.env` не в git (`git check-ignore .env` возвращает путь). Оба скелета должны ответить «привет» и через hosted API (как того требует DoD навигатора) — это проверит ключ, лимиты и конфигурацию обоих фреймворков до того, как они понадобятся под давлением в М2 и М5.
