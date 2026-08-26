"""
CPU-friendly smoke test: confirms the environment works end to end and
captures a BASELINE of how the un-fine-tuned model performs on your actual
eval examples, before any training happens.

This does NOT fine-tune anything — it just loads the base model and runs
generation. Purpose:

  1. Catch environment problems now (model download, tokenizer, chat
     template, dependency versions) rather than discovering them mid
     GPU-rental session on RunPod, where every minute costs money.
  2. Give you a real "before" baseline to compare fine-tuned checkpoints
     against later — without this, you can't tell how much the fine-tuning
     actually helped versus what Qwen2.5-Coder could already do out of the box.

Usage:
    python scripts/smoke_test_base_model.py

Expect this to take a few minutes on CPU (model download the first time,
then slow-but-tolerable generation for a handful of short prompts). This is
fine for 2-3 prompts; it is NOT how you'd want to run real evaluation at
scale — that happens on GPU via evaluate.py once you have a fine-tuned
checkpoint.
"""

import json
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

BASE_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
EVAL_PATH = Path("data/processed/eval.jsonl")
MAX_NEW_TOKENS = 200  # kept short deliberately -- CPU generation is slow


def load_eval_prompts(path: Path, limit: int = 3) -> list[str]:
    if not path.exists():
        print(f"No eval file at {path} -- run scripts/prepare_data.py first.")
        return []
    prompts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if len(prompts) >= limit:
                break
            record = json.loads(line)
            user_msg = next(
                (m["content"] for m in record["messages"] if m["role"] == "user"), None
            )
            if user_msg:
                prompts.append(user_msg)
    return prompts


def main():
    print(f"Loading tokenizer and model ({BASE_MODEL})...")
    print("First run downloads the model (~3GB) -- this may take a while on a slow connection.")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float32,  # no bf16/4-bit -- plain fp32 for CPU correctness
        device_map="cpu",
    )
    model.eval()

    print(f"Loaded in {time.time() - t0:.1f}s.\n")

    prompts = load_eval_prompts(EVAL_PATH)
    if not prompts:
        prompts = ["Write a Python function that reverses a string."]
        print("Using a fallback prompt since no eval file was found.\n")

    for i, prompt in enumerate(prompts, 1):
        print(f"--- Prompt {i} ---")
        print(prompt)
        print()

        messages = [{"role": "user", "content": prompt}]
        chat_input = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(chat_input, return_tensors="pt")

        t0 = time.time()
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,  # deterministic -- easier to compare runs
                pad_token_id=tokenizer.eos_token_id,
            )
        elapsed = time.time() - t0

        generated = output_ids[0][inputs["input_ids"].shape[1]:]
        response = tokenizer.decode(generated, skip_special_tokens=True)

        print(f"--- Response ({elapsed:.1f}s on CPU) ---")
        print(response)
        print()

    print(
        "Smoke test complete. If responses above look coherent, your environment "
        "is confirmed working end to end. Save this output somewhere -- it's your "
        "baseline to compare fine-tuned checkpoints against once you train on RunPod."
    )


if __name__ == "__main__":
    main()
