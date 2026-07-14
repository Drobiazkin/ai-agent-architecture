<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Модуль 1 — Субстрат руками: детализация

*Спутник «Модуля 1» из навигатора. Это самый Python-плотный модуль после М7 — держи открытым `python-primer.md`; каждый сниппет идёт с разбором синтаксиса. Работа — в Jupyter (`uv run jupyter lab`): ноутбук здесь — лабораторный журнал, ячейка = эксперимент.*

## 1.1 Тензорный словарь Прил. A — в ноутбуке

Цель — прогнать руками каждую операцию §A.3 книги и *увидеть формы*. Заготовка ячеек:

```python
import torch

x = torch.randn(1000, 4096)          # «вход блока»: seq × d_model, случайные числа ~N(0,1)
W = torch.randn(4096, 4096)          # весовая матрица проекции

y = x @ W                            # matmul; @ — оператор матричного умножения
print(x.shape, "@", W.shape, "->", y.shape)   # torch.Size([1000, 4096]) -> [1000, 4096]

# broadcast: прибавить вектор-строку к каждой строке таблицы
b = torch.randn(4096)
print((x + b).shape)                 # [1000, 4096] — b «растянулся» по строкам

# батчевый matmul: головы как батч-ось
h, d_head = 32, 128
Q = torch.randn(h, 1000, d_head)
K = torch.randn(h, 1000, d_head)
scores = Q @ K.transpose(-2, -1)     # transpose(-2,-1) — поменять ДВЕ ПОСЛЕДНИЕ оси = Kᵀ по головам
print(scores.shape)                  # [32, 1000, 1000] — вот она, seq² на голову (§1.4 книги)

# та же операция через einsum — сверь с чтением по буквам в §A.3
scores2 = torch.einsum("hqd,hkd->hqk", Q, K)
print(torch.allclose(scores, scores2))   # True — это ОДНА И ТА ЖЕ контракция
```

