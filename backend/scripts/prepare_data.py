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

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This study investigates barriers to mobile banking adoption among rural households in three East African districts. Drawing on 420 household surveys, we find that network reliability concerns and unfamiliarity with digital transaction interfaces are stronger predictors of non-adoption than either income level or distance to the nearest bank branch, challenging the common assumption that mobile banking's main barrier is simply financial access.""",
        response="Researchers surveyed 420 rural households across three East African districts to understand why some people don't use mobile banking. They found that the biggest reasons weren't about money or distance to a bank -- it was more about people not trusting the network to work reliably, and not being comfortable using the digital interface itself.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"We evaluate the reliability and cost-effectiveness of solar microgrids as an alternative to diesel generators for powering rural health clinics in off-grid regions. Across 18 installed sites over two years, solar microgrids reduced average monthly energy costs by 61% while maintaining comparable uptime, though upfront installation costs remained a significant adoption barrier for under-resourced facilities.""",
        response="This study looked at 18 rural health clinics that switched from diesel generators to solar microgrids over two years. The clinics saved 61% on their monthly energy costs and had just as reliable power as before -- the main problem is that the upfront cost of installing solar power is still hard for many under-funded clinics to afford.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This paper examines learning continuity among secondary school students during extended internet connectivity disruptions. Using interview data from 32 students and 12 teachers, we identify SMS-based assignment distribution and offline downloadable content as the two coping strategies most associated with sustained student engagement, compared to schools relying solely on live video instruction.""",
        response="Researchers interviewed 32 students and 12 teachers about how schools kept students learning when the internet went down for extended periods. They found that schools using simple text-message assignments and content students could download ahead of time and use offline kept students more engaged than schools that depended entirely on live video classes.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"We assess the impact of community-managed borehole maintenance programs on water access reliability across 45 villages. Villages with locally trained maintenance technicians experienced 73% fewer multi-week service interruptions compared to villages relying on centralized government repair crews, suggesting that maintenance capacity, not initial infrastructure quality, is the primary determinant of long-term water access reliability.""",
        response="This study compared 45 villages to see what kept their water boreholes running reliably. Villages that trained their own local technicians to do repairs had 73% fewer long water outages than villages that waited for government repair crews to come from elsewhere -- suggesting that having someone nearby who can fix problems matters more than how good the original equipment was.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This study evaluates whether SMS-based prenatal health reminders improve clinic attendance among pregnant women in under-resourced districts. In a sample of 610 participants, women receiving weekly SMS reminders attended 34% more scheduled prenatal visits than the control group, with the effect strongest among first-time mothers.""",
        response="Researchers tested whether sending pregnant women a weekly text message reminder would help them attend their prenatal checkups. Among 610 women studied, those who got the reminders attended 34% more of their scheduled visits than women who didn't -- and the reminders helped first-time mothers the most.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"We examine whether SMS-delivered agricultural advisories affect crop yield outcomes among smallholder maize farmers. Farmers receiving planting-season and pest-warning SMS alerts over two growing seasons achieved 19% higher average yields than a control group receiving no advisories, with the largest gains observed among farmers who had no prior access to an agricultural extension officer.""",
        response="This study tested whether sending smallholder maize farmers text-message farming advice -- like when to plant and pest warnings -- actually helped their harvests. Over two growing seasons, farmers who got the advisory texts grew 19% more maize on average than farmers who didn't, and the benefit was biggest for farmers who'd never had access to an in-person agricultural advisor before.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="Help me write a thesis introduction paragraph about smallholder farmers' adoption of mobile agricultural advisory services. I want it to state the problem and why it matters.",
        response="""Here's a draft introduction paragraph:

"Despite growing mobile phone penetration across rural Africa, smallholder farmers' adoption of mobile agricultural advisory services remains inconsistent, with uptake varying significantly even among farmers facing similar access to network coverage. This gap matters because these services have demonstrated real potential to improve crop yields and reduce losses from pests and poor planting timing -- benefits that remain unrealized wherever adoption stalls. Understanding what actually drives or discourages adoption, beyond simple network availability, is essential for designing advisory programs that reach the farmers who could benefit most, rather than assuming access alone guarantees use."

This structure states the problem (inconsistent adoption despite phone access), explains why it matters (real, unrealized yield benefits), and sets up your research question (what actually drives adoption). Swap in your specific region or crop focus as needed.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How should I structure the literature review section of my thesis?",
        response="""A literature review isn't just a list of summaries -- it should build an argument for why your specific research is needed. A structure that works well for most theses:

1. **Group studies by theme or approach**, not chronologically one-by-one. If several papers examine the same underlying question from different angles, discuss them together.
2. **Move from broad to narrow.** Start with the general area of research, then progressively narrow toward your specific question.
3. **Synthesize, don't just summarize.** For each theme, note where studies agree, where they conflict, and what's still unclear -- this is what makes it a *review*, not a list of abstracts.
4. **End with the gap your research fills.** The final paragraph should make it explicit: here's what's known, here's what isn't, and here's how your study addresses that gap.

A common mistake is writing this section as "Study A found X. Study B found Y. Study C found Z." with no connective analysis between them -- that reads as a summary, not a review, and doesn't build toward your own contribution.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="Help me write a methodology paragraph for a study that surveyed 300 university students about internet access and combined it with follow-up interviews.",
        response="""Here's a draft methodology paragraph:

"This study employed a mixed-methods design combining quantitative and qualitative data. In the first phase, a structured survey was administered to 300 university students to capture patterns in internet access frequency, device type, and connectivity-related academic disruptions. In the second phase, semi-structured follow-up interviews were conducted with a purposively selected subset of 20 survey respondents to explore the specific circumstances and coping strategies behind the patterns identified in the survey data. This sequential design allowed the qualitative interviews to be grounded in and informed by quantitative findings, rather than treating the two data sources independently."

Notice the structure: state the overall design type first (mixed-methods), then walk through each phase in the order it happened, and end by explaining *why* you combined them this way -- reviewers specifically look for that justification, not just a description of what you did.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I turn a general interest in a topic into a specific, researchable research question?",
        response="""A broad interest like "mobile technology and education" isn't researchable as-is -- it's a topic area, not a question. Narrowing it usually means adding three things:

1. **A specific population or context** -- not "students" generally, but which students, where.
2. **A specific outcome you're measuring** -- not "does it help," but help with *what*, measured *how*.
3. **A relationship you're testing** -- between which two things, specifically.

Applying that to the broad topic above: "How does SMS-based assignment delivery affect secondary school students' assignment completion rates during internet outages in Central Equatoria State?" is researchable -- it names the population (secondary students in a specific state), the outcome (completion rates), and the relationship being tested (effect of SMS delivery during outages specifically). If you can't identify what data would actually answer your question, it's usually a sign the question is still too broad.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="Help me write a 150-200 word abstract for a completed study on solar microgrid adoption in rural health clinics.",
        response="""A strong abstract at this length typically has five short parts, one to two sentences each: the problem, your approach, your key finding, why it matters, and (optionally) a limitation. Here's a draft:

"Rural health clinics in off-grid regions often rely on costly, unreliable diesel generators for power. This study evaluated solar microgrids as an alternative across 18 clinics over two years, tracking energy costs and uptime compared to their previous diesel systems. Clinics using solar microgrids reduced average monthly energy costs by 61% while maintaining comparable power reliability. These findings suggest solar microgrids are a financially viable alternative for off-grid health infrastructure, though high upfront installation costs remain a barrier for under-resourced facilities without external funding support. Future research should examine financing models that address this adoption barrier directly."

Notice it front-loads the problem before your own contribution, states one concrete number rather than vague claims, and closes honestly with a limitation rather than overselling the result -- all standard expectations for an academic abstract.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this loop never end?

```python
def countdown(n):
    while n > 0:
        print(n)
    return "done"
```""",
        response="""`n` is never actually changed inside the loop, so `n > 0` stays true forever once it starts true -- the loop has no way to reach its own exit condition.

Fixed version:
```python
def countdown(n):
    while n > 0:
        print(n)
        n -= 1
    return "done"
```
Adding `n -= 1` decreases `n` by 1 on every iteration, so it eventually reaches 0 and the loop naturally stops. This is one of the most common infinite-loop causes: the condition being checked never actually gets updated inside the body of the loop.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""This is supposed to add 5 and the string version of a number, but gives a strange result. Why?

```javascript
let total = 5 + "3";
console.log(total); // "53"
```""",
        response="""`+` in JavaScript does double duty: it's both numeric addition and string concatenation, and it picks based on the types involved. Since `"3"` is a string, JavaScript converts `5` to a string too and *concatenates* them instead of adding numbers -- so `5 + "3"` becomes `"53"`, not `8`.

If you actually want numeric addition, convert the string first:
```javascript
let total = 5 + Number("3"); // 8
// or: 5 + parseInt("3", 10);
```
This is a common source of quiet bugs specifically because it doesn't throw an error -- it just silently produces a string instead of a number, and the mistake only shows up later when something expects a number and gets `"53"` instead.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function sometimes skip the last valid item?

```python
def find_last_positive(numbers):
    for i in range(len(numbers) - 1):
        if numbers[i] > 0:
            last = numbers[i]
    return last
```""",
        response="""`range(len(numbers) - 1)` stops one index short of the end of the list, so the loop never checks the actual last element -- if that last element happens to be the only positive number, or the true last positive one, it gets missed entirely.

Fixed version:
```python
def find_last_positive(numbers):
    last = None
    for i in range(len(numbers)):
        if numbers[i] > 0:
            last = numbers[i]
    return last
```
Two changes: `range(len(numbers))` now checks every index including the last one, and `last` is initialized to `None` upfront so the function doesn't crash with an "undefined variable" error if the list contains no positive numbers at all.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a discussion section that actually connects my results back to existing research, instead of just restating my findings?",
        response="""A discussion section that just repeats your results ("we found X, we found Y") is one of the most common weaknesses in student research writing. A structure that avoids this:

1. **Restate your key finding briefly** -- one sentence, not a re-summary of your whole results section.
2. **Compare it directly to specific prior studies.** Does it agree with what others found? Contradict it? Extend it to a new context? Name the studies and say explicitly how your result relates to theirs.
3. **Explain a plausible reason for any disagreement**, if your results conflict with prior work -- different population, different method, different time period.
4. **State the practical or theoretical implication** -- so what? Who should care about this finding, and why?
5. **Acknowledge a real limitation**, briefly and honestly, rather than only in a separate limitations section.

The difference between a weak and strong discussion section usually comes down to step 2: weak ones describe results in isolation, while strong ones actively argue for where this study fits into a larger, ongoing conversation in the field.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This study evaluates the effect of a six-week digital literacy training program on employment outcomes among unemployed youth in urban centers. Comparing 280 program graduates to a matched control group six months post-training, graduates were 2.3 times more likely to be employed, with the strongest effect observed among participants who completed the program's job-application component specifically, rather than the general computer skills modules alone.""",
        response="Researchers followed 280 unemployed young people who completed a six-week digital literacy course and compared them to similar people who didn't. Six months later, the graduates were more than twice as likely to have found a job -- and the part of the training that mattered most wasn't general computer skills, it was the specific module on how to apply for jobs online.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"We examine how transaction fee structures affect mobile money usage frequency among informal market traders. Survey data from 350 traders across two urban markets shows that flat per-transaction fees, rather than percentage-based fees, are associated with significantly lower usage frequency for small transactions, suggesting that fee structure -- not just fee level -- shapes adoption among low-margin traders.""",
        response="This study surveyed 350 market traders to see how mobile money fees affect how often they use it. Traders faced with a flat fee per transaction used mobile money less often for small purchases than traders paying a percentage-based fee -- meaning it's not just how much the fee costs, but how it's structured, that discourages traders with tight profit margins from using it.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This paper assesses the effectiveness of SMS-based flood early-warning alerts in reducing property losses among riverside communities. Comparing 12 villages with SMS alert systems to 12 without, alerted villages reported 42% lower average property losses during flood events, with response time -- not just alert receipt -- identified as the key mediating factor.""",
        response="Researchers compared 12 villages that received flood warnings by text message to 12 similar villages that didn't. The villages with SMS alerts had 42% less property damage during floods -- but the study found it wasn't just about getting the warning, it was about how quickly people actually acted on it that made the real difference.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This study investigates the relationship between internet connectivity disruptions and self-reported academic stress among university students. Survey responses from 540 students indicate that unpredictable, rather than lengthy, outages are most strongly associated with elevated stress, suggesting that outage predictability -- allowing students to plan around it -- may matter more for wellbeing than outage duration itself.""",
        response="This study surveyed 540 university students about how internet outages affect their stress levels. Surprisingly, it wasn't the length of the outages that stressed students out the most -- it was not knowing when they'd happen. Predictable outages, even long ones, were less stressful than short, unexpected ones, since students could at least plan around a schedule they knew.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"We compare community radio broadcasts and SMS messaging as channels for public health information delivery in rural areas with mixed literacy levels. Radio broadcasts reached a broader audience overall, but SMS messages showed significantly higher message recall accuracy one week later, suggesting the two channels may be complementary rather than substitutes for reaching different program goals.""",
        response="This study compared two ways of sharing public health information in rural areas: community radio and text messages. Radio reached more people overall, but people who got the information by text remembered it more accurately a week later. The takeaway is that these aren't really competing methods -- radio is better for reaching a wide audience, while text messages are better when you need people to actually remember and act on specific information.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a results section without accidentally slipping into interpreting what the results mean?",
        response="""The most common mistake in a results section is mixing reporting with interpretation -- saving interpretation for the discussion section is what keeps a paper's logic clear and lets readers evaluate your evidence before your argument about it.

