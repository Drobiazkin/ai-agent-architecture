<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Python для Java-разработчика: праймер курса

*Читается за 1–2 вечера в Модуле 0, дальше используется как справочник. Формат: каждая конструкция — через контраст с Java. Здесь только то, что реально встретится в коде курса (М1, М3, М6, М7); полный язык — в официальном туториале docs.python.org/3/tutorial (он и есть «книга из интернета», лучше не нужно). Все примеры запускаются: `uv run python имя.py`.*

## 1. Модель исполнения: скрипт вместо класса

```python
# hello.py — это ЦЕЛАЯ программа. Нет класса, нет main, нет ";"
print("hello, world")

def main():
    print("а это — по-джавовски организованный вход")

if __name__ == "__main__":   # истинно, только когда файл ЗАПУЩЕН, а не импортирован
    main()
```

Контрасты с Java:
- **Файл исполняется сверху вниз** при запуске *и* при импорте — поэтому исполняемый код прячут под `if __name__ == "__main__":` (аналог `public static void main`, но по соглашению, а не по сигнатуре).
- **Блоки — отступами, не скобками.** Четыре пробела = `{}`. Двоеточие в конце строки (`if x:`, `def f():`) открывает блок. Смешение табов и пробелов — синтаксическая ошибка.
- Точка с запятой не нужна; перенос строки = конец инструкции.

## 2. Переменные, типы, строки

```python
name = "Анна"          # тип не объявляется: у ПЕРЕМЕННОЙ типа нет, тип есть у ЗНАЧЕНИЯ
count = 3              # int (произвольной длины — long/BigInteger не нужны)
price = 19.99          # float (это double; 32-битного float в языке нет)
active = True          # bool: True/False с большой буквы
nothing = None         # null

greeting = f"Привет, {name}! Заявок: {count + 1}"   # f-строка ≈ String.format/шаблон
ratio = f"{2/3:.2f} и {0.873:.0%}"                   # формат — после двоеточия: .2f — два знака ("0.67"),
                                                     # .0% — проценты без дробной части ("87%")
multiline = """Строка
на несколько строк"""                                # ≈ text block """...""" из Java 15
```

- **Типы-подсказки** (`name: str`, `def f(x: int) -> str:`) — как дженерики без проверки компилятором: их читают IDE и `mypy`, интерпретатор игнорирует. В коде курса они везде — читайте их как сигнатуры.
- **Truthiness:** в условии «ложны» не только `False`, но и `0`, `""`, `[]`, `{}`, `None`. Идиома `if not chunks:` означает «если список пуст». Проверка на null — `if x is None:` (не `==`).
- Сравнение строк — просто `==` (это `equals`, не сравнение ссылок).

## 3. Коллекции: четыре литерала вместо Collections

```python
steps  = ["retrieve", "rerank", "generate"]     # list  ≈ ArrayList — изменяемый, разнотипность допустима
config = {"model": "qwen3:4b", "temp": 0.0}     # dict  ≈ LinkedHashMap (порядок вставки сохраняется)
point  = (52.5, 13.4)                            # tuple ≈ неизменяемый список; в Java аналога нет, ближе record без имён
tags   = {"rag", "eval"}                         # set   ≈ HashSet

steps[0]            # "retrieve";  steps[-1] — ПОСЛЕДНИЙ элемент (отрицательные индексы — с конца)
steps[0:2]          # срез: ["retrieve", "rerank"] — от 0 включительно до 2 НЕ включительно
config["model"]     # чтение; KeyError, если ключа нет
config.get("top_k", 5)   # ≈ getOrDefault
lat, lon = point    # распаковка: две переменные из кортежа за раз
len(steps)          # длина ЛЮБОЙ коллекции — функция len(), не метод .size()
"rag" in tags       # проверка принадлежности — оператор in (работает и для list, dict, str)
```

**Comprehension — главный идиоматический разрыв с Java.** Это встроенный в синтаксис аналог stream-конвейера:

