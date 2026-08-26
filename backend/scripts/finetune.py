"""
LoRA fine-tune the phase 1 base model (Qwen2.5-Coder-1.5B-Instruct) on the
prepared coding + research dataset.

Usage:
    python scripts/finetune.py --model-config configs/model.yaml --train-config configs/train.yaml

Requires: data/processed/train.jsonl and data/processed/eval.jsonl to already
exist (run prepare_data.py first).
"""

import argparse
from pathlib import Path

import yaml
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM


def load_config(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build_model_and_tokenizer(model_cfg: dict):
    use_cuda = torch.cuda.is_available()
    if not use_cuda:
        print(
            "WARNING: no CUDA GPU detected. This script is built around 4-bit "
            "quantized LoRA fine-tuning, which requires a CUDA GPU -- it will not "
            "run correctly on CPU-only machines. Use scripts/smoke_test_base_model.py "
            "for a CPU-friendly environment check instead, and run real fine-tuning "
            "on a rented GPU (e.g. RunPod) once your dataset is ready."
        )
        raise SystemExit(1)

    bnb_cfg = None
    if model_cfg.get("quantization", {}).get("load_in_4bit"):
        q = model_cfg["quantization"]
        bnb_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=getattr(torch, q["bnb_4bit_compute_dtype"]),
            bnb_4bit_quant_type=q["bnb_4bit_quant_type"],
            bnb_4bit_use_double_quant=q["bnb_4bit_use_double_quant"],
        )

    tokenizer = AutoTokenizer.from_pretrained(
        model_cfg["base_model"], trust_remote_code=model_cfg.get("trust_remote_code", False)
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_cfg["base_model"],
        quantization_config=bnb_cfg,
        device_map="auto",
        trust_remote_code=model_cfg.get("trust_remote_code", False),
    )

    if bnb_cfg is not None:
        model = prepare_model_for_kbit_training(model)

    lora_cfg = LoraConfig(**model_cfg["lora"])
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    return model, tokenizer


def format_example(example: dict, tokenizer) -> str:
    """Render a chat-format example into the model's prompt template."""
    return tokenizer.apply_chat_template(example["messages"], tokenize=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-config", type=Path, default=Path("configs/model.yaml"))
    parser.add_argument("--train-config", type=Path, default=Path("configs/train.yaml"))
    args = parser.parse_args()

    model_cfg = load_config(args.model_config)
    train_cfg = load_config(args.train_config)

    model, tokenizer = build_model_and_tokenizer(model_cfg)

    data_cfg = train_cfg["data"]
    dataset = load_dataset(
        "json",
        data_files={
            "train": data_cfg["train_path"],
            "eval": data_cfg["eval_path"],
        },
    )

    def _format(batch):
        return {"text": [format_example({"messages": m}, tokenizer) for m in batch["messages"]]}

    dataset = dataset.map(_format, batched=True)

    t = train_cfg["training"]
    training_args = TrainingArguments(
        output_dir=t["output_dir"],
        num_train_epochs=t["num_train_epochs"],
        per_device_train_batch_size=t["per_device_train_batch_size"],
        per_device_eval_batch_size=t["per_device_eval_batch_size"],
        gradient_accumulation_steps=t["gradient_accumulation_steps"],
        learning_rate=t["learning_rate"],
        lr_scheduler_type=t["lr_scheduler_type"],
        warmup_ratio=t["warmup_ratio"],
        weight_decay=t["weight_decay"],
        logging_steps=t["logging_steps"],
        eval_strategy=t["eval_strategy"],
        eval_steps=t["eval_steps"],
        save_strategy=t["save_strategy"],
        save_steps=t["save_steps"],
        save_total_limit=t["save_total_limit"],
        bf16=t["bf16"],
        gradient_checkpointing=t["gradient_checkpointing"],
        report_to=t["report_to"],
        run_name=train_cfg["run_name"],
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["eval"],
        dataset_text_field="text",
        max_seq_length=data_cfg["max_seq_length"],
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(t["output_dir"])
    tokenizer.save_pretrained(t["output_dir"])
    print(f"Training complete. Adapter saved to {t['output_dir']}")


if __name__ == "__main__":
    main()
