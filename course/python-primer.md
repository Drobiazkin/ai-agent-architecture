<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Python for the Java Developer: The Course Primer

*Reads in 1–2 evenings in Module 0, and serves as a reference from there on. The format: every construct through a contrast with Java. Only what you will actually meet in the course's code (M1, M3, M6, M7); for the full language there is the official tutorial at docs.python.org/3/tutorial (that one is the "book from the internet," and you need nothing better). Every example runs: `uv run python name.py`.*

## 1. The execution model: a script instead of a class

```python
# hello.py—this is a WHOLE program. No class, no main, no ";"
print("hello, world")

def main():
    print("and this one is a Java-style entry point")

if __name__ == "__main__":   # true only when the file is RUN, not imported
    main()
```

Contrasts with Java:
- **A file executes top to bottom** both when launched *and* when imported—which is why executable code hides under `if __name__ == "__main__":` (the analog of `public static void main`, but by convention rather than by signature).
- **Blocks come from indentation, not braces.** Four spaces = `{}`. A colon at the end of a line (`if x:`, `def f():`) opens a block. Mixing tabs and spaces is a syntax error.
- No semicolons; a line break ends the statement.

## 2. Variables, types, strings

```python
name = "Anna"          # no type is declared: a VARIABLE has no type, a VALUE does
count = 3              # int (arbitrary precision—no long/BigInteger needed)
price = 19.99          # float (this is a double; the language has no 32-bit float)
active = True          # bool: True/False, capitalized
nothing = None         # null

greeting = f"Hello, {name}! Tickets: {count + 1}"     # f-string ≈ String.format/template
ratio = f"{2/3:.2f} and {0.873:.0%}"                  # the format follows the colon: .2f—two decimals ("0.67"),
                                                      # .0%—percent with no fractional part ("87%")
multiline = """A string
spanning several lines"""                             # ≈ the text block """...""" from Java 15
```

- **Type hints** (`name: str`, `def f(x: int) -> str:`) are like generics without a compiler check: the IDE and `mypy` read them, the interpreter ignores them. The course's code has them everywhere—read them as signatures.
- **Truthiness:** in a condition, "false" covers not only `False` but also `0`, `""`, `[]`, `{}`, `None`. The idiom `if not chunks:` means "if the list is empty." A null check is `if x is None:` (not `==`).
- Comparing strings is plain `==` (that is `equals`, not a reference comparison).

## 3. Collections: four literals instead of Collections

```python
steps  = ["retrieve", "rerank", "generate"]     # list  ≈ ArrayList—mutable, mixed types allowed
config = {"model": "qwen3:4b", "temp": 0.0}     # dict  ≈ LinkedHashMap (insertion order is preserved)
point  = (52.5, 13.4)                            # tuple ≈ an immutable list; no analog in Java, closest is a record without names
tags   = {"rag", "eval"}                         # set   ≈ HashSet

steps[0]            # "retrieve";  steps[-1] is the LAST element (negative indices count from the end)
steps[0:2]          # a slice: ["retrieve", "rerank"]—from 0 inclusive to 2 EXCLUSIVE
config["model"]     # a read; KeyError if the key is absent
config.get("top_k", 5)   # ≈ getOrDefault
lat, lon = point    # unpacking: two variables out of a tuple at once
len(steps)          # the length of ANY collection—the function len(), not a .size() method
"rag" in tags       # a membership test—the in operator (works for list, dict, and str too)
```

**The comprehension is the main idiomatic break with Java.** It is the analog of a stream pipeline, built into the syntax:

```python
lengths = [len(s) for s in steps]                     # ≈ steps.stream().map(String::length).toList()
long_ones = [s for s in steps if len(s) > 6]          # ≈ .filter(...).toList()
by_name = {s: len(s) for s in steps}                  # ≈ Collectors.toMap(s -> s, String::length)
total = sum(len(s) for s in steps)                    # a generator without a list ≈ .mapToInt(...).sum()
```

Read it from the inside out: "for every `s` in `steps` [if the condition holds] take the expression on the left."

**`Counter` is a counter, not a fifth literal.** It has no syntax of its own; it comes from the standard library (M6, §6.8):

```python
from collections import Counter

found    = Counter(["PERSON", "PHONE_NUMBER", "PERSON"])   # filled in ONE pass
expected = Counter(["PERSON", "PERSON", "LOCATION"])
found["PERSON"]                     # 2
found["EMAIL"]                      # 0—not a KeyError: an absent key counts zero
found & expected                    # Counter({'PERSON': 2})—the element-wise MINIMUM
sum((found & expected).values())    # 2—add up the multiplicities
```