```python
lengths = [len(s) for s in steps]                     # ≈ steps.stream().map(String::length).toList()
long_ones = [s for s in steps if len(s) > 6]          # ≈ .filter(...).toList()
by_name = {s: len(s) for s in steps}                  # ≈ Collectors.toMap(s -> s, String::length)
total = sum(len(s) for s in steps)                    # генератор без списка ≈ .mapToInt(...).sum()
```

Читается изнутри наружу: «для каждого `s` из `steps` [если условие] возьми выражение слева».

**`Counter` — счётчик, а не пятый литерал.** Своего синтаксиса у него нет, берётся из стандартной библиотеки (М6, §6.8):

```python
from collections import Counter

found    = Counter(["PERSON", "PHONE_NUMBER", "PERSON"])   # наполняется за ОДИН проход
expected = Counter(["PERSON", "PERSON", "LOCATION"])
found["PERSON"]                     # 2
found["EMAIL"]                      # 0 — не KeyError: у отсутствующего ключа счёт ноль
found & expected                    # Counter({'PERSON': 2}) — поэлементный МИНИМУМ
sum((found & expected).values())    # 2 — сложить кратности
```

- По роли — `Map<String, Integer>`, набитая за один проход (≈ `Collectors.groupingBy(f, counting())`). Это подкласс `dict`, поэтому всё из §3 к нему применимо — кроме одного: отсутствующий ключ возвращает `0`, а не бросает `KeyError`.
- **`&` значит здесь не то, что на `set`.** На множествах `&` — пересечение, и кратность в нём теряется ещё раньше: `{"PERSON", "PERSON"}` — это вообще один элемент. На счётчиках `&` — поэлементный минимум: ожидали два `PERSON`, нашли один → в зачёт идёт один. Оператор один, арифметика разная; в М6 §6.8 на этой разнице стоит корректность recall.

## 4. Управление потоком

```python
for s in steps:                  # только for-each; индексного for(;;) нет
    print(s)

for i, s in enumerate(steps):    # нужен индекс → enumerate даёт пары (i, элемент)
    print(i, s)

for q, a in zip(questions, answers):   # параллельный обход двух списков
    ...

for i in range(5):               # 0..4 — замена классическому for(int i=0;i<5;i++)
    ...

for k, v in config.items():      # обход словаря ≈ entrySet()
    ...
```

`while` — как в Java. `switch` нет; его роль играют `if/elif/else` и (с 3.10) `match/case`. Тернарник пишется словами: `x = a if cond else b`.

## 5. Функции — объекты первого класса

```python
def hit_rate(golden: list[dict], k: int = 5, *, verbose: bool = False) -> float:
    """Docstring — это Javadoc, живёт ПОД сигнатурой."""
    ...
    return hits / len(golden)

hit_rate(golden)                      # k и verbose — по умолчанию
hit_rate(golden, k=10, verbose=True)  # именованные аргументы; * в сигнатуре требует имён после него
```

- Значения по умолчанию заменяют перегрузку методов — перегрузки в Python нет.
- Функция — значение: её можно класть в переменную, передавать и возвращать (никаких functional interface не нужно). `lambda x: -x[1]` ≈ `x -> -x[1]` — одно выражение, без блока.
- `sorted(items, key=lambda p: -p[1])` — сортировка «по ключу»: функция извлекает из элемента то, по чему сортировать (≈ `Comparator.comparing`).

## 6. Классы: короче, чем вы привыкли

```python
from dataclasses import dataclass

@dataclass                      # ≈ record из Java, но изменяемый: генерирует __init__, __repr__, __eq__
class Chunk:
    doc_id: int
    content: str
    score: float = 0.0

class Retriever:
    def __init__(self, top_k: int):     # конструктор
        self.top_k = top_k              # поля НЕ объявляются заранее — создаются присваиванием

    def search(self, query: str) -> list[Chunk]:   # self = this, но всегда ЯВНЫЙ первый параметр
        ...

class CachedRetriever(Retriever):        # наследование: базовый класс в скобках вместо extends
    def __init__(self, top_k: int, ttl: int):
        super().__init__(top_k)          # ОБЯЗАТЕЛЕН явно — см. ниже
        self.ttl = ttl

    def search(self, query: str) -> list[Chunk]:   # переопределение — просто совпадение имени
        ...
```

