<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Модуль 7 — Свои модели: QLoRA и vLLM — детализация

*Спутник «Модуля 7». Самый плотный Python-модуль (HF-стек) и единственный платный по железу: GPU арендуется часами (~$10–25 на модуль). Всё готовится и отлаживается локально на крошечных объёмах, GPU включается только на длинный прогон.*

## 7.1 Решающая рамка (§21.1) — письменно, до кода

Пройди «Prompt → RAG → Fine-tune» для своего домена честно: что именно не решается промптом и ретривом? Для ассистента поддержки типичный вывод — «дообучение не нужно» (знания меняются — это RAG; формат — это structured output). Это *правильный* вывод; учебная задача дальше — осознанное упражнение: извлечение полей заявки в строгий JSON, где мы хотим маленькую локальную модель вместо большой.

## 7.2 Данные: 500–1000 примеров

Синтез + вычитка (правило корпуса из М0 действует и здесь):

```python
# py/ft/make_dataset.py — примеры в формате chat, сразу со сплитом
import json, random

examples = []          # заполняется синтезом через локальную модель + ТВОЕЙ вычиткой
...
random.shuffle(examples)
split = int(len(examples) * 0.9)
for name, part in [("train", examples[:split]), ("eval", examples[split:])]:
    with open(f"{name}.jsonl", "w") as f:
        for ex in part:
            f.write(json.dumps({"messages": [
                {"role": "user", "content": ex["ticket"]},
                {"role": "assistant", "content": json.dumps(ex["fields"], ensure_ascii=False)},
            ]}, ensure_ascii=False) + "\n")
```

**Разбор синтаксиса:** `examples[:split]` / `examples[split:]` — сплит срезами (§3 праймера); `json.dumps(..., ensure_ascii=False)` — без этого кириллица уедет в `\uXXXX`; JSONL — «по JSON-объекту на строку», стандарт обменного формата в ML.

Качество важнее объёма: 50 вычитанных пограничных случаев (опечатки, два товара в одном обращении, отсутствие поля) дадут больше, чем 500 одинаковых счастливых путей.

## 7.3 QLoRA-прогон (PEFT/TRL; Unsloth — более быстрая альтернатива с тем же смыслом)

```python
# py/ft/train.py — скелет; API TRL/PEFT меняется, сверь с установленной версией
from datasets import load_dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

lora = LoraConfig(
    r=16, lora_alpha=32,                    # ранг и масштаб — стартовые из §21.8 книги (смысл α/r — §21.3)
    lora_dropout=0.05,
    target_modules="all-linear",            # адаптеры на все линейные слои — дефолт статьи QLoRA;
                                            # §21.8 книги стартует с матриц внимания Q/K/V/O
                                            # и добавляет FFN при недоборе качества — отклонение осознанное
)
cfg = SFTConfig(
    output_dir="out",
    per_device_train_batch_size=2, gradient_accumulation_steps=8,   # эффективный батч 16
    learning_rate=2e-4, num_train_epochs=2,
    bf16=True,
    model_init_kwargs={"load_in_4bit": True},   # «Q» в QLoRA: базовые веса в 4 бита (§21.4)
)
trainer = SFTTrainer(model="Qwen/Qwen2.5-7B-Instruct",   # актуальную 7–8B сверь на HF
                     train_dataset=load_dataset("json", data_files="train.jsonl")["train"],
                     peft_config=lora, args=cfg)
trainer.train()                              # на арендованном GPU; локально — на 20 примерах для отладки
trainer.save_model("adapter")               # сохраняется ТОЛЬКО адаптер — десятки МБ, не гигабайты
```

**Разбор синтаксиса:** именованные аргументы конструкторов-конфигов (§5 праймера) — весь HF-стек так устроен: конфиг-объекты вместо билдеров; `load_dataset("json", ...)["train"]` — библиотека `datasets` возвращает словарь сплитов. Смысловые якоря — в комментариях: каждый параметр отсылает к §21.3–21.8 книги, не к магии.

