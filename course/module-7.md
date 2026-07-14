<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Module 7 — Models of Your Own: QLoRA and vLLM — In Depth

*A companion to "Module 7" in the course overview (README.md). The densest Python module (the HF stack) and the only one that costs money in hardware: the GPU is rented by the hour (~$10–25 for the module). Everything is prepared and debugged locally on tiny volumes; the GPU is switched on only for the long run.*

## 7.1 The decision frame (§21.1)—in writing, before any code

Walk "Prompt → RAG → Fine-tune" through your own domain honestly: what exactly is it that prompting and retrieval do not solve? For a support assistant the typical conclusion is "no fine-tuning needed" (knowledge changes—that's RAG; format—that's structured output). That is the *right* conclusion; the task from here on is a deliberate exercise: extracting ticket fields into strict JSON, where we want a small local model instead of a big one.

## 7.2 Data: 500–1000 examples

Synthesis + proofreading (the corpus rule from Module 0 applies here too):

```python
# py/ft/make_dataset.py—chat-format examples, split included
import json, random

examples = []          # filled by synthesis through a local model + YOUR proofreading
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

**Syntax walkthrough:** `examples[:split]` / `examples[split:]`—the split done with slices (§3 of the primer); `json.dumps(..., ensure_ascii=False)`—without it Cyrillic drifts off into `\uXXXX`; JSONL—"one JSON object per line," the standard interchange format in ML.

Quality beats volume: 50 proofread edge cases (typos, two products in one ticket, a missing field) will do more than 500 identical happy paths.

## 7.3 The QLoRA run (PEFT/TRL; Unsloth—a faster alternative that does the same thing)

```python
# py/ft/train.py—a skeleton; the TRL/PEFT API moves, check it against your installed version
from datasets import load_dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

lora = LoraConfig(
    r=16, lora_alpha=32,                    # rank and scale—the starting points from §21.8 of the book (the meaning of α/r—§21.3)
    lora_dropout=0.05,
    target_modules="all-linear",            # adapters on every linear layer—the QLoRA paper's default;
                                            # §21.8 of the book starts with the Q/K/V/O attention matrices
                                            # and adds the FFN when quality falls short—a deliberate deviation
)
cfg = SFTConfig(
    output_dir="out",
    per_device_train_batch_size=2, gradient_accumulation_steps=8,   # effective batch 16
    learning_rate=2e-4, num_train_epochs=2,
    bf16=True,
    model_init_kwargs={"load_in_4bit": True},   # the "Q" in QLoRA: base weights in 4 bits (§21.4)
)
trainer = SFTTrainer(model="Qwen/Qwen2.5-7B-Instruct",   # check HF for the current 7–8B
                     train_dataset=load_dataset("json", data_files="train.jsonl")["train"],
                     peft_config=lora, args=cfg)
trainer.train()                              # on the rented GPU; locally—on 20 examples, for debugging
trainer.save_model("adapter")               # ONLY the adapter is saved—tens of MB, not gigabytes
```

**Syntax walkthrough:** keyword arguments to config constructors (§5 of the primer)—the whole HF stack is built this way: config objects instead of builders; `load_dataset("json", ...)["train"]`—the `datasets` library returns a dict of splits. The anchors of meaning sit in the comments: every parameter points at §21.3–21.8 of the book, not at magic.

Renting a GPU: any by-the-hour provider, one 24 GB card. Estimate the memory *before* you rent—that too is a DoD skill. The book gives the mechanics (§21.4: the base is frozen and stored in 4 bits, only the adapters are trained, and optimizer state is paged out on spikes by a paged optimizer); the arithmetic of the estimate is ours: 4 bits = 0.5 bytes per parameter → a 7–8B base ≈ 3.5–4 GB, with adapters (tens of MB) and optimizer state on top—it fits into 24 GB with room to spare. Debug the script locally on 20 examples (it will fail fast and for free); go to the GPU with something that already works.

## 7.4 Forgetting—measure it (§21.8)

Before/after fine-tuning, both models:

1. **The target task:** field-extraction accuracy on eval.jsonl (your own script, out of the Module 3 experience: the share of fully correct JSON).
2. **General abilities:** a subset of MMLU through lm-evaluation-harness:

```bash
uv add lm-eval
lm_eval --model hf \
  --model_args pretrained=Qwen/Qwen2.5-7B-Instruct,peft=./adapter,load_in_4bit=True \
  --tasks mmlu_high_school_computer_science,mmlu_formal_logic \
  --batch_size 4
# check the flags and task names: lm_eval --tasks list
```

A 2×2 table (model × task): the gain on the target and the drop on the general—that is the §21.8 trade-off itself. Then mix 10–20% general instruction data (replay) into train and repeat the run—the drop should shrink. Three rows of the table = the module's main artifact.

## 7.5 vLLM: serving with multi-LoRA

On the same rented host (docker; k8s/k3s—if you want to practice the production wiring):

```bash
docker run --gpus all -p 8000:8000 \
  -v $PWD/adapter:/adapter \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-7B-Instruct \
  --enable-lora --lora-modules ticket-extractor=/adapter \
  --max-model-len 8192
# check: an OpenAI-compatible endpoint, model = the adapter's name
curl -s localhost:8000/v1/chat/completions -d '{
  "model": "ticket-extractor",
  "messages": [{"role":"user","content":"The kettle broke, order 4412, I want a refund"}]}'
```

Multi-LoRA is exactly the "one base, many adapters" of §21.3: the base weights sit in memory once, and adapters are attached by the model name in the request.

**Measurements (§22.8 by hand):** run 200 requests at concurrency 1 / 8 / 32 (the simplest way is `xargs -P`; more honest is your own script with `asyncio`, or locust): throughput (tokens/s in total) and p50/p99 latency per request. You will see the trade-off from the book: a batch grows throughput and the latency tail at the same time.

**Break-even (§2.6):** ($/hour of rent) / (real throughput, tokens/s × 3600) × 1,000,000 = $/1M tokens of your own serving (without the ×10⁶ you get the price of a single token—check the dimension, that is the classic napkin mistake); compare against the hosted rate of a cheap tier and work out at what *sustained* traffic the rental pays for itself. The memo "when my self-host pays for itself"—with these numbers.

## 7.6 (Opt.) Pre-training in miniature

nanoGPT on a tiny corpus (your own regulations + any open prose, ~10 MB): the goal is not a model but the *arithmetic*. Compute C≈6ND for your run in advance (N—the config's parameters, D—corpus tokens × epochs), check it against the actual time on the GPU and the card's spec-sheet FLOPS—and see both the §23.4 formula and the utilization efficiency: it will be far below 100%, and that is normal—the reason is arithmetic intensity and the accelerator's "balance point" (§A.3, §1.6).

## 7.7 DoD checklist

- [ ] The written decision frame of §21.1 (even if the conclusion is "not needed").
- [ ] Dataset: 500–1000 examples, proofread, train/eval split.
- [ ] The adapter is trained; the memory for the run was estimated BEFORE renting and matched reality.
- [ ] The 3×2 forgetting table (base / ft / ft+replay × target / MMLU)—the main artifact.
- [ ] vLLM with multi-LoRA answers; the concurrency 1/8/32 measurements are taken.
- [ ] A break-even memo with the numbers of your own hardware against hosted.