- **Наследование** — базовый класс в скобках после имени: `class Sub(Base):` ≈ `extends Base`. Главная ловушка для джависта: `super().__init__(...)` вызывается **явно и всегда**, если у базового класса есть свой `__init__`. В Java безаргументный `super()` в начало конструктора вставляет компилятор; в Python не вставляет никто — забыли строку, и инициализация базового класса просто не выполнилась. Конструктор при этом отработает без ошибки: объект останется без полей базового класса, а падение придёт позже и не там — `AttributeError: 'Sub' object has no attribute 'top_k'` на первом же обращении к полю, которое должен был завести `Base.__init__`. В `nn.Module`-слоях (М1, §1.3) тот же вызов заводит внутренние реестры, куда `nn.Module` складывает параметры слоя при `self.Wq = nn.Linear(...)`, — без него слой не работает. Но отложенного сбоя там не ищите: PyTorch, в отличие от чистого Python, этот случай стережёт и роняет сразу на самой строке присваивания — `AttributeError: cannot assign module before Module.__init__() call` (для `nn.Parameter` — «cannot assign parameters before…»). Стережёт он только слои и параметры: обычное поле (`self.n_heads = n_heads`) присвоится молча. Тихий отложенный сбой — это про ваши собственные классы, где такой страховки нет.
- Переопределение — совпадение имени метода, и всё: `@Override` нет (опечатку в имени никто не поймает), `final` нет, все методы «виртуальные» по умолчанию.
- Модификаторов доступа нет: приватность — соглашением (`_поле` — «не трогайте», как package-private на честном слове).
- Интерфейсы не нужны в 90% кода: **duck typing** — подойдёт любой объект с методом `search()`. Когда контракт нужен явно — `typing.Protocol` (структурный интерфейс) или `abc.ABC`.
- Геттеры/сеттеры не пишут: поле — публичное, при необходимости позже оборачивается `@property` без изменения вызывающего кода.

## 7. Исключения: все — unchecked

```python
try:
    r = httpx.post(url, json=payload, timeout=30)
    r.raise_for_status()             # HTTP-ошибка → исключение (иначе статус молча игнорируется!)
except httpx.TimeoutException:
    ...                              # конкретный тип — первым
except Exception as e:               # ≈ catch (Exception e)
    log.warning("fallback: %s", e)
    raise                            # перебросить как есть (raise без аргумента ≈ throw e)
finally:
    ...
```

Checked-исключений нет — `throws` в сигнатурах отсутствует, что бросает функция, видно только из документации и кода. Своё исключение: `class RetrievalError(Exception): pass`, бросается `raise RetrievalError("...")`.

## 8. `with` — try-with-resources

```python
with psycopg.connect(dsn) as conn:          # ≈ try (var conn = ...) { ... } — закроется при любом исходе
    with open("golden.yaml") as f:          # файлы, соединения, транзакции — всё через with
        data = f.read()
```

Именно поэтому в `ingest.py` из module-3 нет ни одного `close()` — их делает `with`.

## 9. Модули, импорты, uv

```python
import re                       # модуль целиком → re.split(...)
import numpy as np              # каноничные алиасы: np, pd, torch — привыкайте, их пишут все
from pathlib import Path        # конкретное имя из модуля
from .chunking import chunk     # относительный импорт внутри своего пакета
```

- **Модуль = файл**, **пакет = каталог** (для своих пакетов — с `__init__.py`). Никакого требования «один публичный класс = один файл».
- `uv add httpx` ≈ добавить dependency в pom; `uv run python x.py` / `uv run pytest` — запуск в окружении проекта; `pyproject.toml` ≈ `pom.xml`; каталог `.venv/` ≈ локальный репозиторий зависимостей (в git не попадает).

