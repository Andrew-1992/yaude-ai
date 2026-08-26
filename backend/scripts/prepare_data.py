"""
Build the phase 1 SFT dataset: coding + research tasks, English + Juba Arabic.

This is a STARTING SCAFFOLD, not a finished pipeline — the actual data collection
work (sourcing code Q&A, research examples, and especially the bilingual Juba
Arabic content) still needs to happen. This script defines the shape of that
work and gives you a runnable, if empty, pipeline to fill in incrementally.

Usage:
    python scripts/prepare_data.py --out data/processed/

What this script does NOT yet do (fill in as data sources are lined up):
  - Pull real code Q&A from permissively-licensed sources
  - Pull real open-access research paper summaries
  - Generate synthetic Juba Arabic technical content
  - De-duplicate or quality-filter examples

See the "Data sourcing plan" section below before writing real loaders.
"""

import argparse
import json
import random
from pathlib import Path
from typing import Iterator

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sanadi.schema import SFTExample, TaskType, Language


# ---------------------------------------------------------------------------
# Data sourcing plan (fill in real loaders here as sources are lined up)
# ---------------------------------------------------------------------------
#
# 1. Coding data (English):
#    - Permissively-licensed code Q&A (check license before use — MIT/Apache/
#      CC-BY only; skip anything GPL or unlicensed)
#    - Synthetic examples: generate {bug, fix, explanation} triples from
#      common beginner mistakes in Python/JavaScript (the languages most
#      relevant to your Starford CS curriculum and Alole Technologies' stack)
#
# 2. Research data (English):
#    - Open-access paper abstracts + plain-language summaries (arXiv, AJOL —
#      African Journals Online — is a good source for regionally relevant work)
#    - Thesis/proposal structuring examples, if you can source or construct
#      them ethically (no scraping real students' unpublished work without
#      consent)
#
# 3. Bilingual Juba Arabic content:
#    - This is the genuinely hard part — almost no natural Juba Arabic
#      technical corpus exists. Two realistic paths:
#      a) Synthetic: take English technical Q&A, have a fluent speaker
#         (or a careful human-reviewed generation + correction pass) produce
#         a Juba Arabic explanation alongside it
#      b) Code-switched: capture how South Sudanese developers actually talk
#         about code day-to-day (often English technical terms embedded in
#         Juba Arabic sentences) rather than forcing pure Juba Arabic
#    - Budget real human review time here — this is the one part of the
#      dataset an automated pipeline genuinely cannot validate.
#
# ---------------------------------------------------------------------------