- By role it is a `Map<String, Integer>` filled in a single pass (≈ `Collectors.groupingBy(f, counting())`). It is a subclass of `dict`, so everything in §3 applies to it—with one exception: an absent key returns `0` instead of throwing `KeyError`.
- **`&` here does not mean what it means on a `set`.** On sets `&` is intersection, and multiplicity is lost there even earlier: `{"PERSON", "PERSON"}` is a single element to begin with. On counters `&` is the element-wise minimum: expected two `PERSON`, found one → one counts. Same operator, different arithmetic; in M6 §6.8 the correctness of recall rests on that difference.

## 4. Control flow

```python
for s in steps:                  # for-each only; there is no indexed for(;;)
    print(s)

for i, s in enumerate(steps):    # need the index → enumerate yields (i, element) pairs
    print(i, s)

for q, a in zip(questions, answers):   # walking two lists in parallel
    ...

for i in range(5):               # 0..4—the replacement for the classic for(int i=0;i<5;i++)
    ...

for k, v in config.items():      # iterating a dict ≈ entrySet()
    ...
```

`while` is as in Java. There is no `switch`; its role is played by `if/elif/else` and (since 3.10) `match/case`. The ternary is spelled out in words: `x = a if cond else b`.

## 5. Functions are first-class objects

```python
def hit_rate(golden: list[dict], k: int = 5, *, verbose: bool = False) -> float:
    """The docstring—this is the Javadoc, and it lives UNDER the signature."""
    ...
    return hits / len(golden)

hit_rate(golden)                      # k and verbose take their defaults
hit_rate(golden, k=10, verbose=True)  # keyword arguments; the * in the signature demands names after it
```

- Default values replace method overloading—Python has no overloads.
- A function is a value: you can put it in a variable, pass it, and return it (no functional interface required). `lambda x: -x[1]` ≈ `x -> -x[1]`—one expression, no block.
- `sorted(items, key=lambda p: -p[1])` sorts "by key": the function pulls out of an element the thing to sort on (≈ `Comparator.comparing`).

## 6. Classes: shorter than you're used to

```python
from dataclasses import dataclass

@dataclass                      # ≈ a Java record, but mutable: generates __init__, __repr__, __eq__
class Chunk:
    doc_id: int
    content: str
    score: float = 0.0

class Retriever:
    def __init__(self, top_k: int):     # the constructor
        self.top_k = top_k              # fields are NOT declared up front—assignment creates them

    def search(self, query: str) -> list[Chunk]:   # self = this, but always an EXPLICIT first parameter
        ...

class CachedRetriever(Retriever):        # inheritance: the base class in parentheses instead of extends
    def __init__(self, top_k: int, ttl: int):
        super().__init__(top_k)          # MANDATORY and explicit—see below
        self.ttl = ttl

    def search(self, query: str) -> list[Chunk]:   # an override is just a matching name
        ...
```

- **Inheritance** puts the base class in parentheses after the name: `class Sub(Base):` ≈ `extends Base`. The main trap for a Java developer: `super().__init__(...)` is called **explicitly and always**, if the base class has an `__init__` of its own. In Java the compiler inserts a no-argument `super()` at the top of the constructor; in Python nobody inserts anything—forget the line and the base class's initialization simply never ran. The constructor finishes without an error, at that: the object is left without the base class's fields, and the crash arrives later and elsewhere—`AttributeError: 'Sub' object has no attribute 'top_k'` on the very first access to a field that `Base.__init__` was supposed to create. In `nn.Module` layers (M1, §1.3) that same call sets up the internal registries where `nn.Module` stashes the layer's parameters when you write `self.Wq = nn.Linear(...)`—without it the layer does not work. Don't go looking for a delayed failure there, though: PyTorch, unlike plain Python, guards this case and blows up right on the assignment line—`AttributeError: cannot assign module before Module.__init__() call` (for `nn.Parameter`, "cannot assign parameters before…"). It guards only layers and parameters: an ordinary field (`self.n_heads = n_heads`) is assigned silently. The quiet delayed failure is about your own classes, where there is no such safety net.
- An override is a matching method name, and that is all: no `@Override` (nobody will catch a typo in the name), no `final`, every method "virtual" by default.
- There are no access modifiers: privacy is a convention (`_field` means "don't touch," like package-private on the honor system).
- Interfaces are unnecessary in 90% of the code: **duck typing**—any object with a `search()` method will do. When the contract has to be explicit, there is `typing.Protocol` (a structural interface) or `abc.ABC`.
- Nobody writes getters and setters: the field is public, and should the need arise it gets wrapped in `@property` later without changing the calling code.

## 7. Exceptions: all unchecked

```python
try:
    r = httpx.post(url, json=payload, timeout=30)
    r.raise_for_status()             # an HTTP error → an exception (otherwise the status is silently ignored!)
except httpx.TimeoutException:
    ...                              # the specific type comes first
except Exception as e:               # ≈ catch (Exception e)
    log.warning("fallback: %s", e)
    raise                            # rethrow as is (a bare raise ≈ throw e)
finally:
    ...
```