## 10. Декораторы: аннотации, которые работают

```python
@app.post("/rerank")            # FastAPI: регистрирует функцию как HTTP-обработчик
def rerank(r: Req): ...

@pytest.fixture                 # pytest: функция становится инъектируемой зависимостью
def golden(): ...
```

Синтаксически похоже на `@Annotation`, но семантика другая: декоратор — это **функция, оборачивающая функцию** (`f = app.post("/rerank")(f)`), поведение добавляется в момент определения, без reflection и прокси. Для курса достаточно уметь их *читать*.

## 11. pytest: JUnit без церемоний

```python
# test_chunking.py — файлы test_*.py, функции test_* находятся сами
def test_chunk_respects_max_len():
    pieces = chunk("# A\n" + "слово " * 1000, max_chars=1200)
    assert all(len(p) <= 1200 for p in pieces)      # голый assert — это и есть assertEquals
    assert len(pieces) > 1

def test_embedding_dim():
    assert len(embed(["тест"])[0]) == 1024
```

`assert выражение, "сообщение"` заменяет весь зоопарк `assertThat`: pytest при падении сам показывает значения подвыражений. Запуск: `uv run pytest -q`.

## 12. Генераторы и yield (генераторные выражения — в М1)

```python
def batches(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]        # функция «отдаёт» элемент и замирает до следующего запроса

for b in batches(chunks, 32): ...      # ≈ ленивый Stream/Iterator, но пишется как обычный код
```

Функции с `yield` в коде модулей не встречаются — раздел здесь ради идиомы, которая встречается: **генераторное выражение** (`sum(p.numel() for p in ...)` в М1, §1.4) — тот же ленивый источник элементов, только записанный как comprehension без квадратных скобок (§3): значения считаются по одному по мере обхода, список в памяти не собирается.

## 13. Библиотеки курса — что чем является

| Библиотека | Java-аналог по роли | Где в курсе |
|---|---|---|
| `httpx` | HttpClient/RestTemplate | М3 ingest; вызовы Ollama — М1, М6 |
| `psycopg` | JDBC-драйвер Postgres | М3 |
| `pydantic` (`BaseModel`) | Jackson + Bean Validation: класс = схема, парсинг = валидация | М3 FastAPI (реранкер) |
| `FastAPI` | Spring MVC в миниатюре: декораторы вместо `@RequestMapping`, pydantic вместо DTO | М3 реранкер |
| `pytest` | JUnit | везде |
| `presidio-analyzer` | своего аналога нет: ищет в тексте персональные данные (телефоны, карты, имена) — правилами плюс NER-моделью | М6 (PII-контур) |
| `torch` | своего аналога нет: массивы+автоград на GPU | М1 |
| `datasets`, `peft`, `trl` | HF-стек: экосистема моделей ≈ Maven Central для весов | М7 (`datasets` — ещё и М3, под RAGAS) |

## 14. Как этим пользоваться

1. **Вечер 1 (М0):** разделы 1–5 + запустить каждый пример руками (`uv run python ...`). Написать свой первый скрипт: прочитать все файлы `corpus/*.md`, вывести имя и число символов каждого — это разделы 3, 4, 9 в сборе.
2. **Вечер 2 (перед М1):** разделы 6–12. Написать `test_*.py` на функцию из вечера 1.
3. Дальше — по встрече: каждый Python-сниппет модулей снабжён блоком «Разбор синтаксиса» со ссылками сюда (`§N` праймера). Незнакомая конструкция без пометки — сигнал дописать её сюда же: праймер — ваш конспект, а не догма.

Справочники, когда праймера мало: официальный туториал (docs.python.org/3/tutorial) — главы 3–9 покрывают всё выше; по PyTorch отдельная книга не нужна — Raschka (М1) учит ровно в темпе курса.