def load_seed_examples() -> Iterator[SFTExample]:
    """
    Hand-verified English seed examples spanning all task types and a range
    of difficulty. Real enough to fine-tune a first small pass on, but still
    small relative to what a real launch needs — treat this as the floor,
    not the target. Extend with real loaders per the sourcing plan above.

    Every example here was written and checked by hand (not generated) —
    that verification is what makes it safe to train on. Any new example
    added to this function should meet the same bar: runnable code where
    code is involved, a technically correct explanation, before it goes in.
    """

    # --- Code generation --------------------------------------------------
    yield SFTExample(
        instruction="Write a Python function that checks if a string is a palindrome, ignoring case and spaces.",
        response=(
            "```python\n"
            "def is_palindrome(s: str) -> bool:\n"
            "    cleaned = s.lower().replace(' ', '')\n"
            "    return cleaned == cleaned[::-1]\n"
            "```\n\n"
            "This lowercases the string and strips spaces before comparing it to its "
            "reverse. `is_palindrome(\"Race car\")` returns `True`."
        ),
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="Write a function in JavaScript that fetches data from a URL and returns the JSON, handling errors.",
        response=(
            "```javascript\n"
            "async function fetchJSON(url) {\n"
            "  try {\n"
            "    const response = await fetch(url);\n"
            "    if (!response.ok) {\n"
            "      throw new Error(`HTTP error: ${response.status}`);\n"
            "    }\n"
            "    return await response.json();\n"
            "  } catch (err) {\n"
            "    console.error('Fetch failed:', err.message);\n"
            "    return null;\n"
            "  }\n"
            "}\n"
            "```\n\n"
            "This checks `response.ok` before parsing (fetch doesn't throw on HTTP "
            "error codes like 404 by default), and catches network-level failures too."
        ),
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="Write a SQL query to find the second-highest salary in an `employees` table with columns `id`, `name`, `salary`.",
        response=(
            "```sql\n"
            "SELECT MAX(salary) AS second_highest\n"
            "FROM employees\n"
            "WHERE salary < (SELECT MAX(salary) FROM employees);\n"
            "```\n\n"
            "The inner query finds the highest salary; the outer query finds the "
            "highest salary that's still less than that, which is the second-highest. "
            "This handles ties correctly (if two people share the top salary, this "
            "still finds the next distinct value down)."
        ),
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intermediate",
    )

    # --- Code debugging ------------------------------------------------------
    yield SFTExample(
        instruction="This function should return the sum of a list but returns None:\n\n"
                     "def total(nums):\n    for n in nums:\n        s = 0\n        s += n",
        response=(
            "The bug is that `s = 0` is inside the loop, so it resets to 0 on every "
            "iteration instead of accumulating. It also never returns a value. Fixed:\n\n"
            "```python\ndef total(nums):\n    s = 0\n    for n in nums:\n        s += n\n    "
            "return s\n```"
        ),
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="This React component doesn't update when the button is clicked:\n\n"
                     "function Counter() {\n  let count = 0;\n  return (\n    <button onClick={() => count++}>{count}</button>\n  );\n}",
        response=(
            "The bug is that `count` is a plain variable, not React state — mutating it "
            "with `count++` doesn't trigger a re-render, so the displayed value never "
            "updates even though the variable changes internally. Fixed with `useState`:\n\n"
            "```jsx\n"
            "import { useState } from 'react';\n\n"
            "function Counter() {\n"
            "  const [count, setCount] = useState(0);\n"
            "  return (\n"
            "    <button onClick={() => setCount(count + 1)}>{count}</button>\n"
            "  );\n"
            "}\n"
            "```"
        ),
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="Why does this loop never terminate?\n\n"
                     "i = 0\nwhile i != 10:\n    i += 2",
        response=(
            "`i` starts at 0 and increases by 2 each time: 0, 2, 4, 6, 8, 10 — so it "
            "actually should terminate here since it does hit exactly 10. This version "
            "IS correct. The bug pattern to watch for is when the step size can skip "
            "past the target — e.g. `while i != 10: i += 3` never terminates, because "
            "i goes 0, 3, 6, 9, 12... and skips 10 entirely. Prefer `while i < 10` over "
            "`while i != 10` when the step size might not land exactly on the target."
        ),
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intro",
    )

    # --- Code explanation ------------------------------------------------------
    yield SFTExample(
        instruction="Explain what a Python list comprehension does, with an example.",
        response=(
            "A list comprehension builds a new list by applying an expression "
            "to each item in an iterable, optionally filtering items.\n\n"
            "Example: `[x * 2 for x in range(5)]` produces `[0, 2, 4, 6, 8]` — "
            "it doubles each number from 0 to 4."
        ),
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="What's the difference between `==` and `is` in Python?",
        response=(
            "`==` checks value equality — whether two objects contain the same data. "
            "`is` checks identity — whether two variables point to the exact same "
            "object in memory.\n\n"
            "`[1, 2] == [1, 2]` is `True` (same values, different list objects), but "
            "`[1, 2] is [1, 2]` is `False` (they're two separate objects). Use `is` "
            "mainly for `None` checks (`x is None`), and `==` for comparing values."
        ),
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="Explain what an API rate limit is and why services use them.",
        response=(
            "A rate limit caps how many requests a client can make to an API in a "
            "given time window (e.g. 100 requests per minute). Services use them to:\n\n"
            "- Prevent any single user or bug from overwhelming the server\n"
            "- Keep the service fair across many users sharing the same infrastructure\n"
            "- Control costs, since each request usually consumes compute or bandwidth\n\n"
            "When you exceed the limit, the API typically responds with an HTTP 429 "
            "(\"Too Many Requests\") status code, often with a `Retry-After` header "
            "telling you how long to wait before trying again."
        ),
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intermediate",
    )

    # --- Research summary ------------------------------------------------------
    yield SFTExample(
        instruction="Summarize the difference between qualitative and quantitative research methods for a research methods assignment.",
        response=(
            "Quantitative research collects numerical data and analyzes it "
            "statistically to test hypotheses or measure relationships — e.g. a "
            "survey with rating scales analyzed for statistical significance. "
            "Qualitative research collects non-numerical data (interviews, "
            "observations, open-ended responses) to understand experiences, "
            "meanings, or context in depth.\n\n"
            "Quantitative answers \"how much\" or \"how many\"; qualitative answers "
            "\"why\" or \"how.\" Many strong research designs combine both "
            "(mixed-methods) — using qualitative work to generate hypotheses that "
            "quantitative work then tests, or quantitative results that qualitative "
            "interviews then help explain."
        ),
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="What is a literature review, and what should one accomplish in a thesis?",
        response=(
            "A literature review surveys existing published research relevant to your "
            "topic, rather than presenting new findings. In a thesis, it should:\n\n"
            "1. Show you understand the current state of knowledge in your field\n"
            "2. Identify gaps, disagreements, or unanswered questions in existing work\n"
            "3. Position your own research as addressing one of those gaps\n"
            "4. Establish the theoretical framework or methods your study builds on\n\n"
            "A common mistake is writing it as a list of summaries (\"Smith (2020) "
            "found X. Jones (2021) found Y.\") rather than synthesizing sources into "
            "a coherent argument about what's known, what's contested, and what's "
            "missing — the synthesis is what makes it a *review* rather than an "
            "annotated bibliography."
        ),
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intermediate",
    )

    # --- Research writing ------------------------------------------------------
    yield SFTExample(
        instruction="How should I structure the introduction of a computer science thesis proposal?",
        response=(
            "A strong CS thesis proposal introduction typically moves through four "
            "stages, in order:\n\n"
            "1. **Context** — the broader problem area and why it matters (1-2 "
            "paragraphs)\n"
            "2. **Gap** — what's missing or unsolved in current approaches, "
            "specifically\n"
            "3. **Your approach** — a brief, high-level statement of what you propose "
            "to build or investigate, without full technical detail yet\n"
            "4. **Contribution** — what this work will add once complete (a system, "
            "an evaluation, a new method)\n\n"
            "Keep it to roughly one page. Save the full technical design, related "
            "work comparison, and methodology for their own dedicated sections later "
            "in the proposal — the introduction's job is to make a reader want to keep "
            "reading, not to explain everything."
        ),
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="Rewrite this sentence to be more formal for an academic paper: \"We tried a bunch of different settings and picked the one that worked best.\"",
        response=(
            "\"A range of configurations was evaluated, and the setting yielding the "
            "best performance was selected.\"\n\n"
            "Changes made: passive voice is common in formal academic writing to keep "
            "focus on the work rather than the researcher; \"a bunch of\" becomes "
            "\"a range of\" (more precise, less casual); \"tried\" becomes \"evaluated\" "
            "(more specific about what was actually done); \"worked best\" becomes "
            "\"yielding the best performance\" (measurable, not vague)."
        ),
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="hand-written-seed",
        difficulty="intro",
    )

    # NOTE: no Juba Arabic or mixed-language examples here yet. Those come
    # from data/juba_arabic_intake.csv once filled in and reviewed — see
    # docs/juba-arabic-data-guide.md for the process. Do not hand-write or
    # generate Juba Arabic examples in this function without a fluent
    # reviewer verifying them first.


def split_and_write(examples: list[SFTExample], out_dir: Path, eval_fraction: float = 0.1) -> None:
    random.seed(42)
    random.shuffle(examples)
    split_idx = max(1, int(len(examples) * (1 - eval_fraction))) if len(examples) > 1 else len(examples)
    train, eval_ = examples[:split_idx], examples[split_idx:]

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(train, out_dir / "train.jsonl")
    _write_jsonl(eval_, out_dir / "eval.jsonl")
    print(f"Wrote {len(train)} train examples, {len(eval_)} eval examples to {out_dir}")


def _write_jsonl(examples: list[SFTExample], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for ex in examples:
            record = {
                "messages": ex.to_chat_format(),
                "task_type": ex.task_type.value,
                "language": ex.language.value,
                "source": ex.source,
                "difficulty": ex.difficulty,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data/processed"))
    args = parser.parse_args()

    examples = list(load_seed_examples())
    if len(examples) < 50:
        print(
            f"WARNING: only {len(examples)} examples loaded. This is a seed set for "
            "pipeline validation, not enough to fine-tune on. Wire in real data "
            "sources per the plan in this script's header before training."
        )
    split_and_write(examples, args.out)


if __name__ == "__main__":
    main()