**Разбор синтаксиса** (→ разделы праймера): `import torch` — §9; `x.shape` — атрибут-кортеж формы, читается как `seq × d_model` из §1.4 книги; `@` — перегруженный оператор matmul (в Java перегрузки операторов нет — здесь есть, и NumPy/PyTorch на ней стоят); отрицательные индексы осей в `transpose(-2, -1)` — «с конца», как срезы §3 праймера; `torch.allclose(a, b)` — поэлементное сравнение с допуском (float'ы не сравнивают на `==`).

**Задание-проверка:** для каждой строки *до запуска* напиши ожидаемую форму результата на бумаге, потом сверь. Ошибся — вернись к правилу `(a×b)·(b×c)→a×c` из §1.4 книги.

## 1.2 Токен-калькулятор

Считаем стоимость своего корпуса. Токенизатор — `tiktoken` (быстрый, локальный) как приближение; точные числа твоего провайдера даст его API подсчёта:

```python
# uv add tiktoken
import glob, tiktoken

enc = tiktoken.get_encoding("o200k_base")     # словарь ~200k; конкретный энкодер сверь с моделью
stats = []
for path in glob.glob("../corpus/*.md"):
    text = open(path).read()
    n_tok, n_chars = len(enc.encode(text)), len(text)
    stats.append((path, n_tok, n_chars / n_tok))   # третье число — символов на токен

total = sum(n for _, n, _ in stats)
print(f"документов: {len(stats)}, всего токенов: {total}")
print(f"символов/токен (медиана): {sorted(s[2] for s in stats)[len(stats)//2]:.2f}")

for price_in in (0.25, 1.0, 3.0):             # $/1M входных — три яруса
    print(f"индексация корпуса при ${price_in}/M: ${total * price_in / 1e6:.4f}")
```

**Разбор синтаксиса:** `for _, n, _ in stats` — распаковка кортежа с `_` для ненужных полей (§3 праймера); `sorted(...)[len(stats)//2]` — медиана через сортировку, `//` — целочисленное деление; `:.2f` и `:.4f` в f-строках — формат «два/четыре знака после запятой» (§2).

**Fertility и множитель цены:** возьми один документ, переведи абзац на английский (моделью). Книга (§1.2) определяет fertility как среднее число токенов **на слово**, то есть считается она для каждого языка отдельно: `len(enc.encode(text)) / len(text.split())` — для ru и для en (у английского ≈ 1, у кириллицы заметно выше). Отношение `len(enc.encode(ru)) / len(enc.encode(en))` — это уже не fertility, а **множитель стоимости ru/en**: следствие fertility, но с примесью разного числа слов в переводе. Именно он и есть цена русскоязычной системы на твоём тексте.

## 1.3 GPT-блок по Raschka — печатай руками

Канва — главы 3–4 его книги; здесь только каркас self-attention, чтобы ты знал, куда идёшь (печатай сам, не копируй, — правило задания). Обучения в М1 нет — гл. 3–4 доводят ровно до прямого прохода на необученных весах; цикл обучения и оптимизатор идут дальше по книге (гл. 5; загрузку данных Raschka вводит раньше — точные номера сверь с оглавлением своего издания), а руками ты будешь дообучать в М7. Блок здесь — объект разбора, а не генератор осмысленного текста:

```python
import torch.nn as nn

class CausalSelfAttention(nn.Module):                # nn.Module — базовый класс всех слоёв
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()                            # ≈ super(); обязателен
        self.n_heads, self.d_head = n_heads, d_model // n_heads
        self.Wq = nn.Linear(d_model, d_model, bias=False)   # это та самая «проекция» §1.4
        self.Wk = nn.Linear(d_model, d_model, bias=False)
        self.Wv = nn.Linear(d_model, d_model, bias=False)
        self.Wo = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x):                             # forward = «прямой проход»; вызывается как слой(x)
        B, T, C = x.shape                             # batch, seq, d_model
        q = self.Wq(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)  # → B,h,T,d_head
        k = self.Wk(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        v = self.Wv(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) / self.d_head ** 0.5      # шаг 2 трассировки §1.4
        mask = torch.tril(torch.ones(T, T, dtype=torch.bool, device=x.device))
        att = att.masked_fill(~mask, float("-inf"))   # причинная маска: будущее не видно
        att = torch.softmax(att, dim=-1)              # шаг 3
        out = (att @ v).transpose(1, 2).reshape(B, T, C)          # шаги 4: собрать головы
        return self.Wo(out)                           # шаг 5
```

**Разбор синтаксиса:** `class CausalSelfAttention(nn.Module)` — наследование (§6 праймера); `self.Wq = nn.Linear(...)` — поля создаются в конструкторе присваиванием; `view(...)` — reshape без копирования («сантехника» из §A.3 книги); `d_head ** 0.5` — `**` это степень, здесь √d_head из шага 2 трассировки; `~mask` — логическое НЕ поэлементно; `float("-inf")` — тот самый −∞ маскирования логитов (§5.3 книги — да, это один и тот же приём!).

**DoD-проверка модуля** — письменно, с номерами строк *твоего* кода: где рождается T×T (O(n²)) и какие тензоры пришлось бы пересчитывать без KV-кэша (§1.6). Правильный ответ указывает на строку с `q @ k.transpose(...)` и на k/v как кэшируемые.

## 1.4 MoE-слой вместо FFN

```python
class MoEFFN(nn.Module):
    def __init__(self, d_model: int, d_ff: int, n_experts: int = 4, top_k: int = 2):
        super().__init__()
        self.router = nn.Linear(d_model, n_experts)   # §1.5 книги: роутер — просто линейный слой
        self.experts = nn.ModuleList(
            nn.Sequential(nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model))
            for _ in range(n_experts))
        self.top_k = top_k

    def forward(self, x):
        logits = self.router(x)                              # B,T,n_experts
        weights, idx = torch.topk(logits, self.top_k, dim=-1)  # top-k экспертов на КАЖДЫЙ токен
        weights = torch.softmax(weights, dim=-1)
        out = torch.zeros_like(x)
        for k in range(self.top_k):                          # учебная (медленная) маршрутизация
            for e in range(len(self.experts)):
                sel = idx[..., k] == e                       # маска токенов, выбравших эксперта e
                if sel.any():
                    out[sel] += weights[..., k][sel].unsqueeze(-1) * self.experts[e](x[sel])
        return out
```

**Счётное задание:** `sum(p.numel() for p in moe.parameters())` — total; active = роутер + top_k экспертов. Сравни с плотным FFN тех же d_ff; FLOPs/токен — по 2·(параметры в деле) из §23.4 книги. **Разбор:** `ModuleList(... for _ in range(...))` — генератор в конструкторе (§3, §12 праймера); `idx[..., k]` — `...` значит «все предыдущие оси»; `x[sel]` — булева индексация: выбрать строки по маске.

## 1.5 Стратегии декодирования: эксперимент §1.7

50 прогонов одной задачи извлечения JSON при T=0 и T=1 (Ollama, локально — бесплатно):

```python
import json, httpx

PROMPT = "Извлеки из текста JSON {\"city\": str, \"days\": int}. Текст: «Едем в Казань на 3 дня». Только JSON."

def run(temp: float, n: int = 50) -> tuple[int, set[str]]:
    valid, contents = 0, set()
    for _ in range(n):
        r = httpx.post("http://localhost:11434/api/generate", timeout=120,
                       json={"model": "qwen3:4b", "prompt": PROMPT, "stream": False,
                             "options": {"temperature": temp}})
        text = r.json()["response"].strip()
        try:
            json.loads(text); valid += 1; contents.add(text)
        except json.JSONDecodeError:
            pass
    return valid, contents

for t in (0.0, 1.0):
    v, c = run(t)
    print(f"T={t}: валидных {v}/50, уникальных ответов {len(c)}")
```

**Разбор:** `-> tuple[int, set[str]]` — функция возвращает кортеж, вызывающий распаковывает `v, c = run(t)` (§3, §5 праймера); `try/except json.JSONDecodeError: pass` — «поймать и проигнорировать» (§7); `set` копит только уникальные ответы — размер множества и есть мера разброса. Ожидание: T=0 даст `len(c)` больше 1 — недетерминизм живёт ниже сэмплирования; почему — §2.4 книги.

## 1.6 KV-кэш: расчёт против замера

Расчёт по формуле §1.6 книги (для своей локальной модели возьми параметры из `ollama show qwen3:8b`):

```python
def kv_bytes(n_layers, n_kv_heads, d_head, seq, bytes_per=2):   # 2 байта = FP16
    return 2 * n_layers * n_kv_heads * d_head * seq * bytes_per # первый множитель 2 — K и V

print(f"{kv_bytes(36, 8, 128, 8192) / 2**20:.0f} MiB на 8k контекста")
```

Замер: `ollama ps` до и после запроса с коротким (~50 токенов) и длинным (вставь документ на несколько тысяч токенов) контекстом — разница занятой памяти и есть цена KV. Расхождение с расчётом объясни письменно (квантизация кэша? GQA — n_kv_heads меньше числа голов? — оба фактора названы в §1.6).

## 1.7 Чек-лист DoD

- [ ] Ноутбук словаря операций: формы предсказаны до запуска, einsum совпал с matmul (`allclose`).
- [ ] Токен-калькулятор: таблица по корпусу + fertility ru и en + множитель стоимости ru/en + стоимость индексации на трёх ярусах.
- [ ] Свой GPT-блок собран (по Raschka гл. 3–4) + **письменный разбор O(n²)/KV со ссылками на строки своего кода**.
- [ ] MoE: таблица total/active/FLOPs против dense + записка-рекомендация (артефакт модуля).
- [ ] Декодирование: доли валидного JSON при T=0/T=1 и вывод о недетерминизме при T=0.
- [ ] KV-кэш: расчёт, замер, объяснение расхождения.