There are no checked exceptions—signatures carry no `throws`, and what a function throws is visible only from the documentation and the code. Your own exception: `class RetrievalError(Exception): pass`, thrown with `raise RetrievalError("...")`.

## 8. `with`—try-with-resources

```python
with psycopg.connect(dsn) as conn:          # ≈ try (var conn = ...) { ... }—closes on any outcome
    with open("golden.yaml") as f:          # files, connections, transactions—all through with
        data = f.read()
```

That is exactly why `ingest.py` from module-3 has not a single `close()`—`with` does them.

## 9. Modules, imports, uv

```python
import re                       # the whole module → re.split(...)
import numpy as np              # the canonical aliases: np, pd, torch—get used to them, everyone writes them
from pathlib import Path        # a specific name out of a module
from .chunking import chunk     # a relative import inside your own package
```

- **A module is a file**, **a package is a directory** (with an `__init__.py` for your own packages). No "one public class = one file" requirement.
- `uv add httpx` ≈ adding a dependency to the pom; `uv run python x.py` / `uv run pytest` run inside the project's environment; `pyproject.toml` ≈ `pom.xml`; the `.venv/` directory ≈ the local repository of dependencies (it stays out of git).

## 10. Decorators: annotations that actually do something

```python
@app.post("/rerank")            # FastAPI: registers the function as an HTTP handler
def rerank(r: Req): ...

@pytest.fixture                 # pytest: the function becomes an injectable dependency
def golden(): ...
```

Syntactically it resembles `@Annotation`, but the semantics differ: a decorator is **a function that wraps a function** (`f = app.post("/rerank")(f)`), and the behavior is added at definition time, with no reflection and no proxies. For this course it is enough to be able to *read* them.

## 11. pytest: JUnit without the ceremony

```python
# test_chunking.py—files named test_*.py and functions named test_* find themselves
def test_chunk_respects_max_len():
    pieces = chunk("# A\n" + "word " * 1000, max_chars=1200)
    assert all(len(p) <= 1200 for p in pieces)      # the bare assert is your assertEquals
    assert len(pieces) > 1

def test_embedding_dim():
    assert len(embed(["test"])[0]) == 1024
```

`assert expression, "message"` replaces the whole `assertThat` menagerie: on a failure pytest shows the values of the subexpressions itself. To run: `uv run pytest -q`.

## 12. Generators and yield (generator expressions—in M1)

```python
def batches(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]        # the function "hands over" an element and freezes until the next request

for b in batches(chunks, 32): ...      # ≈ a lazy Stream/Iterator, but written like ordinary code
```

Functions with `yield` do not appear in the modules' code—this section is here for the idiom that does: the **generator expression** (`sum(p.numel() for p in ...)` in M1, §1.4) is the same lazy source of elements, only written as a comprehension without the square brackets (§3): the values are computed one at a time as the iteration proceeds, and no list is assembled in memory.

## 13. The course's libraries—what each one is

| Library | Java counterpart by role | Where in the course |
|---|---|---|
| `httpx` | HttpClient/RestTemplate | M3 ingest; the Ollama calls—M1, M6 |
| `psycopg` | the Postgres JDBC driver | M3 |
| `pydantic` (`BaseModel`) | Jackson + Bean Validation: the class is the schema, parsing is validation | M3 FastAPI (the reranker) |
| `FastAPI` | Spring MVC in miniature: decorators instead of `@RequestMapping`, pydantic instead of DTOs | M3 reranker |
| `pytest` | JUnit | everywhere |
| `presidio-analyzer` | no counterpart of its own: finds personal data in text (phone numbers, cards, names) with rules plus an NER model | M6 (the PII containment loop) |
| `torch` | no counterpart of its own: arrays + autograd on the GPU | M1, M7 |
| `datasets`, `transformers`, `peft` | the HF stack: an ecosystem of models ≈ Maven Central for weights | M7 |

## 14. How to use this

1. **Evening 1 (M0):** sections 1–5 plus running every example by hand (`uv run python ...`). Write your first script: read every file in `corpus/*.md` and print the name and the character count of each—that is sections 3, 4, and 9 assembled.
2. **Evening 2 (before M1):** sections 6–12. Write a `test_*.py` for the function from evening 1.
3. After that, as you go: every Python snippet in the modules comes with a "Syntax walkthrough" block that links back here (`§N` of the primer). An unfamiliar construct with no such marker is a signal to write it in here yourself—the primer is your own notes, not dogma.

References for when the primer is not enough: the official tutorial (docs.python.org/3/tutorial)—chapters 3–9 cover everything above; for PyTorch you need no separate book—Raschka (M1) teaches at exactly the course's pace.