Аренда GPU: любой почасовой провайдер, одна карта 24 ГБ. Прикинь память *до* аренды — это тоже DoD-навык. Книга даёт механику (§21.4: база заморожена и хранится в 4 битах, обучаются только адаптеры, состояние оптимизатора при всплесках выгружается страничным оптимизатором), арифметика прикидки — наша: 4 бита = 0.5 байта на параметр → база 7–8B ≈ 3.5–4 ГБ, сверху адаптеры (десятки МБ) и состояние оптимизатора — в 24 ГБ помещается с запасом. Отладь скрипт локально на 20 примерах (упадёт быстро и бесплатно), на GPU уходи с готовым.

## 7.4 Забывание — измерь (§21.8)

До/после дообучения, обе модели:

1. **Целевая задача:** точность извлечения полей на eval.jsonl (свой скрипт из М3-опыта: доля полностью верных JSON).
2. **Общие способности:** подмножество MMLU через lm-evaluation-harness:

```bash
uv add lm-eval
lm_eval --model hf \
  --model_args pretrained=Qwen/Qwen2.5-7B-Instruct,peft=./adapter,load_in_4bit=True \
  --tasks mmlu_high_school_computer_science,mmlu_formal_logic \
  --batch_size 4
# флаги и имена задач сверь: lm_eval --tasks list
```

Таблица 2×2 (модель × задача): выигрыш на целевой и просадка на общем — это и есть размен §21.8. Затем добавь в train 10–20% общих инструктивных данных (replay), повтори прогон — просадка должна уменьшиться. Три строки таблицы = главный артефакт модуля.

## 7.5 vLLM: сервинг с multi-LoRA

На том же арендованном хосте (docker; k8s/k3s — если хочешь потренировать прод-обвязку):

```bash
docker run --gpus all -p 8000:8000 \
  -v $PWD/adapter:/adapter \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-7B-Instruct \
  --enable-lora --lora-modules ticket-extractor=/adapter \
  --max-model-len 8192
# проверка: OpenAI-совместимый эндпоинт, модель = имя адаптера
curl -s localhost:8000/v1/chat/completions -d '{
  "model": "ticket-extractor",
  "messages": [{"role":"user","content":"Сломался чайник, заказ 4412, хочу возврат"}]}'
```

Multi-LoRA — то самое «одна база, много адаптеров» из §21.3: базовые веса в памяти один раз, адаптеры подключаются по имени модели в запросе.

**Замеры (§22.8 руками):** прогони 200 запросов при конкуренции 1 / 8 / 32 (простейший способ — `xargs -P`, честнее — свой скрипт с `asyncio` или locust): throughput (токенов/с суммарно) и p50/p99 латентности на запрос. Увидишь размен из книги: батч растит пропускную способность и хвост латентности одновременно.

**Break-even (§2.6):** ($/час аренды) / (реальный throughput, токенов/с × 3600) × 1 000 000 = $/1M токенов твоего сервинга (без ×10⁶ получится цена одного токена — проверь размерность, это классическая ошибка на салфетке); сравни с hosted-тарифом дешёвого яруса и посчитай, при каком *постоянном* трафике аренда окупается. Записка «когда мой self-host окупается» — с этими числами.

## 7.6 (Опц.) Предобучение-мини

nanoGPT на крошечном корпусе (свои регламенты + любая открытая проза, ~10 МБ): цель — не модель, а *счёт*. Посчитай C≈6ND для своего прогона заранее (N — параметры конфига, D — токены корпуса × эпохи), сверь с фактическим временем на GPU и его паспортными FLOPS — увидь и формулу §23.4, и КПД утилизации: он будет сильно меньше 100%, и это нормально — почему, объясняет арифметическая интенсивность и «точка баланса» ускорителя (§A.3, §1.6).

## 7.7 Чек-лист DoD

- [ ] Письменная решающая рамка §21.1 (даже если вывод — «не нужно»).
- [ ] Датасет: 500–1000 примеров, вычитан, train/eval сплит.
- [ ] Адаптер обучен; память под прогон прикинута ДО аренды и сошлась с фактом.
- [ ] Таблица забывания 3×2 (base / ft / ft+replay × целевая / MMLU) — главный артефакт.
- [ ] vLLM с multi-LoRA отвечает; замеры конкуренции 1/8/32 сняты.
- [ ] Записка break-even с числами своего железа против hosted.