A concrete test: if a sentence uses "because," "suggests," "indicates," or "shows that this means," it's probably interpretation, not reporting, and belongs in the discussion instead. Compare these two versions of the same finding:

- **Interpretation (wrong section):** "Graduates were more likely to be employed because the training gave them confidence."
- **Reporting (correct for results):** "Program graduates were employed at a rate of 68%, compared to 29% among the control group (p < 0.01)."

The results section states what you found, with the actual numbers, and lets the discussion section argue about why. Keeping this separation disciplined makes both sections stronger -- results reads as objective evidence, and discussion reads as a genuine argument built on that evidence, rather than the two blurring together.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What's the general principle behind citing sources correctly, even if I'm not sure which specific citation style my program requires?",
        response="""Regardless of the specific style (APA, MLA, Chicago, IEEE, and others all have different exact formatting rules), citations exist to do two things: let a reader trace any claim back to where it came from, and give credit for ideas that aren't your own.

Two things matter more than getting the exact punctuation right on day one:
1. **Consistency.** Pick one style and apply it identically throughout the whole document -- a mix of styles looks like carelessness even if each individual citation is technically well-formed.
2. **Cite the specific claim, not just the general topic.** If you state a specific number or finding, that exact sentence needs a citation attached to it -- not just a general reference somewhere in the paragraph.

Once you know which style your program or journal actually requires, most word processors and reference managers (like Zotero or Mendeley) can auto-format citations for you -- the harder discipline is remembering to cite as you write, rather than trying to reconstruct where every claim came from after the fact.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="I need to summarize my thesis findings for a general audience, not other researchers. How should that be different from my academic abstract?",
        response="""The core content stays the same, but three things change for a general audience:

1. **Cut jargon or define it immediately.** "Mixed-methods design" means nothing to a general reader -- either say "we combined a survey with follow-up interviews" or explain the term the first time you use it.
2. **Lead with why it matters, not with your method.** Academic writing often opens with methodology; general audiences want the practical significance first -- what does this actually change for someone?
3. **Use concrete numbers sparingly, and round them.** "61% cost reduction" is fine; a precise p-value or confidence interval usually isn't meaningful to a non-specialist and can be dropped entirely.

A useful test: read your summary aloud to someone outside your field. If they have to ask "what does that mean?" more than once, it still needs another editing pass -- the goal is that a policymaker or a curious relative could read it and understand what you found and why it's useful, without needing your academic training to follow it.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="A reviewer might question why my study only surveyed 40 people. How do I address a small sample size honestly in my methodology section?",
        response="""Don't try to hide or minimize it -- acknowledging a limitation directly, with reasoning, reads as far more credible than hoping a reviewer won't notice.

A workable approach:
1. **State the number plainly**, without apologizing excessively for it.
2. **Explain the practical constraint that led to it** -- limited time, budget, or access to the population you needed, if that's genuinely why.
3. **Frame what the sample size does and doesn't support.** A small sample can still support a genuine, real finding -- it just can't claim broad generalizability the way a larger, randomly sampled study could.

Example: "Due to time and resource constraints, this study surveyed 40 participants from a single university. While this sample size limits the generalizability of findings to the broader student population, it provides an initial exploratory basis for identifying patterns that future, larger-scale studies could test more broadly." That framing turns a limitation into an honest, defensible scope statement, rather than an unaddressed weakness a reviewer has to point out themselves.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What makes a strong thesis title, versus a weak one?",
        response="""A weak title is usually either too vague ("A Study of Mobile Technology in Africa") or just restates the general topic without saying what the study actually found or examined. A strong title typically does two things: names the specific relationship being studied, and names the specific population or context.

Compare:
- **Weak:** "Mobile Banking in Rural Areas"
- **Stronger:** "Network Reliability and Digital Literacy as Predictors of Mobile Banking Adoption Among Rural Households in East Africa"

The stronger version tells a reader, before they even open the paper, exactly what relationship is being tested (reliability and literacy as predictors) and in what specific context (rural East African households). A good test: could your title apply equally well to five other unrelated studies? If yes, it's probably still too generic and needs the specific variables or population named directly.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does `x` end up being 3 in both print statements, when I expected different values?

```python
functions = []
for x in range(3):
    functions.append(lambda: print(x))

for f in functions:
    f()
```""",
        response="""All three lambdas share the *same* variable `x`, not separate snapshots of its value at the time each lambda was created. By the time the loop finishes, `x` is `2` (the last value it took), and since every lambda looks up `x` fresh each time it's called -- not when it was defined -- they all print `2`, not `0`, `1`, `2` as you might expect.

Fix by capturing the current value as a default argument, which *does* get evaluated at definition time:
```python
functions = []
for x in range(3):
    functions.append(lambda x=x: print(x))
```
`x=x` creates a new parameter that copies the current value of `x` into the lambda's own local scope at the moment it's defined, so each lambda genuinely gets its own frozen snapshot instead of sharing the loop variable.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this function return `undefined` instead of the sum?

```javascript
function sum(a, b) {
    if (a > 0 && b > 0) {
        a + b;
    }
}
```""",
        response="""There's no `return` statement, so the function computes `a + b` and immediately throws the result away -- JavaScript functions return `undefined` by default unless you explicitly return something.

Fixed version:
```javascript
function sum(a, b) {
    if (a > 0 && b > 0) {
        return a + b;
    }
}
```
Worth also noticing: this function still returns `undefined` if `a` or `b` isn't positive, since there's no `else` branch -- whether that's intentional depends on what you want the function to do for negative inputs, but it's worth deciding on purpose rather than by accident.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this comparison sometimes fail even though the math looks correct?

```python
result = 0.1 + 0.2
if result == 0.3:
    print("Equal")
else:
    print("Not equal")  # this prints!
```""",
        response="""This prints "Not equal" because `0.1 + 0.2` actually evaluates to `0.30000000000000004`, not exactly `0.3`. Floating-point numbers can't represent most decimal fractions with perfect precision in binary, so small rounding errors like this are a normal, expected part of floating-point arithmetic -- not a bug in Python itself.

The fix is to compare with a small tolerance instead of exact equality:
```python
result = 0.1 + 0.2
if abs(result - 0.3) < 1e-9:
    print("Equal")
```
`abs(result - 0.3) < 1e-9` checks that the difference is negligibly small, rather than demanding a perfect match. This is a genuinely common trap across almost every programming language, not specific to Python -- exact equality checks on floats are usually the wrong tool.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this SQL query fail with an error about `name` not being in the GROUP BY clause?

```sql
SELECT department, name, COUNT(*)
FROM students
GROUP BY department;
```""",
        response="""When you use `GROUP BY`, every column in `SELECT` has to either be part of the `GROUP BY` list, or be wrapped in an aggregate function like `COUNT()`, `SUM()`, or `AVG()`. Here, `name` is neither -- it's not in `GROUP BY department`, and it's not aggregated, so the database can't determine which single `name` value to show for a department that might contain many different students.

Two ways to fix it, depending on what you actually want:
```sql
-- Option 1: count students per department, drop name entirely
SELECT department, COUNT(*)
FROM students
GROUP BY department;

-- Option 2: include name in the grouping (now grouped by department AND name)
SELECT department, name, COUNT(*)
FROM students
GROUP BY department, name;
```
Option 2 changes the meaning of the query -- it now counts per unique department-name combination, not per department overall -- so pick the one that actually answers your real question.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why do these print statements come out in the wrong order?

```javascript
console.log("1");
fetchData().then(() => console.log("2"));
console.log("3");
```""",
        response="""This prints `1`, `3`, `2` -- and that's actually correct behavior, not a bug, once you understand why. `fetchData()` returns a Promise, and `.then()`'s callback only runs once that Promise resolves, which happens *later*, after the current code finishes running. JavaScript doesn't pause and wait at that line; it keeps executing `console.log("3")` immediately, and only comes back to run the `.then()` callback once the asynchronous work is actually done.

