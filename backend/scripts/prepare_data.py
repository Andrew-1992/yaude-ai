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

from yaude.schema import SFTExample, TaskType, Language


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

    yield SFTExample(
        instruction="I'm building a small portfolio project. Write a function that returns only even numbers from a list.",
        response="""```python
def evens(numbers):
    return [n for n in numbers if n % 2 == 0]
```

This uses a list comprehension: it walks through `numbers`, and for each one keeps it only if `n % 2 == 0` — meaning dividing by 2 leaves no remainder, which is the definition of even. The comprehension is just a compact way to write a loop that builds a new list, and it's the idiomatic Python style for this kind of filtering rather than a manual for-loop with `.append()`.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm debugging a student project. How do you make a controlled text input in React?",
        response="""```jsx
const [name, setName] = useState("");

<input value={name} onChange={e => setName(e.target.value)} />
```

"Controlled" means React's state — not the DOM — is the source of truth for the input's value. Every keystroke fires `onChange`, which updates `name` in state, and the input's `value` is always set from that same state. That round-trip is what makes it "controlled": if you set `value` without `onChange`, the input becomes read-only, since nothing ever updates the state that `value` is reading from — that's the most common bug people hit here.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm building a small portfolio project. Write a function that checks whether a value exists in a list.",
        response="""```python
def contains(items, value):
    return value in items
```

The `in` operator does a membership check — it scans `items` until it finds a match or reaches the end. Worth knowing: for a list, this is O(n) — it can check every element in the worst case. If you're checking membership repeatedly against the same collection, converting it to a `set` first makes each check O(1) on average, which matters once the list gets large.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a database index?",
        response="""An index is an auxiliary data structure — commonly a B-tree — that lets the database find rows matching a condition without scanning the entire table. For example, an index on a `students.age` column lets a query like `WHERE age > 20` jump straight to the relevant rows instead of checking every row in the table.

The trade-off: indexes speed up reads but slow down writes, since every `INSERT` or `UPDATE` has to also update the index. They also take up storage. Because of that, indexes should be added based on your actual query patterns — indexing every column "just in case" usually costs more than it helps.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm practicing programming for a university assignment. Write a function that removes falsy values from an array.",
        response="""```javascript
function compact(array) {
    return array.filter(Boolean);
}
```

`Boolean` used this way acts as the filter's test function — for each element, `filter` keeps it only if `Boolean(element)` is `true`. In JavaScript, the "falsy" values are `false`, `0`, `""` (empty string), `null`, `undefined`, and `NaN` — everything else, including `"0"` (a non-empty string) and empty arrays/objects, is truthy and gets kept.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm building a small portfolio project. Write a function that returns the length of a string.",
        response="""```python
def length(text):
    return len(text)
```

`len()` is a built-in that works on strings, lists, and other collections because they each implement a `__len__` method internally — `len(text)` is really calling `text.__len__()` behind the scenes. Wrapping it in your own function like this is mostly useful if you want a consistent name across your codebase, or plan to add extra logic (like handling `None`) later.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="I'm practicing programming for a university assignment. How do you center items using Flexbox?",
        response="""```css
.container {
    display: flex;
    justify-content: center;
    align-items: center;
}
```

`display: flex` turns on flexbox layout for the container's direct children. From there, `justify-content` controls alignment along the main axis (horizontal, by default) and `align-items` controls the cross axis (vertical, by default) — setting both to `center` centers content in both directions. If you rotate the layout with `flex-direction: column`, the two axes swap, so `justify-content` then controls vertical alignment instead.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What does SELECT do in SQL?",
        response="""`SELECT` is the core statement for reading data from a table:

```sql
SELECT name, email
FROM students;
```

This returns the `name` and `email` columns for every row in `students`. You can list specific columns like this, or use `SELECT *` to get every column — though listing exact columns is usually better practice, since it's clearer what the query actually needs and doesn't break if the table's structure changes later.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="I'm building a task management project. How do you inspect recent commits in git?",
        response="""```
git log
```

This shows your commit history, most recent first, with the full commit hash, author, date, and message for each one. For a quick scan, `git log --oneline` compresses each commit to a single line (short hash + message), which is usually more useful day-to-day. Two other flags worth knowing: `-n 5` limits it to the last 5 commits, and `--graph` draws the branch structure alongside the history, which helps when your history isn't a straight line.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="I'm building a small portfolio project. Write a function that returns only even numbers from a list.",
        response="""```python
def evens(numbers):
    return [n for n in numbers if n % 2 == 0]
```

This uses a list comprehension: it walks through `numbers`, and for each one keeps it only if `n % 2 == 0` — meaning dividing by 2 leaves no remainder, which is the definition of even. The comprehension is just a compact way to write a loop that builds a new list, and it's the idiomatic Python style for this kind of filtering rather than a manual for-loop with `.append()`.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm debugging a student project. How do you make a controlled text input in React?",
        response="""```jsx
const [name, setName] = useState("");

<input value={name} onChange={e => setName(e.target.value)} />
```

"Controlled" means React's state — not the DOM — is the source of truth for the input's value. Every keystroke fires `onChange`, which updates `name` in state, and the input's `value` is always set from that same state. That round-trip is what makes it "controlled": if you set `value` without `onChange`, the input becomes read-only, since nothing ever updates the state that `value` is reading from — that's the most common bug people hit here.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm building a small portfolio project. Write a function that checks whether a value exists in a list.",
        response="""```python
def contains(items, value):
    return value in items
```

The `in` operator does a membership check — it scans `items` until it finds a match or reaches the end. Worth knowing: for a list, this is O(n) — it can check every element in the worst case. If you're checking membership repeatedly against the same collection, converting it to a `set` first makes each check O(1) on average, which matters once the list gets large.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a database index?",
        response="""An index is an auxiliary data structure — commonly a B-tree — that lets the database find rows matching a condition without scanning the entire table. For example, an index on a `students.age` column lets a query like `WHERE age > 20` jump straight to the relevant rows instead of checking every row in the table.

The trade-off: indexes speed up reads but slow down writes, since every `INSERT` or `UPDATE` has to also update the index. They also take up storage. Because of that, indexes should be added based on your actual query patterns — indexing every column "just in case" usually costs more than it helps.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm practicing programming for a university assignment. Write a function that removes falsy values from an array.",
        response="""```javascript
function compact(array) {
    return array.filter(Boolean);
}
```

`Boolean` used this way acts as the filter's test function — for each element, `filter` keeps it only if `Boolean(element)` is `true`. In JavaScript, the "falsy" values are `false`, `0`, `""` (empty string), `null`, `undefined`, and `NaN` — everything else, including `"0"` (a non-empty string) and empty arrays/objects, is truthy and gets kept.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm building a small portfolio project. Write a function that returns the length of a string.",
        response="""```python
def length(text):
    return len(text)
```

`len()` is a built-in that works on strings, lists, and other collections because they each implement a `__len__` method internally — `len(text)` is really calling `text.__len__()` behind the scenes. Wrapping it in your own function like this is mostly useful if you want a consistent name across your codebase, or plan to add extra logic (like handling `None`) later.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="I'm practicing programming for a university assignment. How do you center items using Flexbox?",
        response="""```css
.container {
    display: flex;
    justify-content: center;
    align-items: center;
}
```

`display: flex` turns on flexbox layout for the container's direct children. From there, `justify-content` controls alignment along the main axis (horizontal, by default) and `align-items` controls the cross axis (vertical, by default) — setting both to `center` centers content in both directions. If you rotate the layout with `flex-direction: column`, the two axes swap, so `justify-content` then controls vertical alignment instead.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What does SELECT do in SQL?",
        response="""`SELECT` is the core statement for reading data from a table:

```sql
SELECT name, email
FROM students;
```

This returns the `name` and `email` columns for every row in `students`. You can list specific columns like this, or use `SELECT *` to get every column — though listing exact columns is usually better practice, since it's clearer what the query actually needs and doesn't break if the table's structure changes later.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="I'm building a task management project. How do you inspect recent commits in git?",
        response="""```
git log
```

This shows your commit history, most recent first, with the full commit hash, author, date, and message for each one. For a quick scan, `git log --oneline` compresses each commit to a single line (short hash + message), which is usually more useful day-to-day. Two other flags worth knowing: `-n 5` limits it to the last 5 commits, and `--graph` draws the branch structure alongside the history, which helps when your history isn't a straight line.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm practicing programming for a university assignment. Write a query that returns students older than 20.",
        response="""```sql
SELECT * FROM students WHERE age > 20;
```

The `WHERE` clause filters rows *before* they're returned — only rows where `age > 20` evaluates to true make it into the result. This is different from filtering in application code after fetching everything, which would mean pulling every row over the network first and discarding most of them — `WHERE` lets the database do that filtering, which is far more efficient for large tables.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="I'm building a blogging project. Write a query that counts students in each department.",
        response="""```sql
SELECT department, COUNT(*) FROM students GROUP BY department;
```

`GROUP BY department` collapses all rows into one group per distinct department value. `COUNT(*)` then counts how many rows fall into each group. Without `GROUP BY`, `COUNT(*)` would just return one number for the entire table — the grouping is what makes it "per department" instead of an overall total.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is an HTTP GET request?",
        response="""`GET` is the HTTP method used to retrieve a resource — like fetching a webpage or an API record — without changing anything on the server. It's meant to be "safe": calling it once or a hundred times should leave the server in the same state.

Because of that, `GET` shouldn't be used to trigger side effects like creating a record or charging a payment — that's what `POST`, `PUT`, or `DELETE` are for. This matters practically too: browsers and proxies can cache `GET` requests and retry them automatically, which would be dangerous if a `GET` actually changed data.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="I'm building a help-desk project. Write a function that counts the occurrences of a value in a list.",
        response="""```python
def count_occurrences(items, value):
    return items.count(value)
```

`.count()` is fine for checking one value. But if you need counts for *many* different values from the same list, calling `.count()` separately for each one re-scans the whole list every time — better to build a frequency dictionary once:

```python
from collections import Counter
counts = Counter(items)  # counts[value] gives you the count for any value
```

`Counter` scans the list a single time and gives you O(1) lookups afterward, instead of O(n) per `.count()` call.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm building a task management project. Write a function that returns the names from an array of user objects.",
        response="""```javascript
const names = users.map(user => user.name);
```

`.map()` runs the arrow function once for every element in `users` and collects the results into a *new* array — the original `users` array is left unchanged. Here, the function just extracts `user.name` from each object, so `names` ends up as a plain array of strings, same length and order as `users`.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I'm building a sports statistics project. How do you create two equal Grid columns in CSS?",
        response="""```css
.container {
    display: grid;
    grid-template-columns: 1fr 1fr;
}
```

`display: grid` turns the container into a grid layout. `grid-template-columns` defines the column structure — `1fr 1fr` means two columns, each taking one "fraction" of the available space, so they end up equal width. This is generally cleaner than the older float or inline-block approaches, since the columns automatically adjust if the container resizes, without needing explicit width percentages.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="""Why does this code fail?

```javascript
const user = null;
console.log(user.name);
```""",
        response="""It throws `TypeError: Cannot read properties of null (reading 'name')`. `null` represents "no object here," so it has no properties at all — there's nothing for `.name` to access.

If `user` might legitimately be missing sometimes, optional chaining handles it safely:
```javascript
console.log(user?.name); // logs `undefined` instead of throwing
```
`?.` checks whether the value before it is `null`/`undefined` before trying to access the property, and short-circuits to `undefined` if so, instead of crashing.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is Git?",
        response="""Git is a distributed version control system — it tracks changes to your files over time, so you can see history, undo mistakes, and work on different features in parallel without them interfering with each other.

"Distributed" is the key detail: every contributor has a full copy of the project's history on their own machine, not just a pointer to a central server. That's why you can commit, branch, and view history offline, and only need a network connection when actually syncing with others via `push`/`pull`.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="I am debugging a student project. Implement binary search for a sorted list.",
        response="""```python
def binary_search(sorted_list, target):
    left, right = 0, len(sorted_list) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_list[mid] == target:
            return mid
        elif sorted_list[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1  # not found
```

The idea: instead of checking every element, you keep a shrinking window (`left` to `right`) and always check its middle. If the middle value is too small, the target must be in the right half, so you discard the left half — and vice versa. Each step cuts the remaining search space roughly in half, which is why this runs in O(log n) instead of O(n) for a plain linear scan. It only works because the list is sorted — that's what guarantees "too small" means "must be to the right." """,
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="I am learning this concept for an exam. How do you create a commit in Git?",
        response="""```
git add <files>
git commit -m "Describe the change"
```

Two steps because Git separates "what I might commit" from "what I'm committing now." `git add` moves your chosen changes into the staging area — a middle ground between your working files and history. `git commit` then takes whatever's staged and permanently records it as a new point in history, with the message explaining what changed and why. This separation is useful because it lets you stage only some of your changes, leaving unrelated edits out of a given commit.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="I am practicing programming for a university assignment. How do you create a link to an About page?",
        response="""```html
<a href="/about">About</a>
```

The `<a>` (anchor) tag creates a clickable link, and `href` sets where it goes. `/about` is a relative path starting from your site's root — it'll work regardless of which page the link appears on. If you instead wrote `about.html` (no leading slash), it would be relative to the *current* page's location, which can break if the page moves to a different folder — using a root-relative path like `/about` avoids that problem.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a heap?",
        response="""A heap is a tree-based structure that keeps a specific ordering rule between parents and children — in a **min-heap**, every parent is less than or equal to its children, so the smallest element is always at the root. A **max-heap** works the other way, keeping the largest element on top.

Heaps are the standard structure behind priority queues, since they let you find the smallest (or largest) item in O(1) and remove it in O(log n) — much faster than scanning a plain list every time. In Python, the built-in `heapq` module implements a min-heap on top of a regular list, which is the common way to use one in practice rather than building the tree structure by hand.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="I'm building a small portfolio project. Write a function that checks whether an array is empty.",
        response="""```javascript
function isEmpty(array) {
    return array.length === 0;
}
```

An array's `.length` property always reflects its current element count, so checking it against `0` is the direct, readable way to test emptiness. You'll sometimes see `!array.length` used as a shorthand for the same check — it works because `0` is falsy in JavaScript — but spelling out `=== 0` is usually clearer to read, especially for anyone newer to the language.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="Why is `WHERE age = NULL` incorrect for checking SQL nulls?",
        response="""```sql
SELECT * FROM students WHERE age IS NULL;
```

In SQL, `NULL` means "unknown," not "empty" or "zero" — and comparing anything to an unknown value, including `NULL = NULL`, itself produces an unknown result rather than `true`. That's why `WHERE age = NULL` silently matches nothing, with no error to warn you. `IS NULL` (and `IS NOT NULL`) are special operators built specifically to test for this "unknown" state, which regular comparison operators can't do.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a database transaction?",
        response="""A transaction groups multiple database operations into a single all-or-nothing unit. The classic example is a bank transfer: subtracting money from one account and adding it to another are two separate operations, but they need to succeed or fail *together* — if the system crashed after the subtraction but before the addition, money would simply vanish.

Wrapping both operations in a transaction guarantees that either both complete, or neither does (the transaction "rolls back"). This is the "atomicity" part of what's commonly called ACID transactions — a set of guarantees (atomicity, consistency, isolation, durability) that most relational databases provide for grouped operations like this.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do you print a message in Python?",
        response="""```python
print("Hello, Yaude AI!")
```

`print()` writes whatever you pass it to standard output — normally your terminal. You can pass multiple values separated by commas, and `print()` will join them with a space automatically:
```python
name = "Omol"
print("Hello,", name)  # Hello, Omol
```""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a queue?",
        response="""A queue is a first-in, first-out (FIFO) structure — the first item added is the first one removed, the same way a real line at a shop works: whoever joined first gets served first.

This is different from a stack, which is last-in, first-out. In Python, `collections.deque` is the standard way to implement a queue efficiently — `.append()` to add to the back, `.popleft()` to remove from the front, both O(1). Using a plain list's `.pop(0)` for this works but is O(n), since every remaining element has to shift over each time.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a Python virtual environment, and how do you create one?",
        response="""```
python -m venv venv
```

A virtual environment is an isolated space for a project's installed packages, separate from your system-wide Python installation. Without one, installing a package for one project can silently change the version another project relies on — a real, common source of bugs. Creating one with the command above makes a `venv/` folder; activating it (`.\\venv\\Scripts\\Activate.ps1` on Windows, `source venv/bin/activate` on Mac/Linux) then makes `pip install` affect only that project, not your whole system.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a LEFT JOIN in SQL?",
        response="""```sql
SELECT students.name, enrollments.course
FROM students
LEFT JOIN enrollments ON students.id = enrollments.student_id;
```

A `LEFT JOIN` keeps *every* row from the left table (`students`), and attaches matching rows from the right table (`enrollments`) wherever a match exists. If a student has no enrollments, they still appear in the results — the `enrollments.course` column just comes back `NULL` for them. This is different from a plain `JOIN` (inner join), which would drop that student entirely since there's no match to pair them with.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do you read user input in Python?",
        response="""```python
name = input("Enter your name: ")
print("Hello,", name)
```

`input()` displays the prompt, waits for the user to type something and press Enter, then returns exactly what they typed — always as a string, even if they type a number. That last part trips people up: if you need a number, you have to convert it explicitly:
```python
age = int(input("Enter your age: "))
```
Skipping the `int()` conversion and trying to do math on the raw input directly is a very common source of `TypeError`.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What does `git status` show?",
        response="""```
git status
```

It reports the current state of your working directory compared to your last commit: which files you've modified but haven't staged, which are staged and ready to commit, and which are new/untracked entirely. It's usually the first command worth running before `git add` or `git commit` — it tells you exactly what's about to happen before you commit to it, which matters since committing the wrong files is an easy mistake to make otherwise.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="What is Flexbox?",
        response="""Flexbox is a one-dimensional CSS layout system — it arranges items along a single axis (a row or a column) and gives you tools to align, space, and reorder them along that axis.

```css
.container {
    display: flex;
    justify-content: space-between;
}
```

CSS Grid, by contrast, handles two dimensions at once (rows and columns together), which makes it a better fit for full page layouts. A common rule of thumb: reach for Flexbox when arranging items in a single row or column (like a navbar or a card's contents), and reach for Grid when you need to control both rows and columns simultaneously.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is the difference between a syntax error and a logic error?",
        response="""A syntax error breaks the rules of the language itself — the code can't even run:
```python
def greet(
    print("hi")
```
That's missing a closing parenthesis, so Python refuses to parse it at all.

A logic error is different and sneakier: the code runs without complaint, but produces the wrong result:
```python
def add(a, b):
    return a - b  # should be a + b
```
This runs fine and returns a number — just the wrong one. Logic errors are usually harder to find precisely because nothing crashes to point you at them; you have to notice the output is wrong and work backward.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a custom Hook in React?",
        response="""A custom Hook is just a regular JavaScript function, conventionally named starting with `use`, that calls other React Hooks inside it — letting you package up reusable stateful logic instead of copy-pasting it across components.

```javascript
function useToggle(initial = false) {
    const [value, setValue] = useState(initial);
    const toggle = () => setValue(v => !v);
    return [value, toggle];
}
```

Any component can now call `const [isOpen, toggleOpen] = useToggle();` and get the same open/close behavior without redefining it every time. The `use` prefix isn't just convention for readability — React's linting rules use it to enforce the Rules of Hooks (like not calling Hooks conditionally) on your custom Hook too.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="I am building an employee management project. How do you render a list in React?",
        response="""```jsx
{items.map(item => <li key={item.id}>{item.name}</li>)}
```

`.map()` transforms your data array into an array of JSX elements, one per item. The `key` prop matters more than it looks — React uses it to track which list items changed, were added, or were removed between renders, so it can update the DOM efficiently instead of re-rendering the whole list. Using something stable like `item.id` is important; using the array index as a key can cause subtle bugs if items get reordered or removed, since React would then associate the wrong key with the wrong item.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is linear search?",
        response="""```python
def linear_search(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1
```

Linear search checks every element one at a time, in order, until it finds a match or reaches the end. Its worst case is O(n) — if the target is the last element, or isn't there at all, you end up checking everything. That's slower than binary search's O(log n), but linear search has one real advantage: it works on *any* list, sorted or not, while binary search only works on sorted data.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What does `map()` do in JavaScript?",
        response="""```javascript
const numbers = [1, 2, 3];
const doubled = numbers.map(n => n * 2);
// doubled is [2, 4, 6]
```

`map()` runs your function once for every element and collects the return values into a brand new array — the original `numbers` array is left completely unchanged. This matters: `map()` is for *transforming* data into a new shape, not for side effects like logging. If you're not using the returned array, `map()` is usually the wrong tool — `forEach()` is the more honest choice for "just do something with each item." """,
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a foreign key in SQL?",
        response="""A foreign key is a column (or set of columns) in one table whose values must match values in another table's key column — it's how relational databases represent connections between tables.

```sql
CREATE TABLE enrollments (
    id INT PRIMARY KEY,
    student_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

Here, `enrollments.student_id` is a foreign key referencing `students.id`. The database enforces this: you can't insert an enrollment pointing at a student_id that doesn't actually exist, which is what "referential integrity" means in practice — it stops your data from silently pointing at nothing.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a Promise in JavaScript?",
        response="""A Promise represents a value that isn't ready yet, but will be — the result of something asynchronous, like a network request. It's always in one of three states: pending (still waiting), fulfilled (succeeded), or rejected (failed).

```javascript
fetch("/api/students")
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error("Failed:", error));
```

`.then()` runs once the Promise fulfills, `.catch()` runs if it rejects. The newer `async`/`await` syntax does the same thing with more readable, synchronous-looking code:
```javascript
try {
    const response = await fetch("/api/students");
    const data = await response.json();
} catch (error) {
    console.error("Failed:", error);
}
```""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a variable in programming?",
        response="""A variable is a named reference to a value stored in memory — a label you can use instead of the raw value itself.

```python
age = 22
print(age)  # 22
age = 23    # the label now points to a new value
```

The exact rules differ by language: Python lets you reassign a variable to a different type entirely (`age = "twenty-two"` would be legal), while statically-typed languages like Java require you to declare a variable's type upfront and stick to it. What's universal is the core idea — a variable is a name standing in for a value, so your code stays readable instead of scattered with raw numbers and strings everywhere.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is Big O notation?",
        response="""Big O describes how an algorithm's running time (or memory use) grows as the input gets larger — it's about the growth trend, not an exact stopwatch measurement.

A few common ones, roughly fastest to slowest:
- `O(1)` — constant time, like accessing a list by index; doesn't matter how big the list is.
- `O(log n)` — like binary search; each step cuts the remaining work roughly in half.
- `O(n)` — linear; like scanning every item once, such as linear search.
- `O(n\u00b2)` — quadratic; like comparing every item to every other item, common in naive nested-loop solutions.

Why it matters practically: an `O(n\u00b2)` solution might feel fine on 10 items and become unusably slow on 100,000 — Big O is how you predict that before it happens, rather than finding out the hard way in production.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a commit in Git?",
        response="""A commit is a saved snapshot of your staged changes, permanently recorded in your project's history along with metadata: who made it, when, and a message describing what changed.

```
git commit -m "Fix login validation bug"
```

Each commit also stores a reference to the commit before it, which is what makes Git's history a connected chain rather than a flat list of unrelated saves — that chain is what lets you view history, revert to an earlier point, or see exactly which commit introduced a bug.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a function in programming?",
        response="""A function is a named, reusable block of code that performs a specific task — you define it once and can call it as many times as you need, instead of repeating the same code everywhere.

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Omol"))  # Hello, Omol!
```

`name` here is a parameter — a placeholder for whatever value gets passed in when the function is called. Functions can optionally return a result (like this one does), or just perform an action without returning anything.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is an INNER JOIN in SQL?",
        response="""```sql
SELECT s.name, e.course
FROM students AS s
INNER JOIN enrollments AS e
  ON s.id = e.student_id;
```

An `INNER JOIN` only returns rows where the join condition matches in *both* tables — a student with no enrollments simply won't appear in the results at all. This is the key difference from a `LEFT JOIN`, which keeps every row from the left table regardless of whether a match exists, filling in `NULL` where there isn't one. Use `INNER JOIN` when you only care about rows that genuinely have a match on both sides.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is idempotency in an API?",
        response="""An operation is idempotent when calling it once has the same effect as calling it many times. This matters a lot for retries: if a request times out and you're not sure whether it actually went through, it's only safe to automatically retry if the operation is idempotent.

`PUT /users/5 {"name": "Omol"}` is idempotent — setting the name to "Omol" five times leaves the same end result as setting it once. `POST /orders` typically is *not* idempotent — retrying it naively could create five separate orders instead of one. This is exactly why `PUT` and `POST` have different conventional meanings in REST APIs: `PUT` is meant for idempotent updates, `POST` for actions that may have side effects each time they run.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What does 'lifting state up' mean in React?",
        response="""It means moving a piece of state from a child component up to the closest parent that all the components needing it have in common — then passing the value (and a way to update it) back down as props.

```jsx
function Parent() {
    const [count, setCount] = useState(0);
    return (
        <>
            <Display count={count} />
            <Button onClick={() => setCount(count + 1)} />
        </>
    );
}
```

Here, `count` lives in `Parent`, not in `Display` or `Button` individually — because both components need access to the same value, it has to live somewhere they both can reach. Without lifting it up, `Display` and `Button` would each have their own separate, disconnected copy of the state, and updating one wouldn't affect the other.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="What is an algorithm?",
        response="""An algorithm is a finite, clearly-defined sequence of steps for solving a problem or producing a result. "Finite" matters — a real algorithm has to eventually stop, not run forever.

A simple example: steps for finding the largest number in a list are an algorithm even before you write any code — "start with the first number as your current largest, check each remaining number, update your current largest whenever you find something bigger, stop at the end." Code is just one way of expressing an algorithm precisely enough for a computer to follow it; the algorithm itself is the underlying idea, independent of any specific programming language.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a closure in JavaScript?",
        response="""```javascript
function counter() {
    let count = 0;
    return () => ++count;
}
const next = counter();
console.log(next()); // 1
console.log(next()); // 2
```

A closure happens when a function "remembers" the variables from where it was created, even after that outer function has finished running. Here, the inner arrow function keeps access to `count` even though `counter()` already returned — that's the closure.

What makes this genuinely useful: each call to `counter()` creates a *separate* `count`, fully isolated from any other. If you called `counter()` again to make a second `next`, it would have its own independent counter starting back at 0, completely unaffected by the first one.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the purpose of the `alt` attribute on an image in HTML?",
        response="""```html
<img src="chart.png" alt="Bar chart showing enrollment by department">
```

`alt` describes what the image shows, in words. Screen readers read it aloud for users who can't see the image, and browsers display it if the image fails to load — so it's genuinely functional, not just decoration for accessibility checkers.

For purely decorative images that carry no real information (like a background flourish), use an empty `alt=""` — this explicitly tells screen readers to skip it, rather than reading a filename or leaving the image entirely unlabeled, both of which are worse than an intentional empty value.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a controlled input, and why would you choose it over an uncontrolled one?",
        response="""A controlled input's value lives in React state — React is the single source of truth, and the DOM input just displays whatever state currently holds. An uncontrolled input is the opposite: the DOM manages its own value internally, and you only reach in to read it when you need to (usually via a ref), rather than tracking every keystroke in state.

Controlled inputs are the more common default because they make validation, conditional disabling, and syncing multiple fields straightforward — the current value is always right there in state, ready to check. Uncontrolled inputs are lighter-weight and can be worth it for very simple forms, or when integrating with non-React code that expects to manage the DOM itself, since you're not paying the cost of a state update on every keystroke.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do you find the largest value in a list in Python?",
        response="""```python
numbers = [7, 2, 11, 4]
print(max(numbers))  # 11
```

`max()` is a built-in that works on any list of comparable values — numbers, strings (alphabetically), even tuples. One thing worth knowing: `max()` raises a `ValueError` on an empty list, since there's no sensible "largest" of nothing. If the list might be empty, guard for it:
```python
print(max(numbers, default=None))
```
`default` gives you a fallback value instead of crashing.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is `async/await` in JavaScript?",
        response="""```javascript
async function getUser() {
    const response = await fetch("/api/user");
    return response.json();
}
```

`async/await` is syntax that makes asynchronous code read like ordinary, top-to-bottom synchronous code, even though it's still Promise-based underneath. Marking a function `async` means it always returns a Promise; `await` pauses execution *inside that function* until the awaited Promise settles, without blocking the rest of your program.

It's mostly a readability improvement over chaining `.then()` calls directly — the underlying behavior (and error handling with `try`/`catch`) is the same, just easier to follow for multi-step asynchronous logic.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What does HTTP status 500 mean?",
        response="""500 means the server hit an unexpected problem while handling your request — and critically, it's the server's fault, not something wrong with what you sent.

This is worth contrasting with the 400s: a 404 means the resource wasn't found, and a 400 means the request itself was malformed — both point back at the client. A 500 means the server crashed or errored internally while trying to process an otherwise valid request, which is why 500 errors usually mean checking server logs, not double-checking your request.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this function return None?

```python
def add(a, b):
    a + b
```""",
        response="""The function computes `a + b`, but never sends the result back to whoever called it — there's no `return`. In Python, if a function runs to completion without hitting a `return` statement, it implicitly returns `None`.

Fixed version:
```python
def add(a, b):
    return a + b
```
Now `add(2, 3)` actually gives you `5` back, instead of silently discarding the calculation and handing back `None`. This is a very common early mistake — the function *looks* like it does the math, and it does, but the result just never leaves the function.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a loop in programming?",
        response="""A loop repeats a block of code, either a fixed number of times or until some condition is no longer true.

```python
for i in range(3):
    print(i)  # 0, 1, 2

n = 0
while n < 3:
    print(n)
    n += 1  # 0, 1, 2 -- same result, different style
```

`for` loops are the natural choice when you know how many times you want to repeat (or you're iterating over a known collection). `while` loops fit better when you're repeating until some condition changes, and you can't say in advance exactly how many iterations that'll take.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is the CSS box model?",
        response="""Every element in CSS is a rectangular box made of four layers, from the inside out: **content** (the actual text or image), **padding** (space inside the border, around the content), **border** (the edge itself), and **margin** (space outside the border, separating this element from others).

```css
.card {
    padding: 16px;
    border: 1px solid #ccc;
    margin: 8px;
}
```

The common confusion is padding versus margin: padding pushes the border *outward* from the content (so it's still "inside" the element's visible box), while margin pushes other elements *away* from this one entirely. Mixing these up is one of the most common sources of "why is there a gap I didn't ask for" bugs in CSS.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is the difference between `==` and `===` in JavaScript?",
        response="""```javascript
0 == false   // true  -- coerced, both become comparable
0 === false  // false -- different types, no coercion
```

`==` allows JavaScript to convert the two values to a common type before comparing them, which can produce surprising results like the first line above. `===` skips that conversion entirely — both the value *and* the type have to match, so `0 === false` is false because a number and a boolean are never equal under strict comparison, no matter their values.

Modern JavaScript style strongly prefers `===` almost everywhere, specifically to avoid the surprises `==`'s coercion rules can produce — it's rarely worth the ambiguity.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="Why does `a = b` not copy a list in Python?",
        response="""```python
b = [1, 2]
a = b
a.append(3)
print(b)  # [1, 2, 3] -- b changed too!
```

`a = b` doesn't create a new list — it makes `a` point to the *same* list object that `b` already points to. Lists are mutable, so modifying it through `a` (via `.append()`) is modifying the one and only list both names refer to; `b` sees the change because there was never a second list to begin with.

If you actually want an independent copy:
```python
a = b.copy()
# or: a = list(b)
# or: a = b[:]
```
Any of these creates a genuinely new list with the same starting contents, so changes to `a` no longer affect `b`.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a stack data structure?",
        response="""A stack is last-in, first-out (LIFO) — the most recently added item is the first one removed, like a physical stack of plates: you take from the top, not the bottom.

```python
stack = []
stack.append(1)
stack.append(2)
stack.append(3)
stack.pop()  # removes and returns 3, the most recent addition
```

Python's plain list works as a stack directly via `.append()` (push) and `.pop()` (pop), both O(1) when operating on the end of the list. A very concrete real-world example: your browser's back button and an editor's undo feature are both stacks — the most recent thing you did is the first thing undone.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is debugging?",
        response="""Debugging is the process of finding, understanding, and fixing a defect in a program. A useful, repeatable workflow: reproduce the problem reliably first, gather evidence (error messages, logs, print statements), form a hypothesis about the cause, make one targeted change to test that hypothesis, and verify the fix actually resolves it before moving on.

The "reproduce it reliably first" step is easy to skip but genuinely important — chasing a bug you can't consistently trigger usually wastes far more time than the few extra minutes it takes to first pin down exactly when and how it happens.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a primary key in a database table?",
        response="""```sql
CREATE TABLE students (
    id INT PRIMARY KEY,
    name TEXT
);
```

A primary key uniquely identifies each row in a table — no two rows can share the same primary key value, and it can't be `NULL`. Here, `id` is what the database uses to distinguish one student from another, even if two students happen to share the exact same name.

Primary keys matter beyond just uniqueness: they're what foreign keys in *other* tables reference to represent relationships, and databases typically build an index on the primary key automatically, making lookups by it fast.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="What is state in React?",
        response="""```jsx
function Counter() {
    const [count, setCount] = useState(0);
    return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

State is data a component manages itself, that can change over its lifetime — here, `count`. The important part is *how* it changes: calling `setCount()` doesn't just update the value, it tells React "re-render this component, its output may now be different." Changing a plain variable wouldn't do that; only updates through React's state mechanism (`useState`'s setter) trigger a re-render.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a generator in Python?",
        response="""```python
def count_up_to(n):
    for i in range(1, n + 1):
        yield i

for num in count_up_to(3):
    print(num)  # 1, 2, 3
```

A generator produces values one at a time, on demand, instead of building the entire result in memory upfront. `yield` is what makes this a generator rather than a normal function — each time it's asked for the next value, execution pauses right at the `yield` and resumes there next time, rather than starting over.

This matters for large or infinite sequences: `count_up_to(10_000_000)` doesn't build a 10-million-item list in memory — it just produces the next number each time you ask, using barely any memory regardless of how far you iterate.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What actually goes wrong if you skip keys when rendering a list in React?",
        response="""```jsx
{items.map(item => <li>{item.name}</li>)}  // no key -- React will warn about this
```

Without a stable key, React falls back to comparing list items by their position in the array. If you then reorder, insert, or remove an item, React can misattribute which DOM element corresponds to which data — leading to a real, visible bug: input focus jumping to the wrong row, or a component's internal state appearing to attach to the wrong item after a reorder.

Using `item.id` (something that stays the same for a given piece of data no matter where it moves in the list) instead of the array index avoids this, since React can then correctly track "this is the same item, just in a new position" rather than assuming position alone means identity.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What does `WHERE` do in a SQL query with a different example than filtering by age?",
        response="""```sql
SELECT * FROM students WHERE department = 'Computer Science';
```

Same mechanism as filtering numerically: `WHERE` evaluates its condition against each row and only returns the ones where it's true — here, rows whose `department` column exactly matches the given string. It works the same way regardless of the column's data type; the comparison operator just changes (`=` for exact text match here, versus `>=` for numeric ranges).""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is recursion, using a simple example other than factorial?",
        response="""```python
def sum_list(numbers):
    if not numbers:          # base case: empty list sums to 0
        return 0
    return numbers[0] + sum_list(numbers[1:])
```

Recursion means a function calls itself to solve a smaller version of the same problem — here, "sum a list" reduces to "add the first number, then sum the rest of the list," which is the same problem, just one element shorter each time. Every correct recursive function needs a base case (here, an empty list) that stops the recursion without calling itself again — without one, it would call itself forever until Python's recursion limit is hit.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is authorization in the context of an API?",
        response="""Authorization determines what an already-identified user or service is *allowed to do* — which resources they can access, which actions they can perform. It's a distinct step from authentication, and always comes after it: you first confirm who someone is, then separately check what they're permitted to do.

A concrete example: a logged-in student and a logged-in professor might both be successfully authenticated, but authorization is what decides only the professor can view all students' grades, while the student can only view their own.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is authentication in the context of an API?",
        response="""Authentication is the process of verifying that someone actually is who they claim to be — logging in with a password, validating a token, or checking an API key are all forms of authentication.

It answers only one question: "who is this?" — it says nothing about what that verified identity is allowed to do once confirmed. That second question is authorization's job, and the two are normally implemented as separate steps: authenticate first, then check authorization for the specific action being requested.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a conditional statement?",
        response="""```python
age = 20
if age >= 18:
    print("Adult")
else:
    print("Minor")
```

A conditional lets your program take different paths depending on whether some condition is true or false — here, `age >= 18`. Without conditionals, a program would always do exactly the same thing regardless of its input, which makes them one of the most fundamental tools for writing anything that actually responds to different situations. Most languages also offer `switch` or `match` for choosing between many specific values cleanly, rather than a long chain of `if`/`elif`.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a merge conflict in Git?",
        response="""A merge conflict happens when Git can't automatically combine changes from two branches because they touched the same lines in incompatible ways — Git doesn't know which version you actually want, so it stops and asks you.

Git marks the conflicting section directly in the file:
```
<<<<<<< HEAD
your current branch's version
=======
the incoming branch's version
>>>>>>> other-branch
```
You edit the file to keep whichever version (or combination) is correct, remove the `<<<<<<<`/`=======`/`>>>>>>>` marker lines, then `git add` the resolved file and complete the commit. Conflicts aren't a sign something went wrong — they're Git correctly refusing to guess when it genuinely can't tell which change you want.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What are props in React, and how are they different from state?",
        response="""```jsx
function Welcome({ name }) {
    return <h1>Hello, {name}</h1>;
}
<Welcome name="Omol" />
```

Props are inputs a parent passes *into* a component — here, `name`. The receiving component should treat them as read-only: `Welcome` shouldn't try to reassign `name` itself. This is the key contrast with state: state is data a component owns and can change internally over time (like a counter), while props flow one-way, from parent to child, and only the parent controls when they change.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do you check whether a number is even in Python?",
        response="""```python
number = 14
if number % 2 == 0:
    print("Even")
else:
    print("Odd")
```

`%` is the remainder (modulo) operator — `number % 2` gives you what's left over after dividing by 2. For any even number, that remainder is always exactly 0, so checking `== 0` is a direct, reliable test for evenness. The same pattern works for checking divisibility by anything, not just 2 — `number % 3 == 0` checks divisibility by 3, and so on.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""What is wrong with this Python loop?

```python
numbers = [10, 20, 30]
for i in range(len(numbers) + 1):
    print(numbers[i])
```""",
        response="""It raises `IndexError: list index out of range` on the last iteration. `numbers` has 3 elements, at valid indexes 0, 1, and 2 — but `range(len(numbers) + 1)` produces 0, 1, 2, **3**, and index 3 doesn't exist.

Fix by dropping the `+ 1`:
```python
for i in range(len(numbers)):
    print(numbers[i])
```
Or better, since you don't actually need the index here, iterate directly:
```python
for number in numbers:
    print(number)
```
This second version is generally preferred when you don't need the index at all — it's shorter and can't hit this exact off-by-one mistake.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is dynamic programming?",
        response="""Dynamic programming solves problems that have overlapping subproblems by storing (caching) results instead of recomputing them every time.

Classic example: naive recursive Fibonacci recalculates `fib(2)` many times over as it works out `fib(10)`. Storing each result the first time it's computed avoids all that repeated work:
```python
def fib(n, cache={}):
    if n in cache:
        return cache[n]
    if n <= 1:
        return n
    cache[n] = fib(n - 1, cache) + fib(n - 2, cache)
    return cache[n]
```
This particular style (recursion plus a cache) is called memoization — the "top-down" approach. The alternative, "bottom-up" tabulation, builds the answer iteratively from the smallest subproblems up, without recursion at all. Both are dynamic programming; they just differ in direction.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a Git rebase?",
        response="""```
git rebase main
```

A rebase takes your branch's commits and reapplies them one by one on top of a new base commit — the practical effect is a cleaner, linear-looking history, instead of the branching-and-merging structure a regular merge would produce.

The real caution: rebase rewrites commit history, giving your commits new identities. That's fine for commits only you have, on a branch you haven't shared yet. But rewriting commits other people have already pulled and built on top of causes real problems for them when they next try to sync — as a rule, don't rebase commits that have already been pushed and shared, unless everyone involved knows and agrees to it.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do you use CSS Grid to lay out a page?",
        response="""```css
.page {
    display: grid;
    grid-template-columns: 200px 1fr;
    grid-template-rows: auto 1fr auto;
    gap: 16px;
}
```

This defines a two-column layout (a fixed 200px sidebar, and the rest of the space for content) crossed with three rows (a header that sizes to its content, a flexible middle area, and a footer that also sizes to its content). `gap` adds spacing between grid cells without needing manual margins on each item.

The real strength here versus Flexbox is controlling rows and columns *together* as one coordinated grid — Flexbox only manages a single row or column at a time, which is why Grid tends to be the better fit for whole-page layouts specifically.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is semantic HTML?",
        response="""```html
<header>...</header>
<nav>...</nav>
<main>
  <article>...</article>
</main>
<footer>...</footer>
```

Semantic HTML means choosing elements based on what they actually mean, not just how they look — `<nav>` for navigation, `<article>` for a self-contained piece of content, rather than generic `<div>`s for everything ("div soup").

This matters beyond style: screen readers use these elements to let users jump directly to "navigation" or "main content," and search engines use them to understand a page's structure. A page built entirely from unlabeled `<div>`s looks identical to a sighted user with CSS applied, but conveys none of that structural meaning to anyone or anything relying on the markup itself.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is the difference between `let` and `const` in JavaScript?",
        response="""```javascript
let score = 0;
score = 10;      // fine -- let allows reassignment

const name = "Omol";
name = "Andrew"; // TypeError -- const does not
```

Both are block-scoped (limited to the `{ }` they're declared in), which is itself an improvement over the older `var`. The real difference is reassignment: `let` allows it, `const` doesn't. Note that `const` only locks the *binding*, not the contents of an object or array — `const list = [1, 2]; list.push(3);` is perfectly legal, since you're not reassigning `list` itself, just mutating what it points to. Default to `const` unless you specifically know a variable needs to be reassigned later.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="Why is `Array.prototype.sort()` surprising when used on numbers?",
        response="""```javascript
[10, 2, 30].sort(); // [10, 2, 30] -- NOT sorted numerically!
```

By default, `sort()` converts elements to strings and compares them alphabetically — and alphabetically, "10" comes before "2" (since "1" < "2" as characters), which is why this looks broken to anyone expecting numeric order.

Fix it by providing your own comparator function:
```javascript
[10, 2, 30].sort((a, b) => a - b); // [2, 10, 30]
```
`(a, b) => a - b` tells `sort()` exactly how to compare two elements numerically — negative means `a` comes first, positive means `b` does. This is one of the most common "my code is silently wrong" traps in JavaScript specifically because it doesn't throw an error; it just quietly sorts incorrectly.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is binary search, conceptually, and what does it require?",
        response="""Binary search finds a target value in a sorted collection by repeatedly checking the middle element and discarding half the remaining search space each time, based on whether the target is smaller or larger than that middle value. This gives O(log n) time — dramatically faster than checking every element one by one (O(n)) once the collection gets large.

The one hard requirement: the data has to already be sorted. Binary search's whole logic depends on being able to say "if the middle is too small, the target must be somewhere to the right" — and that's only guaranteed to be true if the data is in order. Running binary search on unsorted data doesn't just run slower, it can give you completely wrong answers.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a React component?",
        response="""```jsx
function Welcome({ name }) {
    return <h1>Hello, {name}</h1>;
}
```

A component is a reusable, self-contained piece of UI — a function that takes some input (props) and returns what should appear on screen (JSX, which looks like HTML but is actually JavaScript). Components are the core building block of a React app: you build small ones like this `Welcome` component, then compose them together into larger ones, the same way you'd build a larger program out of smaller functions.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is responsive web design?",
        response="""Responsive design means a site adapts its layout to fit different screen sizes — a phone, a tablet, a desktop monitor — rather than looking correct on only one.

```css
.container {
    width: 100%;
    max-width: 1200px;
}

@media (max-width: 600px) {
    .sidebar { display: none; }
}
```

`max-width: 1200px` keeps content from stretching uncomfortably wide on large screens, while the `@media` query applies different rules specifically on narrow screens (like hiding a sidebar on mobile). Combined with relative sizing (`%`, `rem`) instead of fixed pixel widths everywhere, these techniques let one set of HTML and CSS genuinely work well across a wide range of devices, instead of needing a separate mobile-only version of the site.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What does HTTP status 404 mean?",
        response="""404 means the server couldn't find anything matching the resource you requested — the URL doesn't correspond to anything it knows about.

It's worth keeping straight against the other status codes already covered: 404 is about a missing resource, while a 500 means the server itself hit an internal error while trying to handle an otherwise valid request. If you're debugging an unexpected 404, the first thing to check is usually the URL itself — a typo in the path, or a route that doesn't actually exist on the server, are the most common causes.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )


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
