"""
Evaluate a fine-tuned checkpoint on practical, task-level criteria — not
academic benchmark scores. The questions this script (and the human review
step it prints reminders for) should answer:

  - Does generated code actually run?
  - Does a debugging response correctly identify and fix the bug?
  - Is a Juba Arabic response comprehensible and correct? (THIS SCRIPT CANNOT
    JUDGE THIS — it flags these examples for human review and stops there.)

Usage:
    python scripts/evaluate.py --checkpoint checkpoints/sanadi-coder-v0 --eval-file data/processed/eval.jsonl
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def load_eval_examples(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def check_code_runs(code: str, timeout: int = 5) -> tuple[bool, str]:
    """Best-effort check that generated Python code executes without error.
    Not a substitute for real test cases — just a fast, cheap smoke test."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        result = subprocess.run(
            [sys.executable, path], capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "timed out"
    finally:
        Path(path).unlink(missing_ok=True)


def run_eval(checkpoint: Path, eval_path: Path):
    examples = load_eval_examples(eval_path)
    if not examples:
        print("No eval examples found. Run prepare_data.py first.")
        return

    juba_arabic_count = sum(1 for ex in examples if ex.get("language") == "juba_ar")
    code_count = sum(1 for ex in examples if "code" in ex.get("task_type", ""))

    print(f"Loaded {len(examples)} eval examples "
          f"({code_count} coding, {juba_arabic_count} Juba Arabic).")
    print()
    print("This script does NOT yet run the model for generation — wire in your")
    print("inference call here (load the checkpoint, generate a response per")
    print("example, then apply the checks below to each response).")
    print()

    if juba_arabic_count > 0:
        print(
            f"REMINDER: {juba_arabic_count} Juba Arabic example(s) in this eval set "
            "need a fluent human reviewer. No automated metric here can validate "
            "correctness or naturalness of Juba Arabic output — don't ship based on "
            "English-only eval results if the product claims Juba Arabic support."
        )

    print()
    print("Suggested review rubric per example (fill in once generation is wired up):")
    print("  - Coding: does it run? does it solve the actual task? (not just 'looks plausible')")
    print("  - Debugging: does it identify the real bug, not a plausible-sounding wrong one?")
    print("  - Research: is the summary/explanation faithful to the source, not just fluent?")
    print("  - Juba Arabic (any task): human-reviewed only, see reminder above")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--eval-file", type=Path, default=Path("data/processed/eval.jsonl"))
    args = parser.parse_args()
    run_eval(args.checkpoint, args.eval_file)


if __name__ == "__main__":
    main()