If you genuinely need `"2"` to print before `"3"`, you have to explicitly wait for it with `await`, inside an `async` function:
```javascript
async function run() {
    console.log("1");
    await fetchData();
    console.log("2");
    console.log("3");
}
```
Now execution genuinely pauses at `await` until `fetchData()` resolves, giving you the order `1`, `2`, `3` instead.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )
    yield SFTExample(
        instruction="""Why is this login query dangerous, and how do I fix it?

```python
def login(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
```""",
        response="""This is vulnerable to SQL injection. Because `username` and `password` are inserted directly into the query string, an attacker can type something like `' OR '1'='1` as the username, turning your intended query into one that's always true, bypassing the login check entirely -- no valid password needed.

Fix it with parameterized queries, which send the values separately from the query structure instead of building them into the string:
```python
def login(username, password):
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
```
The database driver handles escaping safely here, so user input can never change the query's actual structure, no matter what characters someone types in. This is a hard rule worth internalizing: never build a SQL query with string formatting or concatenation when any part of it comes from user input.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this function drop the last character of the string?

```python
def remove_first_char(text):
    return text[1:len(text) - 1]
```""",
        response="""`text[1:len(text) - 1]` slices from index 1 up to, but not including, `len(text) - 1` -- which cuts off both the first character *and* the last one. The intent was clearly just to drop the first character.

Fixed version:
```python
def remove_first_char(text):
    return text[1:]
```
Leaving the end of the slice empty means "go all the way to the end of the string" -- there's no need to calculate `len(text)` manually at all here, and doing so is exactly what introduced the off-by-one mistake.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this print `undefined` instead of the greeting?

```javascript
function greet() {
    console.log(message);
    var message = "Hello!";
}
greet();
```""",
        response="""This is caused by `var`'s "hoisting" behavior: `var message` is moved to the top of the function during compilation, but its *value* assignment (`= "Hello!"`) stays right where it was written. So at the point `console.log(message)` runs, `message` already exists but hasn't been assigned yet -- it's `undefined`, not an error, which makes this bug easy to miss.

Using `let` instead makes this mistake throw a clear error instead of silently printing `undefined`:
```javascript
function greet() {
    console.log(message); // ReferenceError: Cannot access 'message' before initialization
    let message = "Hello!";
}
```
This is one of several real reasons modern JavaScript style prefers `let`/`const` over `var` -- `var`'s hoisting behavior hides genuine ordering bugs instead of surfacing them.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this code never show me what actually went wrong?

```python
try:
    result = risky_calculation()
except:
    print("Something went wrong")
```""",
        response="""A bare `except:` catches *every* exception -- including ones you didn't anticipate, and even ones like `KeyboardInterrupt` that you almost never want to silently swallow. Worse, it discards the actual error entirely, so "something went wrong" is all you'll ever know, even if the real cause was a simple typo you could have fixed in seconds.

Better version:
```python
try:
    result = risky_calculation()
except Exception as e:
    print(f"Something went wrong: {e}")
```
This still catches unexpected errors, but keeps the actual exception message so you can see what really happened. Even better, when you know what specific error you're guarding against, catch that specific exception type (like `except ValueError:`) rather than the broad `Exception` -- that way, genuinely unexpected errors still surface instead of being silently swallowed too.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function only remove every other matching item instead of all of them?

```python
def remove_zeros(numbers):
    for i, n in enumerate(numbers):
        if n == 0:
            numbers.pop(i)
    return numbers
```""",
        response="""Modifying a list while you're iterating over it shifts every later element's index down by one -- so the loop's internal position and the list's actual current contents fall out of sync, and some elements get skipped entirely.

Fix by building a new list instead of mutating the original while iterating:
```python
def remove_zeros(numbers):
    return [n for n in numbers if n != 0]
```
This sidesteps the problem completely, since you're never modifying the list you're currently looping over -- you're building a fresh one from scratch. As a general rule, mutating a list (or dict) while iterating over it is almost always a source of subtle, hard-to-spot bugs, regardless of the specific operation.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This study examines completion rates for scheduled telemedicine consultations in regions with intermittent internet connectivity. Analyzing 890 scheduled appointments across six clinics, consultations scheduled with a text-based fallback option (allowing the visit to continue via SMS if video connection failed) had a 31% higher completion rate than video-only appointments, with no significant difference in patient-reported satisfaction between the two formats.""",
        response="Researchers looked at 890 telemedicine appointments in areas where the internet doesn't always work reliably. Appointments that had a backup option to switch to text messaging if the video call failed were completed 31% more often than video-only appointments -- and patients were just as satisfied either way, suggesting the fallback option is a low-cost way to keep more appointments from failing entirely.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"We investigate whether SMS payment reminders improve microloan repayment rates among small business borrowers. In a sample of 1,200 borrowers, those receiving reminders three days before their payment due date had a 22% lower late-payment rate than borrowers receiving no reminders, with reminders sent on the due date itself showing no measurable effect.""",
        response="This study tested whether text-message reminders help small business owners repay their microloans on time. Among 1,200 borrowers, those reminded three days before their payment was due were 22% less likely to pay late -- but sending the reminder on the actual due date, once it was already too late to plan ahead, made no real difference at all.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This paper evaluates the impact of a year-long teacher professional development program on student mathematics test scores. Comparing 45 participating schools to 45 matched non-participating schools, students in participating schools scored on average 8% higher, with the effect concentrated almost entirely in schools that maintained consistent teacher attendance throughout the program, rather than schools with high teacher turnover during it.""",
        response="This study compared 45 schools whose teachers went through a year-long training program to 45 similar schools that didn't. Students in the trained schools scored 8% higher on math tests on average -- but that benefit mostly only showed up in schools where the same teachers stayed through the whole program; schools with a lot of teacher turnover during the training saw little to no benefit.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="When should I present data in a table versus describing it in prose in my results section?",
        response="""A useful rule: if a reader would need to hold more than two or three numbers in their head at once to follow your sentence, it belongs in a table instead.

Prose works well for a single key comparison: "Program graduates were employed at more than double the rate of the control group (68% vs. 29%)." That's easy to read as a sentence.

A table becomes clearer once you're presenting multiple related figures at once -- say, employment rates broken down by five different age groups, or results across three different survey waves. Cramming that into a paragraph forces the reader to do the organizing work themselves; a table does it for them.

A common mistake to avoid: don't present the same numbers in *both* a table and a full paragraph restating every value -- that's redundant. If you have a table, your prose should reference and interpret its key findings, not just repeat every cell.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I respond professionally to peer review comments that feel overly critical, without sounding defensive?",
        response="""Even a harshly-worded review is usually pointing at something real underneath the tone -- treating every comment as worth a genuine response, rather than dismissing the ones that sting, tends to produce a stronger revised paper either way.

A structure that works well for each point:
1. **Acknowledge what the reviewer is asking**, in your own words, so they can see you actually understood the concern.
2. **State what you changed**, specifically -- point to the actual section or page, not just "we addressed this."
3. **If you disagree, explain why, respectfully** -- reviewers can be wrong, but "we chose not to change this because..." with real reasoning is very different from ignoring the comment or arguing back defensively.

Avoid language like "the reviewer clearly misunderstood" even when you believe that's true -- it reads as combative regardless of whether it's accurate, and it's rarely necessary: you can address the substance of a misunderstanding without characterizing the reviewer's competence at all.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I write a simple unit test in Python?",
        response="""```python
def add(a, b):
    return a + b

# test_add.py
def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2
```

Using `pytest`, any function starting with `test_` in a file that matches `test_*.py` gets automatically discovered and run. Each test calls your actual function and uses `assert` to check the result matches what you expect -- if the assertion is false, `pytest` reports that specific test as failed, showing you exactly which case broke.

Run all tests in a project with:
```
pytest
```
Writing a test for both a normal case and an edge case (like the negative-number example here) is good practice -- it's easy to write code that works for the "obvious" input but breaks on something you didn't think to try manually.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="Write a function that validates whether a string looks like a properly formatted email address.",
        response="""```python
import re

def is_valid_email(email):
    pattern = r'^[\\w.+-]+@[\\w-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

This uses a regular expression: `[\\w.+-]+` matches one or more word characters, dots, plus signs, or hyphens (the part before `@`), `@` matches the literal symbol, `[\\w-]+` matches the domain name, and `\\.[a-zA-Z]{2,}` requires a dot followed by at least two letters (the extension, like `.com` or `.org`).

Worth knowing honestly: this catches obviously malformed input, but fully validating an email address per the official spec is notoriously complex -- the only way to be *certain* an email actually works is to send a verification email to it and see if someone confirms receipt. Use pattern checks like this to catch typos early, not as a substitute for that real verification step.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="Write a simple Python class representing a student, with a name, a list of grades, and a method to compute their average grade.",
        response="""```python
class Student:
    def __init__(self, name):
        self.name = name
        self.grades = []

    def add_grade(self, grade):
        self.grades.append(grade)

    def average(self):
        if not self.grades:
            return 0
        return sum(self.grades) / len(self.grades)

student = Student("Omol")
student.add_grade(85)
student.add_grade(92)
print(student.average())  # 88.5
```

`__init__` is the constructor -- it runs automatically when you create a new `Student`, setting up that instance's starting state (`name` and an empty `grades` list). `self` refers to the specific instance the method is being called on, which is how each `Student` object keeps its own independent `grades` list rather than sharing one across every student. The `if not self.grades` check in `average()` avoids a `ZeroDivisionError` for a student with no grades recorded yet.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I read a CSV file and extract just one column of values in Python?",
        response="""```python
import csv

names = []
with open("students.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        names.append(row["name"])

print(names)
```

`csv.DictReader` reads each row as a dictionary keyed by the header row's column names, so `row["name"]` grabs just that column's value for each row without you needing to track column positions by number. This is generally more readable and less fragile than plain `csv.reader`, which gives you rows as plain lists indexed by position -- if someone reorders the CSV's columns later, `DictReader`-based code still works correctly, while position-based code would silently start reading the wrong column.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="Write a function that reverses a string using recursion.",
        response="""```python
def reverse(text):
    if len(text) <= 1:
        return text
    return reverse(text[1:]) + text[0]
```

The base case is a string of length 0 or 1 -- already its own reverse, nothing to do. The recursive case takes everything except the first character, reverses *that* (via the recursive call), and then appends the first character to the end -- moving it from the front of the original string to the back of the reversed one.

For `"cat"`: `reverse("at") + "c"` → `(reverse("t") + "a") + "c"` → `("t" + "a") + "c"` → `"tac"`. Worth noting honestly: this is a clean way to demonstrate recursion, but Python's built-in `text[::-1]` is both faster and simpler for actually reversing a string in real code -- recursion here is for understanding the technique, not the most practical solution to this specific problem.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="How do I read data from a JSON file and access a specific field in Python?",
        response="""```python
import json

with open("students.json") as f:
    data = json.load(f)

print(data["name"])
```

`json.load()` reads the file and converts its JSON structure directly into Python objects -- JSON objects become dictionaries, JSON arrays become lists, so `data["name"]` works exactly like accessing any regular Python dict once loaded. The reverse direction uses `json.dump()`:
```python
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)
```
`indent=2` makes the output file human-readable with actual line breaks and spacing, instead of one dense unbroken line -- worth using whenever a human might need to open and read the file directly.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="Write a function that counts how many times each word appears in a sentence.",
        response="""```python
def word_frequency(sentence):
    counts = {}
    for word in sentence.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts
```

`.split()` breaks the sentence into a list of words on whitespace, and `.lower()` first ensures "The" and "the" count as the same word rather than two different ones. `counts.get(word, 0)` is the key trick: it looks up the word's current count, defaulting to `0` if the word hasn't been seen yet, so you can safely add 1 without a separate check for "is this word already in the dictionary." This pattern -- a dictionary counting occurrences -- comes up constantly in real code, well beyond just counting words.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I make a GET request to an API and read the response in Python?",
        response="""```python
import requests

response = requests.get("https://api.example.com/students")
data = response.json()
print(data)
```

`requests.get()` sends the request and waits for a response. `response.json()` parses the response body as JSON and hands it back as a regular Python dict or list, ready to use directly. It's worth checking the request actually succeeded before trusting the data:
```python
if response.status_code == 200:
    data = response.json()
else:
    print(f"Request failed: {response.status_code}")
```
Skipping this check is a common source of confusing crashes later on -- if the request failed, `response.json()` might not contain what you expect, or might fail outright, and the error you see then won't obviously point back to the real cause.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="Write a function that builds a formatted greeting message using an f-string.",
        response="""```python
def build_greeting(name, course):
    return f"Hello {name}, welcome to {course}!"
```

An f-string (prefixed with `f`) lets you embed variables and expressions directly inside `{}` within the string, evaluated at runtime -- `{name}` gets replaced with the actual value of the `name` variable. This is generally clearer than building the same string with concatenation:
```python
return "Hello " + name + ", welcome to " + course + "!"
```
The concatenation version works, but gets harder to read as more variables get added, and it's easy to miss a space or forget a `+`. F-strings also handle non-string values automatically -- `f"Score: {score}"` works even if `score` is a number, without needing to convert it with `str()` first.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this crash with a KeyError?

```python
student = {"name": "Omol", "age": 22}
print(student["email"])
```""",
        response="""`student` doesn't have an `"email"` key -- only `"name"` and `"age"` -- so trying to access it directly with `[...]` raises `KeyError: 'email'`. Dictionaries only let you access keys that actually exist this way.

If a key might legitimately be missing sometimes, `.get()` handles it gracefully instead of crashing:
```python
print(student.get("email"))       # None, no error
print(student.get("email", "N/A")) # "N/A" -- your own custom default
```
`.get()` returns `None` (or a default value you specify) instead of raising an error when the key isn't found. Use direct `[...]` access when a missing key genuinely represents a bug you want to catch loudly; use `.get()` when a missing key is an expected, normal possibility.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this crash with a TypeError, and the error points somewhere confusing?

```python
def get_bonus(score):
    if score > 90:
        return 10

total = 50 + get_bonus(85)
```""",
        response="""`get_bonus(85)` runs, but since `85` isn't greater than `90`, the function falls through without hitting any `return` statement -- so it implicitly returns `None`. The actual crash then happens one line later, at `50 + None`, which raises `TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'`.

The fix is to give the function an explicit path for every case, not just the one you were thinking about:
```python
def get_bonus(score):
    if score > 90:
        return 10
    return 0
```
This bug is worth recognizing as a pattern: whenever an error mentions `NoneType` unexpectedly, it's very often a function that forgot to return a value on some path -- the error appears far from the actual missing `return`, which is what makes it confusing to trace at first.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""This error handling doesn't actually catch the real error being thrown -- why not?

```python
try:
    age = int(student_input)
except ValueError:
    print("Please enter a valid number")
```

The actual crash reported is `TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'`.""",
        response="""`except ValueError` only catches `ValueError` -- it does nothing for other exception types. Here, `student_input` is apparently `None` (perhaps a form field that wasn't filled in), and calling `int(None)` raises `TypeError`, not `ValueError`, so your `except` block never triggers at all; the error propagates up and crashes the program.

Catch both, if both are genuinely expected possibilities:
```python
try:
    age = int(student_input)
except (ValueError, TypeError):
    print("Please enter a valid number")
```
The broader lesson: `except SomeSpecificError` only catches that exact type (and its subclasses) -- it's not a general safety net. Before writing exception handling, it's worth actually checking what exception type your specific failure case raises, rather than guessing.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between correlation and causation, and why does it matter for interpreting research findings?",
        response="""Correlation means two variables tend to change together -- when one goes up, the other tends to go up (or down) too. Causation means one variable actually *produces* the change in the other. Correlation on its own never proves causation, because a third, unmeasured factor could be driving both.

A classic example: ice cream sales and drowning deaths both rise in the summer -- they're correlated, but ice cream doesn't cause drowning. The real cause behind both is a third variable: hot weather, which increases both ice cream purchases and swimming (and therefore drowning risk).

This matters directly for how you write about your own findings: "Students who used the tutoring program scored higher" is a correlational claim, even if it sounds causal. To claim the program *caused* the improvement, you'd need to rule out other explanations -- maybe more motivated students were the ones who chose to use tutoring in the first place. Being precise about this distinction in your own writing (using words like "associated with" rather than "caused" unless your study design actually supports a causal claim) is one of the most common things reviewers check for.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What does informed consent actually require when collecting data from research participants?",
        response="""Informed consent means a participant genuinely understands what they're agreeing to before they agree to it -- not just that they signed something. At minimum, that generally means participants should clearly know:

1. **What they're being asked to do**, concretely -- not a vague description.
2. **How the data will be used**, including who sees it and what it's used for.
3. **That participation is voluntary**, and they can withdraw without penalty.
4. **Any real risks or limitations**, stated honestly rather than glossed over -- including things like whether their contribution can later be removed once it's part of a larger dataset or trained system.
5. **Who to contact** with questions or concerns.

A consent form that's technically signed but full of dense legal language a participant didn't actually understand doesn't meet the spirit of informed consent, even if it meets a narrow legal bar. The goal is a participant who could accurately explain back to you what they agreed to -- if they couldn't, the consent process didn't really work, regardless of the paperwork.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the difference between qualitative and quantitative research, and how do I know which one fits my question?",
        response="""Quantitative research measures things numerically and looks for patterns across a (usually larger) group -- surveys with rating scales, test scores, counts of an event. It answers questions like "how much" or "how many," and supports statistical comparison.

Qualitative research explores meaning, experience, and context in depth -- interviews, open-ended responses, observation -- usually with a smaller number of participants studied more thoroughly. It answers questions like "why" or "how does this feel to the people experiencing it."

A rough test for which fits your question: if you're asking "does X happen more than Y, and by how much," that's quantitative. If you're asking "why do people choose X over Y" or "what is this experience actually like for them," that's qualitative. Many strong studies use both together (a "mixed-methods" design) -- quantitative data to establish a pattern exists, and qualitative interviews to understand why it exists, each answering a different part of the same underlying question.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I decide on an appropriate sample size for my study, given I don't have resources for a huge survey?",
        response="""There's no single "correct" sample size that fits every study -- it depends on your population size, how much variation you expect in responses, and how confident you need to be in the result. That said, a few practical principles help even without formal statistical power calculations:

1. **Bigger isn't automatically better if it's not representative.** A well-selected sample of 100 people, covering the real diversity of your target population, often produces more trustworthy findings than a poorly-selected sample of 500 drawn entirely from one convenient location.
2. **Be honest about what your sample size can and can't support.** A sample of 40 can identify a genuine pattern worth investigating further; it usually can't support strong claims about an entire national population.
3. **State your reasoning for the number you chose**, even if it's a practical constraint like time or budget -- reviewers respond much better to an honestly justified small sample than an unexplained one.

If your study is meant to formally test a specific hypothesis with statistical significance, a proper power calculation (which estimates the minimum sample needed to detect an effect of a given size) is worth doing before you start collecting data, not after.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This study explores barriers to entrepreneurship among women operating informal market businesses, drawing on in-depth interviews with 25 traders across two markets. Participants consistently identified lack of access to formal credit -- rather than lack of business skill or market knowledge -- as the primary constraint on business growth, with informal lending networks serving as an insufficient substitute for accessing capital needed to expand inventory.""",
        response="Researchers interviewed 25 women running informal market businesses to understand what holds their businesses back from growing. The women themselves said the biggest problem wasn't a lack of business knowledge or skill -- it was not being able to get formal loans. The informal lending networks they relied on instead just weren't enough to help them buy more inventory and actually expand.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"We evaluate the effectiveness of a community-led handwashing behavior change campaign in reducing diarrheal disease incidence among children under five. Comparing 20 villages with the campaign to 20 without over a six-month period, campaign villages saw a 27% reduction in reported diarrheal cases, with community-led messaging (delivered by trained local volunteers) outperforming an earlier pilot that used only printed posters.""",
        response="This study tested whether a handwashing campaign run by trained local volunteers could reduce diarrhea cases in young children. Comparing 20 villages that had the campaign to 20 that didn't, the campaign villages saw diarrhea cases drop by 27% over six months -- and having local volunteers deliver the message worked much better than an earlier attempt that just used printed posters.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This paper examines why scheduled remote consultations are abandoned mid-session in regions with unreliable electricity access. Analyzing 310 dropped sessions, device battery depletion -- rather than network failure -- was the single largest identified cause, accounting for 44% of dropped calls, suggesting that power access, not just connectivity, is a critical and often overlooked constraint on remote service delivery.""",
        response="Researchers looked at 310 remote consultation calls that got cut off partway through, in areas where electricity isn't always reliable. The single biggest reason calls dropped wasn't a bad internet connection -- it was people's phones running out of battery, accounting for 44% of the dropped calls. This suggests that just having internet access isn't enough; having a way to actually keep your device charged matters just as much for these services to work.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Summarize this abstract in plain language, in 2-3 sentences:

"This study examines academic performance differences between university students who own a personal computer and those who rely on shared computer labs or borrowed devices. Controlling for prior academic performance, students relying on shared devices reported 40% less time available for assignment completion due to scheduling constraints, though final grades showed no statistically significant difference between the two groups once study time itself was accounted for.""",
        response="Researchers compared university students who own their own computer to students who rely on shared computer labs or borrowed devices. Students relying on shared devices had 40% less available time to work on assignments because of scheduling limits -- but once you account for actual study time, their final grades ended up about the same as students with their own computer, suggesting the students without personal devices were working just as effectively with the more limited time they had.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="Write a program that prints numbers 1 to 20, but prints 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, and 'FizzBuzz' for multiples of both.",
        response="""```python
for i in range(1, 21):
    if i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```

The order of the checks matters here: multiples of both 3 and 5 (like 15) also pass the `i % 3 == 0` check on its own, so if that check came first without the combined `and` condition, "FizzBuzz" would never actually print -- only "Fizz". Checking the combined condition first, before the individual ones, is what makes the more specific case take priority over the more general ones.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I sort a list of dictionaries by one of their fields, like sorting students by grade?",
        response="""```python
students = [
    {"name": "Omol", "grade": 85},
    {"name": "Andrew", "grade": 92},
    {"name": "Sara", "grade": 78},
]

sorted_students = sorted(students, key=lambda s: s["grade"], reverse=True)
```

`sorted()`'s `key` argument tells it exactly what to compare -- here, `lambda s: s["grade"]` extracts just the grade from each dictionary, so Python sorts based on that number instead of trying (and failing) to compare entire dictionaries directly. `reverse=True` sorts highest first; leave it out (or set `False`) for ascending order. This `key=` pattern is the general tool for sorting by any specific field, not just grades -- swap in whatever field you actually need.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I read a secret API key from an environment variable instead of hardcoding it in my Python code?",
        response="""```python
import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file into the environment

api_key = os.environ.get("API_KEY")
if not api_key:
    raise RuntimeError("API_KEY is not set -- check your .env file")
```

`os.environ.get("API_KEY")` reads the value from the environment rather than a value written directly into your source code. `load_dotenv()` (from the `python-dotenv` package) is what lets a local `.env` file populate those environment variables during development, without needing to set them manually in your terminal every time.

This matters for a real reason, not just style: hardcoded keys get committed to git history by accident constantly, and once something's in git history, it's very hard to fully remove even after you delete it -- keeping secrets in a `.env` file (and adding `.env` to `.gitignore`) keeps them out of your codebase entirely.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I get today's date and format it as a readable string in Python?",
        response="""```python
from datetime import date

today = date.today()
print(today.strftime("%B %d, %Y"))  # e.g. "September 1, 2026"
```

`date.today()` gives you the current date as a `date` object. `.strftime()` ("string format time") converts it into whatever text format you want, using format codes: `%B` is the full month name, `%d` is the day, `%Y` is the four-digit year. Change the format string to control the output -- `"%Y-%m-%d"` would give `"2026-09-01"` instead, the common format for sorting dates as plain text.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I create and raise my own custom exception in Python, instead of using a generic one?",
        response="""```python
class InsufficientFundsError(Exception):
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(f"Cannot withdraw {amount}, balance is only {balance}")
    return balance - amount
```

A custom exception is just a class that inherits from `Exception` (or a more specific built-in exception type). Once defined, you `raise` it exactly like a built-in exception, and callers can catch it specifically:
```python
try:
    withdraw(100, 150)
except InsufficientFundsError as e:
    print(f"Transaction failed: {e}")
```
The real benefit over just raising a generic `Exception` or `ValueError`: calling code can catch `InsufficientFundsError` specifically, without accidentally also catching unrelated errors that happen to be the same generic type -- your error handling gets more precise as your codebase grows.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this comparison return False even though the lists look identical?

```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a is b)  # False
```""",
        response="""`is` checks whether two names point to the exact same object in memory -- not whether their contents look equal. `a` and `b` are two separate list objects that happen to contain the same values, so `a is b` is `False`, even though `a == b` would correctly be `True`.

Use `==` when you want to compare values (almost always what you actually want):
```python
print(a == b)  # True -- same contents
print(a is b)  # False -- different objects
```
`is` is the right tool specifically for checking identity -- most commonly, checking whether something `is None`, since there's genuinely only ever one `None` object in a Python program. For comparing whether two things have the same *value*, `==` is almost always the correct choice.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function not actually change the string?

```python
def uppercase_first(text):
    text[0] = text[0].upper()
    return text
```""",
        response="""This raises `TypeError: 'str' object does not support item assignment`. Strings in Python are immutable -- once created, their individual characters can never be changed in place, unlike a list.

To get an uppercase first letter, you have to build a *new* string instead:
```python
def uppercase_first(text):
    return text[0].upper() + text[1:]
```
This takes the uppercased first character and concatenates it with everything after the first character, producing a new string rather than trying to modify the original. Any string "modification" in Python actually works this way under the hood -- even something like `.replace()` returns a new string rather than changing the original, which is why you always need to assign the result: `text = text.replace(...)`, not just call `.replace()` on its own and expect `text` to have changed.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function always print the discount message, even for cheap items?

```python
def check_price(price):
    if price > 100:
        print("Regular price")
    print("Discount available!")
```""",
        response="""The `print("Discount available!")` line isn't indented under the `if` block -- it's at the same indentation level as the `if` statement itself, so it runs every single time the function is called, completely independent of the price check above it.

Fixed version, if the discount message should only show for cheaper items:
```python
def check_price(price):
    if price > 100:
        print("Regular price")
    else:
        print("Discount available!")
```
Python uses indentation itself to define which lines belong inside a block -- there are no curly braces `{}` marking the boundaries like some other languages use. This makes indentation mistakes genuinely capable of silently changing your program's logic, not just its formatting, which is worth remembering as a real, distinct category of bug to watch for.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this always print "Access granted", no matter what role is passed in?

```python
def check_access(role):
    if role = "admin":
        print("Access granted")
    else:
        print("Access denied")
```""",
        response="""This is actually a syntax error in real Python, not a silent logic bug -- `=` is assignment, not comparison, and Python doesn't allow assignment inside an `if` condition this way, so it would refuse to run at all with a `SyntaxError`.

(In some other languages, like older C-style languages, `if (role = "admin")` *is* legal and this exact mistake silently always evaluates as true -- which is why it's worth knowing about even though Python catches it for you.)

The fix in Python is using `==` for comparison:
```python
def check_access(role):
    if role == "admin":
        print("Access granted")
    else:
        print("Access denied")
```
`=` assigns a value to a variable; `==` checks whether two values are equal. Mixing them up is one of the most common typos across almost every programming language, which is exactly why Python treats it as an error rather than silently running with the wrong meaning.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does sorting this list of dictionaries crash with a TypeError?

```python
students = [{"name": "Omol", "grade": 85}, {"name": "Sara", "grade": 92}]
sorted_students = sorted(students)
```""",
        response="""`sorted()` without a `key` argument tries to compare the dictionaries directly against each other using `<`, and Python has no defined way to say one dictionary is "less than" another -- there's no natural ordering for dictionaries, so it raises `TypeError: '<' not supported between instances of 'dict' and 'dict'`.

Fix it by telling `sorted()` exactly what to compare, using `key`:
```python
sorted_students = sorted(students, key=lambda s: s["grade"])
```
Now `sorted()` compares the extracted grade values (which *do* have a natural ordering) instead of trying to compare the dictionaries as a whole. Any time you're sorting a list of complex objects -- dictionaries, or your own custom class instances -- you need a `key` function telling Python specifically what value to sort by.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I search academic databases effectively, instead of just typing my whole research question into the search box?",
        response="""A whole research question typed directly into a search box usually returns poor results, since databases match on the specific words present, not on your underlying intent. A more effective approach:

1. **Break your question into 3-4 key concepts.** "How does mobile banking affect financial inclusion in rural areas?" breaks down into: mobile banking, financial inclusion, rural.
2. **List synonyms for each concept.** "Rural" might also appear as "remote," "underserved," or a specific region name in different papers.
3. **Combine concepts with AND, and synonyms with OR.** Most academic databases support this: `("mobile banking" OR "mobile money") AND ("financial inclusion" OR "financial access") AND rural`.
4. **Use the database's filters**, not just the search box -- publication date range, peer-reviewed only, and subject area filters cut out a lot of irrelevant results before you even start reading abstracts.

This structured approach consistently returns more relevant results than a single long natural-language sentence, since it matches how the database's search index actually works, rather than how a conversational question is phrased.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I paraphrase a source properly, so it doesn't count as plagiarism, even if I cite it?",
        response="""Citing a source tells the reader where an idea came from -- it doesn't automatically make copying that source's exact wording acceptable. Real paraphrasing means rewriting the idea in genuinely your own sentence structure and word choice, not just swapping a few synonyms into the original sentence.

A test that catches weak paraphrasing: cover the original source and try to write the idea from memory, in your own words, based on your actual understanding of it -- rather than looking at the original sentence and editing it word by word. If your "paraphrase" still follows the same sentence structure as the original with just a few words changed, that's still too close, even with a citation attached.

One more distinction worth knowing: if you want to use the source's exact original wording, that requires quotation marks *and* a citation -- paraphrasing (no quotation marks) and quoting (with quotation marks) are different, both legitimate tools, but using one while presenting it as the other is exactly what causes plagiarism problems, even when unintentional.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the difference between an abstract and an executive summary?",
        response="""Both summarize a longer document, but for different audiences and purposes. An abstract is written for other researchers in your field -- it can use technical terminology freely, and its job is to help someone decide whether the full academic paper is relevant to their own research.

An executive summary is written for decision-makers who may not have your specialized background -- a policymaker, a funder, an organization's leadership. It leads with practical implications and recommendations rather than methodology, and generally avoids field-specific jargon or explains it immediately if used.

A useful way to tell them apart: an abstract answers "what did you study, how, and what did you find?" An executive summary answers "what should I, the reader, actually do or understand as a result of this?" The same research project might need both documents, written quite differently, depending on who's going to read each one.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines e-waste disposal behavior among urban households, focusing on the relationship between awareness of environmental harm and actual disposal practices. Survey data from 400 households found that awareness of environmental risks did not predict proper disposal behavior; instead, the primary predictor was simple physical proximity to a designated e-waste collection point, suggesting that convenience -- not education campaigns alone -- drives behavior change."',
        response="Researchers surveyed 400 urban households about how they dispose of old electronics. Surprisingly, knowing that e-waste is harmful to the environment didn't actually predict whether people disposed of it properly -- what mattered most was simply how close they lived to a proper collection point. This suggests that making disposal convenient matters more than just teaching people why it's important.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate the impact of a short financial literacy training program on savings behavior among informal-sector workers. Comparing 200 program participants to a matched control group three months later, participants opened formal savings accounts at more than triple the rate of non-participants, with the effect strongest among workers who had never previously used any formal financial institution."',
        response="This study tested whether a short financial literacy course changes how informal-sector workers save money. Three months after 200 people took the course, they were more than three times as likely to have opened a formal savings account compared to people who didn't take it -- and the training helped most among workers who'd never used a bank or formal financial service before at all.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="What is a JWT, and why do apps use it for login sessions?",
        response="""A JWT (JSON Web Token) is a compact, signed piece of text that represents "this user is logged in, and here's who they are" -- without the server needing to store session data in memory or a database for every logged-in user.

A JWT has three parts, separated by dots: a header, a payload (the actual data, like a user ID and an expiration time), and a signature. The signature is the important part -- it's created using a secret key only the server knows, and lets the server verify the token hasn't been tampered with, without needing to look anything up. If someone edited the payload to claim a different user ID, the signature would no longer match, and the server would reject it.

This is why JWTs are described as "stateless": the server doesn't need to remember anything about active sessions -- each request just carries its own proof of identity, verifiable on the spot. The trade-off is that once issued, a JWT is valid until it expires; unlike a traditional server-side session, there's no simple built-in way to instantly revoke one early.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="Why shouldn't I just store user passwords directly in my database?",
        response="""If your database is ever breached -- and breaches happen even to careful teams -- storing plain-text passwords means every single user's actual password is immediately exposed, and since many people reuse passwords across sites, that damage extends far beyond just your own application.

The standard fix is hashing: running the password through a one-way function (like bcrypt) that produces a fixed-length scrambled output you can't reverse back into the original password.

```python
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

To check a login attempt, you hash the attempted password the same way and compare the two hashes -- you never need to "un-hash" anything, or even store the real password at all. bcrypt specifically also adds a random "salt" to each password before hashing, which prevents attackers from using a precomputed table of common password hashes to crack many accounts at once.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is rate limiting, and why do APIs use it?",
        response="""Rate limiting caps how many requests a single user, API key, or IP address can make in a given time window -- for example, "10 requests per minute." Once that limit is hit, further requests get rejected (usually with an HTTP 429 "Too Many Requests" response) until the window resets.

It serves two real purposes: protecting the server from being overwhelmed by a bug that accidentally sends requests in a runaway loop, and preventing deliberate abuse -- someone trying to hammer an endpoint to scrape data or brute-force a password.

A simple rate limit is usually enough for a small application; larger systems sometimes use more nuanced approaches, like different limits for different endpoints (a login endpoint might allow far fewer attempts per minute than a general read-only endpoint, since repeated login attempts are a common attack pattern worth limiting more aggressively).""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I check what type a variable is in Python before operating on it?",
        response="""```python
def process(value):
    if isinstance(value, str):
        return value.upper()
    elif isinstance(value, (int, float)):
        return value * 2
    else:
        return None
```

`isinstance(value, str)` checks whether `value` is a string (or a subclass of `str`). Passing a tuple of types, like `(int, float)`, checks against any of them at once. This is generally preferred over the older `type(value) == str` style, since `isinstance()` correctly handles subclasses -- if you ever create a custom class inheriting from `str`, `isinstance()` still recognizes it as a string, while `type() ==` would not.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I combine two lists element-by-element in Python, like pairing names with scores?",
        response="""```python
names = ["Omol", "Andrew", "Sara"]
scores = [85, 92, 78]

paired = list(zip(names, scores))
# [("Omol", 85), ("Andrew", 92), ("Sara", 78)]
```

`zip()` walks through both lists in parallel and pairs up elements at matching positions into tuples. It's commonly used directly in a loop without needing to build the full list first:
```python
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```
One thing worth knowing: if the two lists are different lengths, `zip()` stops at the shorter one -- it doesn't raise an error or pad the longer list, it just silently ignores the extra elements, which is worth being aware of if your lists might not always match in length.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this crash when the user enters something like "twenty"?

```python
age = int(input("Enter your age: "))
print(f"You are {age} years old")
```""",
        response="""`int()` can only convert strings that look like valid numbers -- `"25"` works, but `"twenty"` raises `ValueError: invalid literal for int() with base 10: 'twenty'`, since there's no numeric interpretation of that text.

Handle it gracefully with a try/except instead of letting the program crash:
```python
try:
    age = int(input("Enter your age: "))
    print(f"You are {age} years old")
except ValueError:
    print("Please enter a valid number")
```
Any time you're converting user-provided input to a number, assume it might not actually be a valid number -- users mistype, paste the wrong thing, or genuinely misunderstand what's being asked. Wrapping the conversion in error handling is standard practice, not excessive caution.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this function call give unexpected results?

```python
def create_student(name, age, grade):
    return {"name": name, "age": age, "grade": grade}

student = create_student(22, "Omol", 85)
```""",
        response="""The arguments were passed in the wrong order. Python matches positional arguments strictly by position, not by their apparent meaning -- so `22` gets assigned to `name`, `"Omol"` to `age`, and `85` to `grade`, even though that clearly wasn't intended, and nothing about calling it this way raises an error.

Two fixes, depending on preference:
```python
# Fix 1: just get the order right
student = create_student("Omol", 22, 85)

# Fix 2: use keyword arguments, which are self-documenting and order-independent
student = create_student(name="Omol", age=22, grade=85)
```
Keyword arguments are worth using especially for functions with several parameters of the same type (several numbers or several strings in a row) -- they make the call itself readable, and they make this exact kind of silent misordering mistake far less likely to happen in the first place.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How should I structure a research proposal, before I've actually collected any data?",
        response="""A research proposal argues for why a study is worth doing and how you'll do it -- it's forward-looking, unlike a finished paper's report of what you found. A structure that works for most proposals:

1. **Background and problem statement** -- what's known, and what specific gap or problem your study addresses.
2. **Research question(s)** -- stated precisely, the same way you would in a finished thesis.
3. **Proposed methodology** -- how you plan to collect and analyze data, written in future tense ("will be surveyed," not "were surveyed").
4. **Significance** -- who benefits from this research existing, and why it matters beyond satisfying a course requirement.
5. **Timeline and feasibility** -- a realistic plan for actually completing the work, including any resource or access constraints you're aware of upfront.

A proposal that skips feasibility is a common weakness reviewers flag -- it's not enough to describe an ideal study; you need to convince the reader that *you specifically*, with your actual available time and resources, can realistically carry it out.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between statistical significance and effect size, and why does it matter to report both?",
        response="""Statistical significance (usually reported as a p-value) tells you whether an observed difference is likely to be a real pattern rather than random chance. Effect size tells you how *large* that difference actually is in practical terms. A result can be statistically significant while still being practically tiny -- especially with a large sample size, even a trivial difference can reach statistical significance.

Concretely: a study of 50,000 people might find a "statistically significant" 0.5% improvement in test scores from some intervention. That's real (not chance), but a 0.5% improvement might not be worth the cost or effort of implementing the intervention at all.

This is why strong research reports both numbers, not just "p < 0.05." A p-value alone tells a reader "this is probably real," while the effect size tells them "and here's whether it's actually worth caring about." Reporting significance without effect size is a common and genuinely misleading gap in weaker research writing.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I write an honest limitations section without making my whole study sound weak or unreliable?",
        response="""Every study has limitations -- acknowledging them is a sign of rigor, not weakness, and reviewers actively look for this section. The goal is precision, not excessive apology: name the specific limitation, explain its likely impact, and move on, rather than hedging every single claim in your paper.

A useful structure for each limitation:
1. **State it plainly.** "This study relied on self-reported data, which may be subject to recall bias."
2. **Explain the likely direction of impact**, if you can reasonably estimate it. "This may have led to overestimating actual usage frequency, if participants rounded up when recalling past behavior."
3. **Note what would address it in future work**, briefly. "Future studies could pair self-report with usage logs to validate these estimates."

What to avoid: vague blanket statements like "this study has several limitations and results should be interpreted with caution" without naming any of them specifically -- that reads as evasive rather than rigorous, and gives the reader no actual information about how much to trust which parts of your findings.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What makes a survey question 'leading', and how do I avoid writing them by accident?",
        response="""A leading question is phrased in a way that nudges respondents toward a particular answer, rather than neutrally measuring their actual view. This often happens without the researcher intending it.

Compare: "Don't you think the new library hours are more convenient?" versus "How would you rate the new library hours?" The first embeds an expected positive answer directly into the question's wording; the second leaves genuine room for any response.

A few concrete things to watch for:
- **Loaded words.** "Do you support this reasonable policy?" -- "reasonable" is doing persuasive work that doesn't belong in a neutral question.
- **Assuming a premise.** "How much did the new system improve your workflow?" assumes it improved things at all, rather than first asking whether it did.
- **Unbalanced options.** A scale from "good" to "excellent" gives no way to express a negative view at all.

A useful check: have someone unfamiliar with your expected results read your questions and guess what answer you're hoping for. If they can guess it easily, the wording likely needs revising before you actually send the survey out.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether offering flexible micro-loan repayment schedules, aligned with seasonal agricultural income, improves repayment rates among smallholder farmers. Comparing 300 farmers on flexible schedules to 300 on fixed monthly schedules, flexible-schedule borrowers had a 38% lower default rate, with the effect concentrated almost entirely among farmers growing single-harvest crops rather than those with multiple harvests per year."',
        response="This study compared 300 farmers repaying loans on a schedule matched to their harvest income against 300 farmers on a regular fixed monthly schedule. Farmers on the flexible schedule defaulted on their loans 38% less often -- and this benefit mostly applied to farmers who only harvest once a year, since a fixed monthly payment doesn't match how their income actually arrives.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine the relationship between class size and student participation in university computer science courses. Observational data from 40 course sections found that sections with fewer than 25 students had significantly higher rates of student-initiated questions during lectures, with no corresponding difference found in final exam performance between smaller and larger sections."',
        response="Researchers looked at 40 university computer science classes to see how class size affects student participation. Smaller classes, with fewer than 25 students, had noticeably more students asking questions during lectures -- but interestingly, this didn't translate into better final exam scores; students in larger classes performed just as well despite asking fewer questions in class.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether offline-cached map data improves emergency response times for ambulance services operating in areas with unreliable mobile network coverage. Across 85 recorded emergency dispatches, teams using offline-cached routing reached the scene an average of 4.2 minutes faster than teams relying on live network-dependent navigation, with the gap widening substantially during confirmed network outage periods."',
        response='This study looked at 85 ambulance emergency responses to see if having maps saved on the phone in advance -- rather than relying on a live internet connection -- helped ambulances get to the scene faster in areas with unreliable network coverage. Teams using the offline maps arrived 4.2 minutes faster on average, and that gap got even bigger specifically during times when the network was actually down.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We assess whether peer mentorship programs improve first-year retention rates among university students from first-generation college backgrounds. Comparing 150 mentored students to a matched group of 150 unmentored first-generation students, mentored students had a 19-percentage-point higher first-year retention rate, with the effect strongest among students matched with a mentor from a similar academic department."',
        response="This study compared 150 first-generation college students who had a peer mentor to 150 similar students who didn't. Students with a mentor were 19 percentage points more likely to still be enrolled after their first year -- and the mentoring worked best when the student and mentor were studying in similar academic departments.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )
    yield SFTExample(
        instruction="What is the `useEffect` hook in React, and when should I use it?",
        response="""`useEffect` lets a component run code in response to rendering -- typically for things that reach outside React itself, like fetching data, setting a timer, or subscribing to an external event.

```jsx
useEffect(() => {
    fetchData();
}, []);
```

The second argument (the "dependency array") controls when the effect re-runs. An empty array `[]` means "run once, after the first render, and never again." Including a variable, like `[userId]`, means "re-run whenever `userId` changes." Omitting the array entirely means "run after every single render," which is rarely what you actually want.

A useful mental model: `useEffect` is for synchronizing your component with something *outside* React's own rendering system -- an API, a browser API like `setTimeout`, a subscription. If you're just computing a value from existing props or state, you usually don't need `useEffect` at all; a plain calculation during render is simpler and avoids an unnecessary extra render cycle.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between `null` and `undefined` in JavaScript?",
        response="""`undefined` means a variable has been declared but never assigned a value -- it's JavaScript's own default for "nothing here yet." `null` means a value was deliberately set to represent "no value," as an explicit choice by whoever wrote the code.

```javascript
let a;
console.log(a); // undefined -- never assigned

let b = null;
console.log(b); // null -- deliberately set to "nothing"
```

A function that doesn't explicitly return anything returns `undefined`; a function parameter that isn't passed in is `undefined`. `null`, on the other hand, only ever appears because someone wrote `= null` on purpose. `== ` treats them as equal (`null == undefined` is `true`), but `===` treats them as different types entirely (`null === undefined` is `false`) -- which is one more reason `===` tends to be the safer default for comparisons in JavaScript.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="Write a Python decorator that measures how long a function takes to run.",
        response="""```python
import time
from functools import wraps

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@timed
def slow_calculation():
    time.sleep(1)
    return 42
```

A decorator is a function that takes another function and returns a modified version of it -- `@timed` above `def slow_calculation()` is shorthand for `slow_calculation = timed(slow_calculation)`. The `wrapper` function runs your timing code before and after calling the original function (`func(*args, **kwargs)`), then returns whatever the original function returned, so calling `slow_calculation()` behaves normally but now also prints its runtime. `@wraps(func)` preserves the original function's name and docstring, which would otherwise get overwritten by `wrapper`'s own metadata.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How does array destructuring work in JavaScript?",
        response="""```javascript
const scores = [85, 92, 78];
const [first, second, third] = scores;
console.log(first); // 85
```

Destructuring unpacks values from an array directly into named variables, based on their position -- `first` gets `scores[0]`, `second` gets `scores[1]`, and so on. It works the same way for function return values that come back as an array:
```javascript
function getMinMax(numbers) {
    return [Math.min(...numbers), Math.max(...numbers)];
}
const [min, max] = getMinMax([3, 7, 1, 9]);
```
You can also skip elements you don't need with an empty slot: `const [first, , third] = scores;` grabs the 1st and 3rd elements while ignoring the 2nd entirely. This is mostly a readability improvement over accessing `scores[0]`, `scores[1]` individually -- functionally equivalent, but the intent reads more clearly at a glance.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do template literals in JavaScript compare to regular string concatenation?",
        response="""```javascript
const name = "Omol";
const score = 85;

const message = `Hello ${name}, your score is ${score}.`;
```

Template literals (backtick strings) let you embed expressions directly inside `${}`, evaluated and inserted into the string automatically -- similar to Python's f-strings. Compare this to concatenation:
```javascript
const message = "Hello " + name + ", your score is " + score + ".";
```
Both produce the same result, but template literals also support real multi-line strings without needing `\\n` escape codes or `+` continuation:
```javascript
const message = `Line one
Line two`;
```
Regular strings with `"` or `'` can't span multiple lines this way at all -- that alone is often enough reason to reach for template literals whenever a string needs to include a variable or span more than one line.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I join a list of words into a single sentence, and split it back apart in Python?",
        response="""```python
words = ["Yaude", "AI", "helps", "students", "learn"]
sentence = " ".join(words)
print(sentence)  # "Yaude AI helps students learn"

back_to_words = sentence.split(" ")
print(back_to_words)  # ["Yaude", "AI", "helps", "students", "learn"]
```

`.join()` is called on the *separator* string, not the list -- `" ".join(words)` reads as "join these words together, with a space between each one." This can feel backwards at first if you're expecting `words.join(" ")`, but it's this way because `.join()` works on any iterable of strings, not just lists specifically.

`.split(" ")` does the reverse, breaking a string apart wherever it finds that separator. Calling `.split()` with no argument at all splits on any whitespace (spaces, tabs, newlines) and also collapses multiple consecutive spaces into one split point, which is usually what you want for cleaning up user-typed text.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this component keep fetching data forever, freezing the page?

```jsx
function StudentList() {
    const [students, setStudents] = useState([]);

    useEffect(() => {
        fetchStudents().then(data => setStudents(data));
    });

    return <ul>{students.map(s => <li key={s.id}>{s.name}</li>)}</ul>;
}
```""",
        response="""There's no dependency array on `useEffect` at all -- so it runs after *every* render, with no stopping condition. Here's the loop that creates: the effect runs, calls `setStudents(data)`, which triggers a re-render, which runs the effect again, which calls `setStudents` again, forever.

Fix by adding an empty dependency array, so it only runs once after the first render:
```jsx
useEffect(() => {
    fetchStudents().then(data => setStudents(data));
}, []);
```
This is one of the most common real-world React bugs, specifically because the broken version often *looks* like it works at first glance in a quick test -- the infinite loop is a fetch happening rapidly in the background, not always an obvious visible crash, until it noticeably freezes the page or exhausts your API's rate limit.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this crash with 'cannot read properties of undefined'?

```javascript
const [name, age] = getStudentInfo();
console.log(name.toUpperCase());
```

Assume `getStudentInfo()` returns a single object `{name: "Omol", age: 22}`, not an array.""",
        response="""Array destructuring (`const [name, age] = ...`) expects the right side to be an array or another iterable, unpacking by *position*. But `getStudentInfo()` returns a plain object, not an array -- objects aren't iterable this way, so `name` and `age` don't get the values you expect (this specific case would actually throw a `TypeError` since objects aren't iterable at all).

Since the data is an object, use object destructuring instead, which unpacks by *key name* rather than position:
```javascript
const { name, age } = getStudentInfo();
console.log(name.toUpperCase());
```
The syntax looks similar (`{}` versus `[]`), but they match completely different things: `[]` destructuring matches by position in an array, `{}` destructuring matches by property name in an object. Mixing them up based on which one you saw most recently is a common, easy mistake.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this print with an extra space at the start?

```python
words = ["", "Hello", "world"]
print(" ".join(words))
```""",
        response="""`words` starts with an empty string `""` as its first element, and `.join()` faithfully includes every element -- including empty ones -- separated by the given separator. Joining `["", "Hello", "world"]` with `" "` produces `" Hello world"`, with a leading space, because there's genuinely an empty string sitting before "Hello" in the list.

This usually traces back to how the list was built -- often from splitting a string that itself started with the separator:
```python
text = " Hello world"
words = text.split(" ")  # ["", "Hello", "world"] -- the leading space creates an empty first element
```
The fix is usually at the source: `text.strip().split(" ")` removes leading/trailing whitespace before splitting, which avoids creating that empty first element in the first place, rather than trying to filter it out afterward.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the difference between a primary and secondary source, and why does it matter which I cite?",
        response="""A primary source is original, first-hand material -- the actual study, the raw data, an original interview transcript, a firsthand account. A secondary source discusses, analyzes, or summarizes primary sources -- a textbook explaining a theory, a news article reporting on a study, a review paper synthesizing multiple studies.

Why it matters: secondary sources can introduce errors or shifts in meaning as they summarize the original. If you cite a textbook's summary of a study's finding, and that summary is slightly imprecise, your paper inherits that imprecision without you realizing it. Where possible, especially for a specific factual claim or statistic, tracing back to the primary source and citing that directly is more rigorous and accurate.

Secondary sources aren't inherently worse -- they're genuinely useful for background context and for surveying a wide body of literature efficiently. But for any specific finding you're building your own argument on, checking the primary source yourself rather than trusting a secondary summary is worth the extra effort.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the difference between a cross-sectional and a longitudinal study design?",
        response="""A cross-sectional study collects data from participants at a single point in time -- a snapshot. A longitudinal study follows the same participants over an extended period, collecting data at multiple points to track change over time.

Cross-sectional studies are faster and cheaper, and are good for measuring the current state of something -- what percentage of students currently use a particular study tool. But they can't tell you about change or causation reliably, since you're only seeing one moment.

Longitudinal studies can actually observe change -- did students who started using the tool improve their grades over the following year? This makes them much stronger for questions about cause and effect over time, but they cost more, take longer, and risk losing participants who drop out partway through ("attrition"), which can itself bias the results if the people who drop out differ systematically from those who stay.

Choosing between them comes down to your actual research question: "what is the current state of X" fits cross-sectional; "how does X change, and why" fits longitudinal.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a control group, and why do experimental studies need one?",
        response="""A control group doesn't receive the intervention being tested -- it exists specifically to show what would have happened *without* the intervention, so you can attribute any difference to the intervention itself rather than to unrelated factors (like time passing, or a general trend affecting everyone).

Without a control group, you can't actually isolate the intervention's effect. If students' test scores improve after a new teaching method, was that the teaching method -- or would scores have improved anyway that semester, for unrelated reasons? A control group (students not receiving the new method, otherwise as similar as possible to the treatment group) lets you compare the two and attribute the difference specifically to the intervention.

The strongest designs randomly assign participants to treatment or control groups, which helps ensure the two groups are genuinely comparable at the start -- if participants choose their own group (like opting into a program), any observed difference later might reflect who chose to participate, not the program's actual effect.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether providing students with downloadable offline lecture recordings, rather than requiring live-streamed attendance, affects course completion rates in programs with unreliable internet access. Comparing 220 students given offline access to 220 requiring live attendance, offline-access students had a 26% higher course completion rate, with the gap widest among students living outside major urban centers."',
        response="This study compared 220 students who could download lecture recordings to watch offline against 220 students who had to attend live streamed classes, in a program where internet access wasn't always reliable. The students with offline access completed the course 26% more often -- and this advantage was even bigger for students living outside major cities, where internet tends to be less reliable.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate the relationship between code review turnaround time and software defect rates in student software engineering projects. Analyzing 60 student teams, teams with a code review turnaround under 24 hours had 31% fewer post-submission bugs than teams with turnaround exceeding 48 hours, suggesting review speed itself -- not just review occurrence -- meaningfully affects code quality outcomes."',
        response="Researchers studied 60 student software teams to see if how quickly team members reviewed each other's code affected how many bugs ended up in the final project. Teams that reviewed code within 24 hours had 31% fewer bugs than teams that took more than 48 hours -- suggesting that just doing code review isn't enough, doing it quickly actually matters for catching problems early.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper evaluates whether pairing new employees with a formal onboarding buddy affects 90-day retention rates in entry-level technology roles. Comparing 180 employees with an assigned onboarding buddy to 180 without, buddy-paired employees had a 23-percentage-point higher 90-day retention rate, with the effect strongest among employees who were the first in their family to work in a technology role."',
        response="This study looked at whether pairing new tech employees with an onboarding buddy affected whether they were still at the company 90 days later. Employees who had a buddy stayed at a rate 23 percentage points higher than those who didn't -- and the buddy system helped the most for employees who were the first in their family to work in a tech job.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )
    yield SFTExample(
        instruction="How do I create a new Git branch and switch to it, to work on a feature without affecting main?",
        response="""```
git branch feature-login
git checkout feature-login
```

Or as a single combined command:
```
git checkout -b feature-login
```

`-b` creates the branch and switches to it in one step. A branch is essentially a movable pointer to a commit -- creating one doesn't copy your files, it just gives you a separate line of history to commit to, starting from wherever you were when you created it. Work you commit on `feature-login` won't appear on `main` until you explicitly merge it back, which is exactly the point: you can experiment, break things, and commit freely without touching the stable `main` branch until you're ready.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I merge a finished feature branch back into main?",
        response="""```
git checkout main
git merge feature-login
```

You switch to the branch you want to merge *into* first (`main`), then run `merge` naming the branch you want to bring in (`feature-login`). Git combines the two histories -- if the changes don't overlap with anything that happened on `main` since the branches diverged, this completes automatically with no extra work.

If both branches changed the same lines, Git can't automatically decide which version to keep, and you'll get a merge conflict -- Git marks the conflicting section directly in the affected file, you manually choose what the final version should be, then `git add` the resolved file and run `git commit` to complete the merge. Conflicts aren't a sign something went wrong; they're Git correctly asking you to make a judgment call it can't make on its own.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I check if a string looks like a valid phone number using a regular expression in Python?",
        response="""```python
import re

def is_valid_phone(number):
    pattern = r'^\\+?[\\d\\s-]{7,15}$'
    return re.match(pattern, number) is not None
```

Breaking down the pattern: `\\+?` matches an optional leading `+`, `[\\d\\s-]` matches any digit, space, or hyphen, `{7,15}` requires between 7 and 15 of those characters, and `^`/`$` anchor the match to the entire string (without them, the pattern could match just part of a longer, invalid string).

Like the email validation pattern, this catches obviously malformed input but doesn't guarantee the number is real or reachable -- phone number formats vary significantly by country, so a pattern this simple is meant to catch typos and obvious garbage, not to serve as a complete international phone number validator.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I reverse a string in Python without writing a recursive function?",
        response="""```python
text = "Yaude"
reversed_text = text[::-1]
print(reversed_text)  # "eduaY"
```

`[::-1]` is Python's slice notation with a step of `-1`, meaning "walk through the string backwards, one character at a time." The general slice syntax is `[start:stop:step]` -- leaving `start` and `stop` empty means "the whole string," and `-1` for `step` means "in reverse."

This is both simpler and faster than the recursive version shown earlier -- recursion is genuinely useful for understanding the underlying technique, but for a real task like string reversal, Python's built-in slicing is the practical, idiomatic choice almost everyone actually uses.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I get the unique values from a list, removing duplicates?",
        response="""```python
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = list(set(numbers))
```

A `set` can only contain each distinct value once -- converting the list to a set automatically drops duplicates, and converting it back to a list gives you a plain list again. One thing worth knowing: sets don't preserve order, so `unique` might not come out in the same sequence as the original list.

If order matters, use a dictionary instead (in modern Python, dictionaries preserve insertion order):
```python
unique = list(dict.fromkeys(numbers))  # preserves original order
```
`dict.fromkeys(numbers)` creates a dictionary with each number as a key (again dropping duplicates automatically, since dict keys must be unique), and converting that back to a list gives you the unique values in their original order.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this crash when trying to add a grade?

```python
grades = (85, 92, 78)
grades.append(95)
```""",
        response="""`grades` is a tuple, defined with `()` instead of `[]` -- and tuples are immutable, meaning they can't be changed after creation. `.append()` is a list method; tuples don't have it at all, so this raises `AttributeError: 'tuple' object has no attribute 'append'`.

If you need to add items, either use a list from the start:
```python
grades = [85, 92, 78]
grades.append(95)
```
Or, if you specifically need a tuple as the final result but want to build it up, create a new tuple by combining:
```python
grades = (85, 92, 78)
grades = grades + (95,)  # creates a new tuple, doesn't modify the original
```
The general rule: use a list when the collection needs to change over time, and a tuple when it represents a fixed, unchanging group of values -- the immutability is often a deliberate feature (like preventing accidental modification of coordinates or a fixed configuration), not just an inconvenience.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this nested loop only ever compare the last row against itself?

```python
grid = [[1, 2], [3, 4], [5, 6]]
for row in grid:
    for row in grid:
        print(row)
```""",
        response="""Both loops use the same variable name, `row` -- the inner loop's `row` overwrites the outer loop's `row` on every iteration, so by the time the inner loop finishes, the outer loop's own `row` has been silently changed out from under it too. This is a naming collision, not a logic error in the loop structure itself.

Fix by giving each loop variable a distinct name:
```python
for outer_row in grid:
    for inner_row in grid:
        print(outer_row, inner_row)
```
Now each loop tracks its own position independently, without interfering with the other. This is a genuinely easy mistake to make when nesting nested loops over similar data -- always double-check that inner and outer loop variables have different names, especially when they're iterating over similarly-named collections.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this error handling hide the real problem instead of fixing it?

```python
def get_student_average(grades):
    try:
        return sum(grades) / len(grades)
    except ZeroDivisionError:
        return None
    except Exception:
        return None
```""",
        response="""Both `except` blocks do the exact same thing, which suggests the second one (`except Exception`) isn't really intentional -- it silently swallows *any* other error too, including genuine bugs elsewhere in the function that have nothing to do with an empty grades list. If `grades` accidentally contained a string instead of a number, this would silently return `None` instead of surfacing the real `TypeError` that would help you find the actual bug.

Better to only catch the specific error you're actually expecting and know how to handle:
```python
def get_student_average(grades):
    if not grades:
        return None
    return sum(grades) / len(grades)
```
This sidesteps the division entirely by checking upfront, rather than catching the error after the fact -- and it means genuinely unexpected errors (like bad data types in the list) still surface loudly instead of being silently converted into a misleading `None`.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What belongs in a 'future work' section, and how is it different from a limitations section?",
        response="""A limitations section explains what your *current* study couldn't establish or address, given constraints you had. A future work section is forward-looking -- it proposes specific next steps that would build on what you found, for someone (possibly you) to actually pursue later.

The key difference is direction: limitations look backward at what wasn't covered; future work looks forward at what should happen next. They often connect directly -- a limitation ("small sample size limits generalizability") frequently leads straight into a future work suggestion ("a larger-scale study across multiple regions would test whether these findings generalize").

Avoid vague suggestions like "more research is needed" without specifics -- a strong future work section names a concrete next study, a specific population it should examine, or a specific methodological improvement, giving a reader (including future you) an actual starting point rather than a generic gesture at more research existing somewhere.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the difference between reliability and validity when designing a way to measure something?",
        response="""Reliability means your measurement is *consistent* -- if you measured the same thing again under the same conditions, you'd get a similar result. Validity means your measurement actually captures what you *intend* to measure, not something else entirely.

A measurement can be reliable without being valid: a bathroom scale that's consistently 5kg off every single time is highly reliable (same result every time) but not valid for measuring true weight. A survey question that people interpret inconsistently, on the other hand, might be measuring the right concept in theory but unreliably in practice, since different people are effectively answering different questions.

Both matter, but they fail differently: low reliability means your data is noisy and hard to trust at all; low validity means your data is consistent but consistently measuring the wrong thing. Before trusting a finding, it's worth asking both questions separately -- "would this measurement give the same result again?" and "does this measurement actually capture what I think it does?\"""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I interpret a confidence interval in plain terms, for someone who isn't a statistician?",
        response="""A confidence interval gives you a range, rather than a single number, reflecting genuine uncertainty in an estimate based on sample data. If a study reports "average improvement: 12% (95% CI: 8%-16%)," that means the study's best estimate is 12%, but the true value in the broader population is plausibly anywhere in that 8%-16% range, given the data collected.

A common misinterpretation worth avoiding: a 95% confidence interval does *not* mean "there's a 95% chance the true value falls in this range." The more precise (if less intuitive) interpretation is: if you repeated this exact study many times, about 95% of the confidence intervals you'd calculate would contain the true population value.

Practically, the width of the interval matters as much as its center: a narrow interval (8%-9%) reflects a precise, confident estimate; a wide interval (2%-25%) reflects real uncertainty, even if the midpoint looks similar. A wide interval is honest information worth reporting, not a flaw to hide.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is thematic analysis, and how do I actually do it with interview data?",
        response="""Thematic analysis is a common method for finding patterns ("themes") across qualitative data, like interview transcripts. A practical process:

1. **Get familiar with the data.** Read (or re-read) all transcripts before starting any formal coding -- don't jump straight to labeling.
2. **Code the data.** Go through systematically, tagging meaningful segments with short descriptive labels ("frustration with slow internet," "reliance on family for tech help"). One segment can get multiple codes if relevant.
3. **Group codes into candidate themes.** Look for codes that cluster around a shared underlying idea -- several related codes might combine into one broader theme like "trust in technology."
4. **Review themes against the full dataset.** Check whether each candidate theme genuinely holds up across your data, or whether it was really only reflecting one or two vivid quotes that aren't representative.
5. **Name and define each final theme clearly**, and select representative quotes that illustrate it in your write-up.

The most common shortcut that weakens thematic analysis is skipping step 4 -- claiming a theme based on a few memorable quotes without checking it against the dataset as a whole.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether providing new small-business owners with a structured financial record-keeping template affects loan approval rates. Comparing 130 businesses using the template to 130 using informal record-keeping, template users had a 44% higher loan approval rate, with lenders citing record clarity, rather than business size or revenue alone, as the deciding factor most often."',
        response='Researchers compared 130 small businesses that used a structured template for keeping financial records against 130 that kept informal records, to see how it affected their chances of getting a loan. Businesses using the template got approved 44% more often -- and when lenders explained their decisions, they said it was mainly the clarity of the records that mattered, not just how big or profitable the business was.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether peer code review training for junior developers reduces production bug rates in their first six months on the job. Comparing 95 developers who received structured review training to 95 who did not, trained developers introduced 34% fewer production bugs, with the largest gap observed in the first two months of employment specifically."',
        response="This study looked at whether teaching new junior developers how to properly review code helped reduce bugs in the software they wrote during their first six months on the job. Developers who got this training introduced 34% fewer bugs into production compared to those who didn't -- and the difference was biggest in just the first two months, when developers are typically still learning the ropes.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates the effect of bilingual technical documentation on tool adoption rates among non-native English-speaking developer communities. Comparing adoption of an open-source tool before and after bilingual documentation was introduced, weekly active users from the target language community increased by 58% over the following three months, with no corresponding increase observed in English-speaking user regions during the same period."',
        response="Researchers tracked what happened when an open-source tool added documentation in a second language, alongside English. Weekly active users from that language community grew by 58% over the next three months -- and importantly, usage among English-speaking users didn't change at all during the same period, suggesting the growth was genuinely driven by the new language support, not some other unrelated factor.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )
    yield SFTExample(
        instruction="What is a lambda function in Python, and when is it actually useful?",
        response="""```python
square = lambda x: x * x
print(square(5))  # 25
```

A lambda is a small, unnamed function defined inline, in a single expression -- `lambda x: x * x` is equivalent to writing:
```python
def square(x):
    return x * x
```
Lambdas are mainly useful when you need a quick, throwaway function as an argument to something else, and defining a full named function would feel like unnecessary ceremony for something used once:
```python
students.sort(key=lambda s: s["grade"])
```
Here, the lambda exists purely to tell `.sort()` what to compare by, right where it's used. As a rule of thumb: if the logic is more than a single simple expression, or you're using it in more than one place, a regular named `def` function is usually clearer -- lambdas are for small, one-off cases, not a replacement for normal functions generally.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a one-line if/else to assign a value, instead of a full if/else block?",
        response="""```python
age = 16
status = "adult" if age >= 18 else "minor"
```

This is a conditional expression (sometimes called a ternary operator) -- it reads as "status is 'adult' if age is 18 or older, otherwise 'minor'." It's equivalent to the longer form:
```python
if age >= 18:
    status = "adult"
else:
    status = "minor"
```
Both do exactly the same thing; the one-line version is just more compact for simple value assignments. It's worth reaching for this specifically when you're assigning one of two values based on a condition -- for anything more complex than that (multiple conditions, or actions beyond a simple assignment), a regular `if`/`else` block stays more readable.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I loop through a list while also keeping track of each item's position?",
        response="""```python
students = ["Omol", "Andrew", "Sara"]

for index, name in enumerate(students):
    print(f"{index + 1}. {name}")
```

`enumerate()` wraps a list so each iteration gives you both the position (`index`, starting from 0 by default) and the value (`name`) together, instead of just the value alone. `index + 1` here just shifts the display to start counting from 1, which reads more naturally for a numbered list than starting at 0.

If you need it to start counting from something other than 0 directly, `enumerate()` accepts a `start` argument: `enumerate(students, start=1)` gives you `1, 2, 3` directly without needing the `+ 1` adjustment yourself.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is CORS, and why do browsers block requests because of it?",
        response="""CORS (Cross-Origin Resource Sharing) is a browser security rule that blocks a webpage from making requests to a different domain than the one it was loaded from, unless that other domain explicitly allows it. "Different origin" means a different domain, protocol, or port -- `https://yaude-ai.vercel.app` and `https://overlook-unify-reboot.ngrok-free.dev` count as different origins from each other, for example.

This exists to protect users: without it, any malicious website you visited could silently make authenticated requests to your bank or email in the background, using cookies your browser already holds for those sites. CORS forces the *target* server to explicitly say "yes, I allow requests from this specific origin" before the browser lets the response through.

The server signals this permission via response headers, most importantly `Access-Control-Allow-Origin`. If that header doesn't list the requesting page's origin, the browser blocks the response from reaching your JavaScript code -- even if the server actually processed the request successfully, which is exactly why a CORS error can appear even when the backend logs show everything worked fine.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""My frontend request fails with a CORS error in the browser console, but my backend logs show the request succeeded. Why the mismatch, and how do I fix it?

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
)
```

The frontend is actually deployed at `https://my-app.vercel.app`, not localhost.""",
        response="""This mismatch is normal, not a contradiction -- CORS is enforced by the *browser*, not the server. Your backend genuinely did process the request and send back a valid response; the browser then checked that response's headers, saw the requesting origin (`https://my-app.vercel.app`) wasn't in the allowed list, and blocked your JavaScript from ever seeing that response. The server did its job; the browser is the one refusing to hand over the result.

The fix is adding the actual deployed origin to the allowed list:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://my-app.vercel.app"],
)
```
The allowed origin has to match *exactly* -- including the protocol (`http` vs `https`) and no trailing slash. This is a very common real deployment bug: code that works perfectly on `localhost` during development breaks once deployed, specifically because the deployed URL was never added to the backend's allowed origins list.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this function crash when `discount` is 0, even though 0 is a valid discount?

```python
def apply_discount(price, discount):
    if discount:
        return price - (price * discount)
    return price
```

Calling `apply_discount(100, 0)` returns `100` instead of raising an error, but the developer expected the `if discount:` branch to run since `0` was explicitly passed in.""",
        response="""This isn't a crash, but it is a real logic bug -- and it's a classic one. `if discount:` treats `0` as falsy (Python considers `0`, `""`, `None`, and empty collections all falsy in a boolean context), so `if discount:` is `False` when `discount` is `0`, even though `0` is a perfectly valid, meaningful discount value the caller explicitly provided.

The function happens to return the right answer here purely by coincidence (a 0% discount does leave the price unchanged), but the *logic* is wrong -- it's checking "is discount truthy" when it should be checking "was a discount value actually provided."

Fix by explicitly checking against `None` instead of relying on truthiness:
```python
def apply_discount(price, discount=None):
    if discount is not None:
        return price - (price * discount)
    return price
```
This distinguishes "no discount was given" from "a discount of exactly 0 was given" -- a distinction that matters whenever `0` (or an empty string, or an empty list) is a legitimate, meaningful value rather than a stand-in for "nothing." """,
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this still print the string with leading/trailing spaces?

```python
name = "  Omol  "
name.strip()
print(name)
```""",
        response="""`.strip()` doesn't modify `name` in place -- like other string methods, it returns a *new* string with the whitespace removed, and leaves the original completely unchanged. Since the result of `.strip()` was never assigned to anything, it's computed and immediately discarded.

Fixed version:
```python
name = "  Omol  "
name = name.strip()
print(name)  # "Omol"
```
This is the exact same immutability principle behind why strings can't be modified in place at all -- every string method that seems to "change" a string (`.strip()`, `.replace()`, `.upper()`, and others) actually returns a new string, and you always need to capture that return value with `=` if you want to keep the result.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I write interview questions that get genuine, detailed answers instead of a one-word response?",
        response="""The core distinction is open-ended versus closed questions. A closed question can be answered in a word or two: "Do you use mobile banking?" invites a simple yes/no. An open-ended question requires the person to actually explain: "Can you walk me through the last time you used mobile banking?"

A few practical techniques for writing stronger interview questions:
1. **Start with "how," "what," or "tell me about"** rather than "do you" or "did you," which invite yes/no answers.
2. **Ask about specific past experiences, not general opinions.** "Tell me about a time X happened" tends to get more concrete, useful detail than "what do you think about X."
3. **Avoid stacking multiple questions into one.** "Do you use the app often, and if so, why, and what would you change?" -- pick one focus per question and follow up naturally based on what they say.
4. **Save your most important questions for partway through**, not the very first question -- people often warm up and give more detailed answers a few minutes into a conversation, not immediately.

A useful test while drafting: could this question honestly be answered with just "yes" or "no"? If so, it usually needs rephrasing before you actually use it.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What does it mean to 'operationalize' a variable in research, and why does it matter?",
        response="""Operationalizing means turning an abstract concept into something concrete and measurable. "Student engagement" is an abstract idea -- you can't directly measure it. Operationalizing it means deciding, specifically, what you'll actually count as evidence of engagement: maybe attendance rate, number of questions asked per class, or time spent on course materials.

This matters because different, reasonable operationalizations of the same abstract concept can produce genuinely different findings. If one study operationalizes "engagement" as attendance and another operationalizes it as questions asked, they might reach different conclusions about the same underlying concept -- not because either is wrong, but because they're actually measuring different things while using the same word.

When writing your methodology, state your operational definition explicitly, not just the abstract concept: "engagement was measured as the number of discussion posts per student per week" tells a reader exactly what you counted, rather than leaving them to guess what "engagement" meant in your specific study.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is publication bias, and why should I be cautious about it when reviewing existing literature?",
        response="""Publication bias is the tendency for studies with positive, statistically significant, or "interesting" results to get published more often than studies that found no effect or a null result. A researcher who runs a study and finds "no significant difference" is often less likely to submit it for publication, and journals are historically less likely to accept it even when submitted.

The practical consequence: the published literature on a topic can look more consistently positive than reality actually is, simply because negative or null findings are underrepresented, not because the effect is genuinely as strong or consistent as the literature makes it appear.

When reviewing literature for your own work, it's worth explicitly considering this: if you find five published studies all showing a positive effect, it's worth asking whether unpublished or unsuccessful studies on the same question might exist that you're not seeing. Some fields address this partly through "pre-registration" (researchers publicly commit to a study design before collecting data, regardless of outcome), which is worth mentioning if you're evaluating how much to trust a given body of literature.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is ecological validity, and why might a well-controlled lab study still have low ecological validity?",
        response="""Ecological validity is the extent to which a study's findings generalize to real-world settings, outside the controlled conditions of the study itself. A study can be very rigorous internally -- well-controlled, minimal confounding variables -- while still having low ecological validity if the setting is too artificial to reflect how things actually work in practice.

A concrete example: testing a new teaching method in a quiet lab with one researcher observing a single student is easier to control precisely, but that setting is quite different from a real classroom with 40 students, background noise, and normal daily distractions. The method might work beautifully in the lab and behave very differently once actually deployed in a real classroom.

This creates a genuine trade-off researchers have to navigate: more controlled settings make it easier to isolate a specific cause, but often at the cost of how confidently you can claim the finding applies outside that controlled setting. Naming this trade-off honestly in your own methodology section -- rather than assuming lab results automatically transfer to real-world settings -- is a mark of careful research writing.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether requiring a cooling-off period before large mobile money transfers reduces fraud victimization among first-time users. Comparing transaction data before and after a 10-minute delay was introduced for transfers above a set threshold, reported fraud incidents dropped by 29% in the following quarter, with no measurable change in overall transfer volume, suggesting the delay deterred fraudulent transfers specifically rather than discouraging legitimate use."',
        response="Researchers looked at what happened when a mobile money service added a 10-minute delay before large transfers went through, as a way to give people time to reconsider. Fraud reports dropped by 29% in the following months -- and importantly, the overall number of transfers people made didn't change at all, suggesting the delay specifically stopped fraudulent transfers rather than just discouraging people from using the service.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether providing students with worked example solutions, in addition to standard assignment instructions, improves first-attempt completion rates on introductory programming assignments. Comparing 260 students given worked examples to 260 given instructions only, worked-example students had a 37% higher first-attempt success rate, with no significant difference in final course grades between the two groups by semester end."',
        response='This study tested whether giving beginner programming students a fully worked example, in addition to the assignment instructions, helped them succeed on their first try. Students with the worked example succeeded on their first attempt 37% more often -- but by the end of the semester, both groups ended up with similar final grades, suggesting the worked examples helped students get started faster without necessarily changing how much they ultimately learned.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper evaluates the effect of open-source contribution requirements in a university software engineering course on students\' post-graduation employment outcomes. Comparing 140 students who completed a contribution requirement to 140 who took the standard course without it, contribution-requirement students reported job offers within three months of graduation at a rate 21 percentage points higher, with the strongest effect among students without prior internship experience."',
        response="Researchers compared university software engineering students who were required to contribute to open-source projects as part of their coursework to students who took a standard version of the course without that requirement. The students with the open-source requirement got job offers within three months of graduating at a rate 21 percentage points higher -- and this benefit was strongest specifically for students who hadn't already done an internship.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether displaying estimated wait times affects patient dropout rates in public health clinic queues. Comparing 15 clinics that introduced estimated wait time displays to 15 that did not, clinics with wait time displays saw an 18% reduction in patients leaving before being seen, with the effect concentrated among patients waiting longer than 45 minutes."',
        response='This study looked at whether showing patients an estimated wait time in public health clinics reduced how often people gave up and left before being seen. Clinics that added wait time displays saw 18% fewer patients leave early -- and this effect was strongest specifically among patients who ended up waiting more than 45 minutes, suggesting that just knowing how long the wait will be helps people decide to stick it out.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
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
