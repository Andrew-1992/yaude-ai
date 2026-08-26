# Sanadi AI — Phase 1

An AI coding and research assistant for African developers, students, and researchers,
starting in South Sudan. Bilingual by design (Juba Arabic + English), built for
constrained connectivity and local pricing.

This repo is the **phase 1 scaffold**: fine-tune an existing open-weight coding model
rather than training from scratch, to reach a usable product quickly. From-scratch
foundation-model research (the original Sanadi AI direction) resumes in a later,
better-funded phase once this product has real users and usage data.

## Why this base model

**Base model: Qwen2.5-Coder-1.5B-Instruct**

| Consideration | Why it fits |
|---|---|
| License | Apache 2.0 — no usage restrictions, safe for a commercial product |
| Coding benchmarks | Strongest in its size class (HumanEval, MBPP) as of training data |
| Multilingual grounding | Qwen's pretraining corpus has meaningfully more Arabic-script exposure than DeepSeek-Coder or CodeLlama — a real head start for Juba Arabic, which sits on Arabic script and vocabulary |
| Size | 1.5B fits LoRA/QLoRA fine-tuning on a single consumer GPU (e.g. RTX 4090, 24GB) without needing multi-GPU infra |
| Upgrade path | Same family scales to 3B/7B/32B — re-run the same fine-tuning pipeline on a bigger checkpoint once there's funding/compute to justify it |

If early evals show Qwen2.5-Coder's Arabic handling isn't strong enough even as a base,
the fallback is fine-tuning a general-purpose multilingual model (e.g. Qwen2.5-3B-Instruct,
not the coder-specialized variant) and leaning harder on the SFT data to teach coding.
That trade-off should be an early, data-driven decision — see `docs/model-eval-notes.md`
once evaluation begins.

## Repo layout

```
configs/            Model, LoRA, and training hyperparameter configs (YAML)
data/
  raw/               Unprocessed source data (not committed — see .gitignore)
  processed/         Tokenized/formatted training-ready data (not committed)
scripts/
  prepare_data.py    Build the bilingual coding + research SFT dataset
  finetune.py        LoRA fine-tuning entrypoint (PEFT + TRL SFTTrainer)
  evaluate.py        Run coding/research task evals against a checkpoint
  serve.py           FastAPI inference server for the fine-tuned model
src/sanadi/          Shared Python package (data schemas, prompt templates, utils)
```

## Phase 1 build order

1. **Data pipeline** (`scripts/prepare_data.py`) — assemble coding + research SFT
   examples, English and Juba Arabic. This is the actual bottleneck: almost no
   Juba Arabic technical corpus exists, so a meaningful share of this data will be
   synthetically generated (English technical content translated/adapted with
   bilingual explanations) rather than scraped.
2. **Fine-tuning** (`scripts/finetune.py`) — LoRA fine-tune Qwen2.5-Coder-1.5B on the
   prepared dataset. Start small (a few hundred examples) to validate the pipeline
   end-to-end before investing in large-scale data collection.
3. **Evaluation** (`scripts/evaluate.py`) — practical checks: does it produce runnable
   code, does it correctly explain a bug, is the Juba Arabic output actually
   comprehensible (this last one needs a human fluent in Juba Arabic — you — in the loop,
   not an automated metric).
4. **Serving** (`scripts/serve.py`) — FastAPI endpoint wrapping the fine-tuned model,
   ready to sit behind the existing Next.js frontend pattern from earlier Sanadi AI work.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Requires a CUDA-capable GPU with at least 16GB VRAM for LoRA fine-tuning at this model
size (24GB recommended for comfortable batch sizes). CPU-only will run inference but
not practical fine-tuning.

## Status

Phase 1, step 1 (data pipeline scaffold). Nothing has been fine-tuned yet — this is
the starting structure, not a trained model.
