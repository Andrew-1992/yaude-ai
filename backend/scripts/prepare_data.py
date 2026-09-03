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

    yield SFTExample(
        instruction="How do I pass a variable number of arguments to a Python function?",
        response="""```python
def total(*numbers):
    return sum(numbers)

print(total(1, 2, 3))       # 6
print(total(1, 2, 3, 4, 5)) # 15
```

`*numbers` collects any number of positional arguments into a tuple inside the function -- you can call `total()` with 2 arguments or 20, and it just works. For keyword arguments, `**kwargs` does the same thing but collects them into a dictionary:
```python
def describe(**details):
    for key, value in details.items():
        print(f"{key}: {value}")

describe(name="Omol", age=22)
```
The names `*args` and `**kwargs` are just convention, not required -- what matters is the `*` and `**`. Use `*args` when the caller might pass a varying number of plain values, and `**kwargs` when they might pass a varying number of named options.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I build a dictionary from a list, transforming each value, in one line?",
        response="""```python
names = ["omol", "andrew", "sara"]
capitalized = {name: name.capitalize() for name in names}
# {"omol": "Omol", "andrew": "Andrew", "sara": "Sara"}
```

This is a dictionary comprehension -- the same idea as a list comprehension, but building key-value pairs instead of a flat list. `name: name.capitalize()` defines what each key and value should be, evaluated for every `name` in the list.

Equivalent to the longer form:
```python
capitalized = {}
for name in names:
    capitalized[name] = name.capitalize()
```
Both produce the same dictionary; the comprehension is just more compact once you're comfortable reading them. As with list comprehensions, if the transformation logic gets complex, a regular loop is usually more readable than forcing it into one dense line.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What's the difference between using `print()` statements and a proper logging library for debugging?",
        response="""`print()` is fine for a quick, temporary check while you're actively writing code, but it has real limitations in anything beyond a small script: there's no way to turn print statements off without deleting them, no indication of severity (a routine status update looks identical to a serious error), and no record kept after the program exits.

Python's built-in `logging` module addresses all three:
```python
import logging
logging.basicConfig(level=logging.INFO)

logging.info("Server started")
logging.warning("Config file not found, using defaults")
logging.error("Failed to connect to database")
```
Each call has a severity level, and you can globally control which levels actually get shown (`level=logging.WARNING` would hide `.info()` calls entirely, without deleting them from the code). Logging can also write to a file automatically, so you have a real record to review later, not just whatever happened to be visible in the terminal when it scrolled by.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this crash with a KeyError even though I checked the key exists first?

```python
config = {"api_url": "https://api.example.com"}

if "api_key" in config:
    key = config["api_key"]
print(config["api_key"])
```""",
        response="""The `if "api_key" in config:` check only guards the line inside that block -- `key = config["api_key"]` never actually runs, since `"api_key"` genuinely isn't in the dictionary. But the last line, `print(config["api_key"])`, is completely outside that `if` block (notice it's not indented under it), so it runs unconditionally regardless of whether the key exists, and raises `KeyError: 'api_key'`.

This is really an indentation/scope issue: the check only protects code that's actually indented inside it. Fix by either indenting the print statement into the same block, or using `.get()` to handle the missing case gracefully:
```python
print(config.get("api_key", "not set"))
```
Whenever you write a defensive check like `if key in dict:`, double-check that everything depending on that key's existence is genuinely inside the protected block -- a line sitting just outside it, even by accident, completely defeats the purpose of the check.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does `git stash` sometimes seem to make my changes disappear?

```
git stash
git checkout other-branch
```

After switching back, the developer can't find their work.""",
        response="""`git stash` doesn't delete your changes -- it temporarily sets them aside, restoring your working directory to match your last commit, and saves the actual changes in a separate stash list. They're not gone; they're just not visible in your files anymore until you bring them back.

To see what's stashed and restore it:
```
git stash list
git stash pop
```
`git stash list` shows every stashed set of changes (you can stash multiple times). `git stash pop` re-applies the most recent stash and removes it from the list; `git stash apply` re-applies it *without* removing it from the list, useful if you want to apply the same stashed changes to more than one branch.

The confusion usually happens because `git stash` genuinely does make your working directory look clean -- that's the entire point, so you can safely switch branches without losing uncommitted work, but it's easy to forget the stash exists if you don't check `git stash list` afterward.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the purpose of a `.gitignore` file?",
        response="""`.gitignore` tells Git which files or folders to never track, even if they exist in your project directory -- Git simply won't show them as changes, won't let you accidentally `git add` them by wildcard, and won't include them in commits.

```
# .gitignore
node_modules/
.env
__pycache__/
*.log
```

This matters for a few real, distinct reasons: `node_modules/` and similar dependency folders are huge and fully regeneratable from a manifest file (`package.json`), so committing them bloats your repository for no benefit. `.env` often contains real secrets (API keys, database passwords) that should never end up in git history at all. Log files and compiled bytecode (`__pycache__/`) are machine-generated and just create noise in your commit history. A well-maintained `.gitignore` keeps your repository focused on the actual source code that needs version control.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What does `requirements.txt` do in a Python project?",
        response="""`requirements.txt` lists every external package your project depends on, usually with specific version numbers, so anyone else (including you, on a different machine) can install the exact same dependencies with one command:
```
pip install -r requirements.txt
```

A typical file looks like:
```
fastapi==0.115.0
requests==2.32.3
bcrypt==4.2.0
```

Pinning specific versions (`==0.115.0` rather than just `fastapi`) matters because a newer version of a dependency might change behavior in ways that break your code -- pinning ensures everyone installs the exact version your code was actually built and tested against, rather than whatever happens to be newest at install time. This is part of why setting up a fresh virtual environment and reinstalling from `requirements.txt` is the standard way to get a project running on a new machine, rather than trying to manually recreate someone's installed packages.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How does inheritance work in Python, and when should I actually use it?",
        response="""```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):
    def speak(self):
        return f"{self.name} barks"
```

`Dog(Animal)` means `Dog` inherits from `Animal` -- it automatically gets `Animal`'s `__init__` and any methods it doesn't define itself. Here, `Dog` overrides `speak()` with its own version, while still inheriting `__init__` unchanged.

```python
d = Dog("Rex")
print(d.speak())  # "Rex barks"
```

Inheritance is genuinely useful when several classes share real common structure and behavior, with some specific differences -- multiple animal types sharing a `name` and basic structure, but differing in how they `speak()`. It's easy to overuse, though: if two classes don't actually share meaningful behavior, forcing an inheritance relationship between them just to avoid repeating a little code usually creates more confusion than it saves.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between a null hypothesis and the hypothesis I'm actually trying to support?",
        response="""The null hypothesis is the default assumption of "no effect" or "no difference" -- your study's job is to gather enough evidence to reject it, not to directly prove your own hypothesis true. This might feel backwards at first, but it reflects a genuinely important principle: you can accumulate evidence against "no effect," but you can never fully prove a positive claim true with statistics alone -- only make it more or less likely.

Concretely: if you're testing whether a new teaching method improves scores, the null hypothesis is "the teaching method has no effect on scores." Your alternative hypothesis is "the teaching method does affect scores." Your statistical test doesn't directly test the alternative hypothesis -- it calculates how likely your observed data would be *if* the null hypothesis were actually true. A small enough probability (typically below 0.05) leads you to reject the null hypothesis, which is treated as support for the alternative, not direct proof of it.

This is why research papers say "we reject the null hypothesis" or "we failed to reject the null hypothesis" rather than "we proved our hypothesis" -- the language reflects genuine statistical humility about what a single study can actually establish.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between a Type I and Type II error in research?",
        response="""A Type I error is a false positive -- concluding there's a real effect when there actually isn't one (incorrectly rejecting a true null hypothesis). A Type II error is a false negative -- concluding there's no effect when there actually is one (failing to reject a false null hypothesis).

A useful analogy: think of a court trial. A Type I error is convicting an innocent person (concluding guilt when there was none). A Type II error is acquitting a guilty person (concluding innocence when guilt was real).

These two error types trade off against each other in a real, practical way: making your significance threshold stricter (say, requiring p < 0.01 instead of p < 0.05) reduces Type I errors but increases Type II errors, since you're now requiring stronger evidence before concluding an effect is real -- genuine effects that produce moderate evidence get missed more often. Which error matters more depends on context: in medical testing, a Type II error (missing a real disease) is often considered far worse than a Type I error (a false alarm that gets ruled out by follow-up testing), which is why different fields sometimes use different conventional significance thresholds.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is inter-rater reliability, and why does it matter when coding qualitative data?",
        response="""Inter-rater reliability measures how consistently different people, coding the same qualitative data independently, arrive at the same codes or categories. If two researchers read the same set of interview transcripts and apply your coding scheme, but consistently disagree on how to categorize the same passages, that suggests your coding categories are too ambiguous, or too dependent on individual judgment, to trust as objective findings.

A common practical approach: have two people independently code a sample of the same data, then calculate agreement (sometimes using a statistic like Cohen's Kappa, which adjusts for the agreement you'd expect by chance alone). Low agreement means the coding scheme needs refining -- clearer definitions, more examples of what does and doesn't count as each category -- before applying it to the full dataset.

This matters because a reader can't verify your coding decisions themselves the way they could check a numeric calculation -- reporting inter-rater reliability is how you demonstrate that your qualitative analysis wasn't just one person's individual, potentially idiosyncratic interpretation, even though qualitative analysis inherently involves more judgment than a purely quantitative measurement.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="Should I write my research paper in active or passive voice?",
        response="""Modern academic writing across most fields has shifted toward preferring active voice in most cases, though passive voice still has legitimate specific uses. Compare:

- **Passive:** "The survey was administered to 200 participants."
- **Active:** "We administered the survey to 200 participants."

Active voice is generally more direct and easier to read -- it's clearer who did what. Passive voice was traditionally favored in scientific writing partly to sound more "objective" by removing the researcher from the sentence, but this convention has weakened considerably; many journals and style guides now actively encourage active voice for clarity.

Passive voice still makes sense when the actor genuinely doesn't matter or isn't known: "Participants were recruited through community health clinics" works fine in passive, since who specifically did the recruiting isn't the point of the sentence. The practical guidance: default to active voice, and use passive deliberately when it genuinely serves the sentence, not habitually because it "sounds more academic." """,
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether including a progress bar in multi-step online forms affects completion rates among first-time users. Comparing 400 form submissions with a visible progress indicator to 400 without, forms with progress bars had a 33% higher completion rate, with the largest drop-off in both groups occurring specifically at the payment information step."',
        response='Researchers compared 400 people filling out a multi-step online form that showed a progress bar to 400 filling out the same form without one. Forms with the progress bar were completed 33% more often -- though in both versions, most people who gave up did so at the same specific step: entering payment information.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether requiring students to explain their code aloud before submitting an assignment (a technique known as rubber duck debugging) affects the number of bugs found before submission. Comparing 90 students required to explain their code to a peer before submitting to 90 who submitted directly, the explanation group caught 41% more bugs prior to submission, with no significant difference in time spent on the assignment overall."',
        response="This study tested whether making students explain their code out loud to another person before submitting -- a technique sometimes called rubber duck debugging -- helped them catch more of their own bugs. Students who explained their code first caught 41% more bugs before submitting, and interestingly, this didn't even take them significantly more total time to finish the assignment.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction="""Why does this loop only process every other item in the list?

```python
items = ["a", "b", "c", "d", "e"]
i = 0
while i < len(items):
    print(items[i])
    i += 2
```""",
        response="""`i += 2` increments by 2 each time, not 1 -- so the loop visits indices 0, 2, 4 and skips 1 and 3 entirely, printing "a", "c", "e" while missing "b" and "d".

If the intent was to process every item, the fix is straightforward:
```python
i = 0
while i < len(items):
    print(items[i])
    i += 1
```
If skipping every other item was actually intentional (a real, valid pattern sometimes used deliberately), then the original code is correct as written -- the "bug" here is really about mismatched intent versus implementation. Whenever a loop produces fewer results than expected, checking the increment step size is one of the first things worth verifying, especially in a `while` loop where the increment isn't as visually obvious as it is in a `for i in range(...)` loop.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )
    yield SFTExample(
        instruction="How do I make a POST request with a JSON body using Python's requests library?",
        response="""```python
import requests

payload = {"name": "Omol", "email": "omol@example.com"}
response = requests.post("https://api.example.com/students", json=payload)

if response.status_code == 201:
    print("Created:", response.json())
else:
    print("Failed:", response.status_code, response.text)
```

Passing `json=payload` does two things automatically: it serializes your Python dictionary into a JSON string, and it sets the `Content-Type: application/json` header so the server knows how to interpret the request body -- you don't need to do either step manually. `201 Created` is the conventional success status for a POST that created a new resource (as opposed to `200 OK`, more typical for a successful GET). Checking `response.status_code` before trusting the response is worth doing here too, same as with GET requests -- a failed request can still return a body, just one describing the error rather than the data you expected.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I combine two dictionaries in Python, with the second one's values taking priority on any overlapping keys?",
        response="""```python
defaults = {"theme": "light", "font_size": 12}
user_settings = {"font_size": 16}

merged = {**defaults, **user_settings}
# {"theme": "light", "font_size": 16}
```

`{**defaults, **user_settings}` unpacks both dictionaries into a new one -- keys from `user_settings` overwrite matching keys from `defaults` since it's listed second, while keys unique to either dictionary are kept as-is. This pattern is common for applying user overrides on top of default settings, without needing to manually check and overwrite each key one at a time.

In Python 3.9+, there's also a dedicated merge operator that does the same thing:
```python
merged = defaults | user_settings
```
Both approaches produce identical results; `|` is newer and arguably more readable once you know what it means, while `{**a, **b}` works on older Python versions too.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I check if a number falls within a range in Python, without writing two separate comparisons?",
        response="""```python
age = 20
if 18 <= age <= 65:
    print("Working age")
```

Python supports chained comparisons directly -- `18 <= age <= 65` reads naturally as "18 is less than or equal to age, and age is less than or equal to 65," evaluated as a single combined check. This is equivalent to, but cleaner than:
```python
if age >= 18 and age <= 65:
```
Both work identically, but the chained version reads closer to how you'd actually say the range out loud, and avoids writing `age` twice. This chaining works with any comparison operators, not just `<=` -- `a < b < c`, `a == b == c`, and mixed chains are all valid, though mixing very different operators in one chain can get confusing to read and is worth avoiding even when technically legal.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is caching, and why would I use it in a web application?",
        response="""Caching means storing the result of an expensive operation so a future request for the same thing can reuse the stored result instead of redoing the work. If computing something (a database query, an API call, a complex calculation) takes real time, and the same request comes in repeatedly with the same result each time, caching that result can turn a slow repeated operation into a near-instant lookup.

A simple example: a page showing "top 10 most popular courses" might be recalculated from the database every single time someone visits, even though the answer barely changes minute to minute. Caching that result for, say, 5 minutes means the expensive calculation runs once every 5 minutes instead of on every single page load, while still staying reasonably up to date.

The real trade-off is staleness: a cached value can become outdated if the underlying data changes before the cache refreshes. Deciding how long to cache something, and when to explicitly invalidate a cache early (like right after data actually changes), is often the harder design question -- the caching mechanism itself is usually the easy part.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is API pagination, and why do APIs return results in pages instead of all at once?",
        response="""Pagination breaks a large result set into smaller chunks ("pages"), returned one page at a time, rather than sending everything in a single response. If an endpoint has 50,000 records, returning all of them in one request would be slow, use a huge amount of memory and bandwidth, and likely time out before completing anyway.

A typical paginated API response includes the current page's data, plus metadata for getting more:
```json
{
  "results": [...],
  "page": 1,
  "total_pages": 340,
  "next": "/api/students?page=2"
}
```

Client code typically requests one page, processes it, then requests the next using the provided link or page number, repeating until there are no more pages left. This keeps each individual request fast and predictable in size, regardless of how large the total dataset actually is -- a well-designed API stays equally responsive whether the underlying table has 100 rows or 100 million.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function silently return the wrong total when an item is missing its price?

```python
def cart_total(items):
    total = 0
    for item in items:
        total += item["price"]
    return total

cart = [{"name": "Book"}, {"name": "Pen", "price": 2}]
print(cart_total(cart))
```""",
        response="""The first item, `{"name": "Book"}`, has no `"price"` key at all -- so `item["price"]` raises `KeyError: 'price'` the moment the loop reaches it. This isn't a silent wrong answer; it's a crash, which is actually the better outcome here, since a silently wrong total would be far more dangerous in something handling money.

If missing prices should be treated as a specific case (skip the item, or default to 0), handle it explicitly rather than letting the crash happen:
```python
def cart_total(items):
    total = 0
    for item in items:
        total += item.get("price", 0)
    return total
```
`.get("price", 0)` defaults to `0` for any item missing a price, rather than crashing. Whether that's actually the *correct* behavior depends on your application -- silently treating a missing price as free could hide a real data problem. Sometimes the crash is actually more useful than a silent wrong number, since it forces you to notice and fix the missing data rather than quietly computing an incorrect total.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""This code is supposed to retry a failed request up to 3 times, but it only ever tries once. Why?

```python
def fetch_with_retry(url, attempts=3):
    for i in range(attempts):
        response = requests.get(url)
        if response.status_code == 200:
            return response
        return None
    return None
```""",
        response="""The `return None` inside the loop runs on the *first* failed attempt, before the loop ever gets a chance to try again -- it exits the function immediately rather than continuing to the next iteration. So even though the loop is set up to run 3 times, a single failure ends the function on attempt 1.

Fixed version -- only give up after all attempts are exhausted:
```python
def fetch_with_retry(url, attempts=3):
    for i in range(attempts):
        response = requests.get(url)
        if response.status_code == 200:
            return response
    return None  # only reached after all attempts failed
```
Moving the final `return None` outside the loop (matching the loop's indentation level, not nested inside it) means it only executes once the loop has genuinely finished all its iterations without succeeding. This is a good example of how indentation in Python directly determines control flow, not just visual formatting -- the exact same code with a `return` shifted one level of indentation behaves completely differently.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the DRY principle in software development, and can following it too strictly cause problems?",
        response="""DRY stands for "Don't Repeat Yourself" -- the idea that a piece of logic or knowledge should exist in exactly one place in your codebase, rather than copy-pasted in multiple spots. If you find yourself writing nearly identical code in three different functions, DRY suggests extracting that logic into one shared function all three can call instead.

The real benefit: when that logic needs to change, you update it in one place, instead of hunting down every copy and hoping you found them all -- missed copies are a genuine, common source of bugs.

That said, DRY can be followed too aggressively. Two pieces of code that look similar right now, but represent genuinely different concepts that just happen to coincide today, can become a real problem if you prematurely merge them into one shared function -- a later change needed for one use case might now incorrectly affect the other. A useful check before extracting shared code: are these two things the same because they're conceptually the same thing, or just because they currently happen to look alike? Only the first case is a good candidate for genuine DRY refactoring.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="Why do style guides recommend avoiding 'magic numbers' in code?",
        response="""A magic number is an unexplained literal value embedded directly in code, with no indication of what it represents or why that specific value was chosen:
```python
if age > 17:
    print("Eligible")
```
What does `17` mean here? Is it a legal age threshold? An arbitrary business rule? A typo for `18`? Nothing in the code itself answers that.

Giving it a name fixes this:
```python
MINIMUM_AGE = 18
if age >= MINIMUM_AGE:
    print("Eligible")
```
Now the code explains itself, and if the age threshold ever needs to change, there's one obvious place to update it, rather than hunting through the codebase for every place `17` or `18` might appear (some of which might be unrelated numbers that just happen to share the same value). This matters more as codebases grow -- a magic number that's obvious to you today, writing it, is often genuinely mysterious to someone else reading it six months later, including future you.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is snowball sampling, and when is it an appropriate method to use?",
        response="""Snowball sampling recruits initial participants, then asks them to refer other potential participants who fit your study's criteria -- the sample grows outward from an initial small group through referrals, like a snowball picking up more snow as it rolls.

It's particularly useful for reaching populations that are hard to identify or contact through standard sampling methods -- people in a specific informal profession, members of a tight-knit community without a public directory, or people who might be reluctant to be identified through a public recruitment call but are more willing to participate if referred by someone they trust.

The real limitation: because participants come through personal networks, the resulting sample tends to reflect the characteristics of your starting participants and their social circles specifically, rather than representing the broader population evenly. Findings from a snowball sample generally shouldn't be treated as generalizable to the whole population the way a proper random sample's findings could be -- it's a practical tool for reaching hard-to-access groups, with that generalizability trade-off clearly acknowledged in how you frame your findings.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between purposive sampling and random sampling, and why would a researcher choose purposive sampling deliberately?",
        response="""Random sampling gives every member of a population an equal, known chance of being selected -- it's the standard approach when you want findings that generalize confidently to the whole population. Purposive sampling deliberately selects specific participants based on characteristics relevant to your research question, rather than selecting randomly.

A researcher chooses purposive sampling when they specifically need participants with particular relevant experience or characteristics that random sampling might miss entirely, or select too few of to study meaningfully. If you're studying the experience of first-generation university students specifically, randomly sampling the entire student body would likely give you very few first-generation students in your sample -- purposively selecting participants who are first-generation students ensures your sample actually contains the population you need to study.

The trade-off is the same generalizability limitation as snowball sampling: a purposive sample is chosen to answer a specific question well, not to represent the broader population proportionally. This is a legitimate, common, and often necessary choice for research questions focused on a particular group's experience -- it's not a lesser method, just one suited to a different kind of research question than random sampling is.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether requiring version control usage from day one in an introductory programming course affects students\' later comfort with collaborative software projects. Comparing 150 students taught with git from the first week to 150 taught without it until a later course, early-git students reported significantly higher confidence in group project settings, though no significant difference was found in individual assignment grades."',
        response="Researchers compared 150 students who learned git version control from their very first week of an intro programming course to 150 students who didn't learn it until a later course. The students who learned git early felt much more confident working on group projects later on -- though it didn't seem to affect their grades on individual assignments either way.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether providing real-time typing feedback (highlighting syntax errors as they occur) versus feedback only at compile time affects debugging skill development among beginner programmers over a semester. Comparing 110 students using real-time feedback tools to 110 using compile-time-only feedback, the compile-time-only group showed stronger independent debugging skills by semester end, despite slower initial progress."',
        response='This study compared beginner programmers who got instant feedback on syntax errors as they typed to students who only found out about errors when they tried to compile their code. Surprisingly, the students who had to wait and debug errors themselves ended up with stronger independent debugging skills by the end of the semester, even though they were slower to get started -- suggesting that struggling with errors a bit actually helped them learn to debug better in the long run.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether pair programming, compared to solo programming, affects code quality in introductory software engineering coursework. Analyzing 200 submitted projects, pair-programmed submissions had 27% fewer post-submission defects than solo submissions, with no significant difference in total development time between the two approaches."',
        response="Researchers compared code quality between student projects built by pairs of programmers working together versus students working alone. The pair-programmed projects had 27% fewer bugs found after submission -- and notably, working in pairs didn't actually take any longer overall than working solo, despite involving two people on the same work.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction="What is a code review, and what should I actually look for when reviewing someone else's pull request?",
        response="""A code review is a check by someone other than the author before code gets merged -- catching bugs, design issues, or unclear logic while it's still cheap to fix, rather than after it's already part of the shared codebase.

A few concrete things worth checking, beyond just "does it run":
1. **Does it actually solve the stated problem?** Not just "does this code work," but "is this the right fix for what was reported."
2. **Are there obvious edge cases unhandled?** Empty input, very large input, unexpected types -- the kinds of bugs covered throughout this conversation.
3. **Is the code readable to someone who didn't write it?** If you have to ask the author to explain what a section does, that's worth flagging, even if the logic itself is correct.
4. **Does it introduce duplication that already exists elsewhere?** Sometimes worth pointing out even if it's not blocking.

A good review comment explains *why*, not just *what*: "this will break if the list is empty" is more useful than just "fix this." The goal is a better outcome for the code and a better understanding for the author, not just approval or rejection.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="How do I flatten a nested list in Python, like turning [[1,2],[3,4]] into [1,2,3,4]?",
        response="""```python
nested = [[1, 2], [3, 4], [5, 6]]
flat = [item for sublist in nested for item in sublist]
# [1, 2, 3, 4, 5, 6]
```

This is a nested list comprehension -- read it left to right: "for each `sublist` in `nested`, for each `item` in that `sublist`, include `item`." It's equivalent to:
```python
flat = []
for sublist in nested:
    for item in sublist:
        flat.append(item)
```
This only flattens one level deep -- if your list contains lists of lists (three levels or more), this specific pattern won't fully flatten it, and you'd need a recursive approach instead. For the common two-level case, though, this compact version is the standard idiomatic way to do it in Python.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I safely access a value that might be several levels deep in a nested dictionary, without it crashing if a level is missing?",
        response="""```python
data = {"user": {"profile": {"name": "Omol"}}}

name = data.get("user", {}).get("profile", {}).get("name")
```

Chaining `.get()` calls means each step returns an empty dictionary as a fallback if that key is missing, so the *next* `.get()` call has something safe to operate on instead of crashing with `AttributeError: 'NoneType' object has no attribute 'get'`. If any level is genuinely missing, the final result is simply `None`, rather than a crash partway through.

For deeply nested structures, this chaining gets visually noisy -- at that point, a small helper function is often cleaner:
```python
def safe_get(d, *keys):
    for key in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(key)
    return d

name = safe_get(data, "user", "profile", "name")
```
Both approaches solve the same problem; which one's worth using depends on how deep the nesting actually goes and how often this pattern repeats in your code.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I use a `try`/`finally` block, and how is it different from just `try`/`except`?",
        response="""```python
file = open("data.txt")
try:
    data = file.read()
    process(data)
finally:
    file.close()
```

`finally` runs no matter what happens in the `try` block -- whether it completes successfully, raises an exception, or even hits a `return` statement partway through. This makes it the right tool for cleanup code that absolutely must run regardless of outcome, like closing a file or releasing a lock.

The key difference from `except`: `except` only runs if a *specific* error occurs, and it can prevent that error from propagating further. `finally` runs unconditionally, and doesn't stop an exception from continuing to propagate after it finishes -- it just guarantees the cleanup code executes first. In modern Python, a `with` statement (like `with open("data.txt") as file:`) handles this exact file-closing pattern automatically, which is why you'll see `with` used far more often than manual `try`/`finally` for resource cleanup specifically -- but `finally` is still the right tool for other kinds of guaranteed cleanup that don't fit the `with` pattern.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the single responsibility principle, and how do I recognize when a function is violating it?",
        response="""The single responsibility principle says a function (or class) should have one clear job, not several unrelated ones bundled together. A function that does too much becomes harder to test, harder to reuse, and harder to change without accidentally affecting unrelated behavior.

A warning sign: if describing what a function does requires the word "and" more than once, it's often doing too much:
```python
def process_order(order):
    validate_order(order)
    save_to_database(order)
    send_confirmation_email(order)
    update_inventory(order)
```
This function validates, saves, emails, *and* updates inventory -- four distinct responsibilities in one function. Splitting it into four smaller functions, each doing one thing, makes each piece independently testable and reusable -- you could reuse `send_confirmation_email` elsewhere without dragging along the database or inventory logic.

This doesn't mean every function should be one line -- it means each function's job should be describable in one clear sentence without an "and" connecting unrelated tasks.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What's the difference between camelCase and snake_case, and does it actually matter which I use?",
        response="""`camelCase` (`studentName`) and `snake_case` (`student_name`) are both ways of writing multi-word variable names, since spaces aren't allowed in most languages' identifiers. Which one to use is mostly a convention question, not a technical one -- code runs identically either way.

What actually matters is consistency with your language's established convention: Python's community standard is `snake_case` for variables and functions (`student_name`, `calculate_total`), while JavaScript's community standard is `camelCase` (`studentName`, `calculateTotal`). Mixing conventions within the same codebase -- some functions in `snake_case`, others in `camelCase`, in the same Python file -- reads as inconsistent and makes a codebase feel less professional, even though it doesn't cause any actual bugs.

The practical rule: follow whatever convention is standard for the language and codebase you're working in, even if you personally prefer the other style -- consistency with everyone else's code matters more than your own preference here.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this function work fine the first time but break on the second call?

```python
def add_student(name, roster=[]):
    roster.append(name)
    return roster

print(add_student("Omol"))   # ["Omol"]
print(add_student("Andrew")) # ["Omol", "Andrew"] -- but expected just ["Andrew"]
```""",
        response="""This is the mutable default argument trap: `roster=[]` creates the default empty list *once*, when the function is first defined -- not fresh on every call. Every call that doesn't explicitly pass its own `roster` shares that same single list, which is why it keeps growing across calls instead of starting fresh each time.

Fixed version:
```python
def add_student(name, roster=None):
    if roster is None:
        roster = []
    roster.append(name)
    return roster
```
Using `None` as the default, and creating a genuinely new list inside the function body when needed, means each call that doesn't pass its own `roster` gets its own fresh list. This specific bug is common enough that it's worth remembering as a named pattern: never use a mutable object (list, dict, set) directly as a default argument value in Python.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this crash with a RecursionError instead of finishing?

```python
def countdown(n):
    print(n)
    countdown(n - 1)

countdown(5)
```""",
        response="""There's no base case -- no condition that stops the recursion. `countdown` keeps calling itself with a smaller `n` forever: 5, 4, 3, 2, 1, 0, -1, -2... it never reaches a point where it decides to stop, so it keeps recursing until Python's built-in recursion depth limit is hit, raising `RecursionError: maximum recursion depth exceeded`.

Fixed version, with an explicit stopping condition:
```python
def countdown(n):
    if n < 0:
        return
    print(n)
    countdown(n - 1)
```
Every recursive function needs exactly this: a base case that stops the recursion, reached in a finite number of steps from any valid starting input. Forgetting the base case entirely, or writing one that the recursive calls never actually reach, are both common causes of this exact error.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a strong topic sentence that actually previews what a paragraph is about?",
        response="""A strong topic sentence states the paragraph's main claim clearly, so a reader knows what to expect before reading the supporting details. A weak topic sentence either states a fact with no real claim attached, or is so vague it could open almost any paragraph on the topic.

Compare:
- **Weak:** "Mobile banking is used in many countries." (a fact, but no argument -- what's this paragraph actually about?)
- **Strong:** "Despite widespread mobile banking availability, adoption remains low among informal-sector workers due to persistent trust concerns." (states a specific claim the rest of the paragraph will support)

A useful test: read only your topic sentences, in order, skipping everything else. If they form a coherent outline of your overall argument on their own, they're doing their job. If they read as a disconnected list of facts, or you can't tell what most paragraphs are actually arguing just from their opening sentence, that's worth revising -- the topic sentence should carry the weight of "here's this paragraph's job," not just introduce a general subject.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is hedging language in academic writing, and how much of it is actually appropriate to use?",
        response="""Hedging language qualifies a claim's certainty -- words like "suggests," "may," "appears to," "tends to" -- rather than stating something as an absolute fact. Used well, it accurately reflects genuine uncertainty; used poorly, it either overstates confidence (no hedging where real uncertainty exists) or undermines every claim with excessive qualification.

Overstated confidence: "This intervention improves outcomes" -- when your actual evidence is one modest study, this claims more certainty than the evidence supports.

Reasonable hedging: "This intervention appears to improve outcomes, though further research across different populations would strengthen this conclusion" -- this accurately reflects what a single study can and can't establish.

Excessive hedging (the opposite problem): "It might perhaps be somewhat possible that this intervention could potentially have some effect on outcomes in certain cases" -- stacking multiple hedges on the same claim reads as weak and evasive rather than appropriately cautious.

The right amount of hedging matches your actual confidence level, stated once clearly -- not zero hedging on strong claims, and not multiple redundant hedges piled onto the same sentence.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How should I structure my discussion section around my original research questions, rather than just writing generally about what I found?",
        response="""A discussion section organized directly around your original research questions is usually clearer than one that wanders through findings in whatever order feels natural. If you had three research questions, structuring your discussion in three matching sections -- each addressing one question directly -- helps the reader track how your evidence actually answers what you set out to ask.

A structure that works well per question:
1. **Restate the question briefly.**
2. **State what you found, connecting it back to the question directly** -- "In answer to this question, we found..."
3. **Situate it against existing literature** -- does it align, conflict, extend prior work?
4. **Note any relevant limitation specific to this particular finding.**

This structure also makes it much easier for a reader (or a reviewer) to check that you actually answered every question you originally posed -- a common weakness in student research writing is posing three research questions in the introduction, then discussing findings in a way that doesn't clearly map back to answering each one directly, leaving the reader to piece together which finding answers which original question themselves.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether displaying a live word count while students write essays affects final essay length and quality. Comparing 180 students with a visible word counter to 180 without one, the word-counter group produced essays averaging 15% longer, but graders found no significant difference in essay quality scores between the two groups."',
        response="Researchers tested whether showing students a live word count while writing essays changed how much they wrote and how good the essays were. Students who could see the word counter wrote essays that were 15% longer on average -- but when graders scored the essays, there was no real difference in quality between the two groups, suggesting the extra length didn't actually translate into better writing.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether requiring students to write unit tests before writing their actual implementation code (test-driven development) affects final code quality in an introductory software course. Comparing 85 students using test-driven development to 85 writing tests afterward or not at all, the test-first group\'s final submissions had 22% fewer defects, though students reported the test-first approach felt slower initially."',
        response='This study tested whether having beginner programmers write their tests before writing the actual code -- a practice called test-driven development -- led to better final code. Students who wrote tests first ended up with 22% fewer bugs in their final submissions, even though many of them said the approach felt slower to start with.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether university writing centers\' use of structured feedback rubrics, compared to open-ended written comments, affects student revision quality on research papers. Comparing 120 papers receiving rubric-based feedback to 120 receiving open-ended comments, rubric-fed students made more substantive revisions to their argument structure specifically, while open-ended-feedback students made more surface-level wording changes."',
        response='Researchers compared two ways university writing centers give feedback on research papers: a structured rubric versus open-ended written comments. Students who got rubric-based feedback tended to make more meaningful revisions to their actual argument and structure, while students who got open-ended comments tended to focus more on surface-level wording changes instead.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether displaying peer code quality scores publicly within a classroom affects individual code quality in a way that differs by initial skill level. Comparing 60 higher-initial-skill and 60 lower-initial-skill students under a public-scoring system, higher-skill students showed modest quality improvement, while lower-skill students showed no significant change and reported increased anxiety about the visible comparison."',
        response="This study looked at what happened when a classroom made students' code quality scores visible to their peers, and whether the effect differed based on students' starting skill level. Students who already had stronger coding skills improved a bit under the public scoring system -- but students with weaker starting skills didn't improve at all, and instead reported feeling more anxious about being compared publicly to their classmates.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction="""Why does this configuration loading code break in production but work fine locally?

```python
import os
API_KEY = os.environ["API_KEY"]
```""",
        response="""`os.environ["API_KEY"]` requires the environment variable to already exist -- if it's not set, this raises `KeyError: 'API_KEY'` immediately when the module loads. Locally, this probably works because a `.env` file (loaded by something like `python-dotenv`) or your shell already has `API_KEY` set. In production, if that same variable was never configured on the actual server or hosting platform, the app crashes on startup.

Two improvements worth making: use `.get()` with a clear error message instead of letting a raw `KeyError` surface, and fail loudly with an explanation rather than a cryptic built-in error:
```python
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set")
```
This produces a much clearer error message when something's missing, and more importantly, it's worth double-checking that every environment variable your code depends on is actually configured on each environment you deploy to -- "works on my machine" often means exactly this: an environment variable set locally that was never set on the actual server.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )
    yield SFTExample(
        instruction="How do I write a Python function that accepts either a single item or a list of items, and always processes it as a list internally?",
        response="""```python
def notify(recipients):
    if not isinstance(recipients, list):
        recipients = [recipients]
    for r in recipients:
        print(f"Notifying {r}")

notify("Omol")                    # works
notify(["Omol", "Andrew", "Sara"]) # also works
```

`isinstance(recipients, list)` checks whether the caller already passed a list; if not, wrapping the single value in a list (`[recipients]`) normalizes it to the same shape before the rest of the function runs. This means the actual processing logic only ever has to deal with one case (a list), rather than branching its behavior throughout the function based on which form was passed in.

This pattern is genuinely convenient for callers -- they don't need to remember to wrap a single value in a list themselves -- but it's worth using deliberately, not by default: it can make a function's expected input less obvious from its signature alone, so it's most appropriate for utility functions where this flexibility is a clear, documented convenience, not a surprise.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a function with a default parameter value in Python, and how do I override it when needed?",
        response="""```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Omol"))                    # "Hello, Omol!"
print(greet("Omol", "Welcome"))         # "Welcome, Omol!"
print(greet("Omol", greeting="Hi"))     # "Hi, Omol!"
```

`greeting="Hello"` gives that parameter a default value used whenever the caller doesn't provide one. It can still be overridden either positionally (the second call) or by name (the third call) -- both work identically here since there's no ambiguity, though using the keyword form (`greeting="Hi"`) becomes more valuable for readability once a function has several parameters.

One rule worth knowing: default parameters must come *after* any parameters without defaults in the function's definition -- `def greet(greeting="Hello", name):` would raise a `SyntaxError`, since Python needs to know unambiguously which arguments are required before it can allow optional ones.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is semantic versioning, and what do the three numbers in a version like 2.4.1 actually mean?",
        response="""Semantic versioning (semver) is a convention for version numbers in the format MAJOR.MINOR.PATCH, where each part signals something specific about what changed:

- **MAJOR** (the first number) increases for breaking changes -- code written for the old version might not work with the new one without modification.
- **MINOR** (the second number) increases for new features that don't break existing usage -- old code should keep working fine.
- **PATCH** (the third number) increases for bug fixes that don't add features or break anything.

So going from `2.4.1` to `2.5.0` means new features were added, but your existing code should still work unchanged. Going from `2.4.1` to `3.0.0` is a signal to actually read the changelog before upgrading, since something breaking almost certainly changed.

This convention is why `requirements.txt` sometimes uses version ranges like `requests>=2.28,<3.0` instead of pinning one exact version -- it allows automatic updates for new features and bug fixes (safe, since MAJOR didn't change) while blocking a MAJOR version bump that might break your code unexpectedly.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What should a good README file actually include for a project other people might use or contribute to?",
        response="""A README is usually the first thing anyone sees when they find your project, so it should answer the questions a new visitor actually has, roughly in this order:

1. **What does this project do?** One or two sentences, before anything else.
2. **How do I install/run it?** Concrete, copy-pasteable commands, not vague instructions.
3. **How do I use it?** A minimal working example, if applicable.
4. **How do I contribute** (if it's open to contributions), including how to set up a development environment.
5. **What license is it under?**

A common mistake is leading with implementation details or a long history of the project before explaining what it actually does or how to get started -- a new visitor deciding whether this project is relevant to them shouldn't have to read several paragraphs before finding out. Treat the top of your README as the highest-value real estate in the whole project: the most important, immediately useful information belongs there, with deeper detail further down.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this function return the wrong average when the list contains a mix of ints and strings?

```python
def average(numbers):
    return sum(numbers) / len(numbers)

print(average([10, 20, "30"]))
```""",
        response="""`sum()` tries to add all the elements together, but Python can't add an integer and a string directly -- `10 + 20 + "30"` raises `TypeError: unsupported operand type(s) for +: 'int' and 'str'`, since addition between a number and text isn't a defined operation. This isn't a silently wrong average; the function crashes entirely once it hits the mismatched type.

If the input might legitimately contain numeric strings that should be treated as numbers, convert explicitly before summing:
```python
def average(numbers):
    numbers = [float(n) for n in numbers]
    return sum(numbers) / len(numbers)
```
`float(n)` works whether `n` is already a number or a numeric string, normalizing everything to the same type before the math happens. If the data is expected to always be clean numbers and a string appearing represents a real data problem elsewhere, letting it crash loudly (rather than silently converting) might actually be the more appropriate behavior -- which is the right fix depends on whether mixed types are expected and valid, or a sign something upstream is wrong.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does calling this function twice with the same input give different results the second time?

```python
def get_next_id(ids=[]):
    new_id = len(ids) + 1
    ids.append(new_id)
    return new_id

print(get_next_id())  # 1
print(get_next_id())  # 2 -- but expected 1 again, since no ids were passed either time
```""",
        response="""This is the mutable default argument bug again, in a slightly different shape than usual -- `ids=[]` is created once at function definition time, and every call that doesn't pass its own `ids` shares that same persistent list. The first call appends `1` to it; the second call sees a list that already has one item in it (from the first call), so it computes `len(ids) + 1` as `2` instead of `1`.

Fixed the same way as before:
```python
def get_next_id(ids=None):
    if ids is None:
        ids = []
    new_id = len(ids) + 1
    ids.append(new_id)
    return new_id
```
This bug is worth recognizing by its symptom, not just its code shape: if a function's behavior seems to depend on how many times it's been called before, even with what looks like identical fresh input each time, a mutable default argument is one of the first things worth checking.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I write a strong methodology section that a reader could actually replicate, not just skim?",
        response="""Replicability is the real test of a methodology section -- another researcher, with access to your paper alone, should be able to run essentially the same study. That's a higher bar than just describing generally what you did.

Concrete things that often go missing:
1. **Exact sample size and how participants were selected**, not just "a group of students."
2. **Precise wording or a reference to the actual instrument used** -- if you used a survey, either include it in an appendix or cite the validated instrument you drew from.
3. **The exact time period and setting** data was collected in -- context that could plausibly affect results.
4. **The specific analysis method and any software/tools used**, including version numbers where it might matter (a statistical test run in one software package can occasionally produce slightly different output than another).

A useful test while drafting: could someone unfamiliar with your specific study read only this section and set up an attempt to replicate it, without needing to guess or ask you for missing details? If they'd have to ask "wait, how exactly did you select participants?" or "what did the actual survey questions say?", the section needs more specificity.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What does reproducibility mean in research, and why has it become such a significant concern across many fields?",
        response="""Reproducibility means that if another researcher takes your same data and same analysis approach, they arrive at the same results. This is a narrower concept than replicability (which involves collecting new data): reproducibility asks "can someone get the same answer from the same data," while replicability asks "does a new, independent study find the same thing."

Concerns about this have grown because a meaningful number of published findings, when other researchers have attempted to reproduce or replicate them, haven't held up -- sometimes because of outright errors, but more often because of subtle issues like unclear analysis choices, small sample sizes that produced results that don't generalize, or selective reporting of only the analyses that "worked."

Practical steps that support reproducibility in your own work: share your actual data and analysis code where possible (not just a written description of your method), document every analysis decision as you make it rather than reconstructing your reasoning afterward, and pre-register your hypotheses and planned analysis before collecting data, if your field and study design support doing so. These practices make it possible for others to actually verify your work, rather than simply trusting your written description of it.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is triangulation in research, and how is it different from just using multiple data sources for convenience?",
        response="""Triangulation means deliberately using multiple methods, data sources, or perspectives to examine the same research question, specifically to check whether they converge on a consistent answer -- strengthening confidence in a finding if they agree, or revealing something genuinely more complex if they don't.

This is different from just having multiple data sources incidentally. True triangulation is a deliberate design choice: if you're studying student stress, you might combine a survey (quantitative, broad reach), interviews (qualitative, depth), and objective data like library usage logs (behavioral, no self-report bias) -- specifically because each method has different strengths and blind spots, and agreement across all three gives you more confidence than any single method alone.

When the different sources *don't* agree, that's not a failure of the method -- it's often the most interesting finding, worth exploring rather than discarding. If your survey shows low reported stress but interview participants describe significant stress, that discrepancy itself might reveal something real, like a gap between how people describe their experience on a quick survey versus in a more reflective conversation.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether assigning students to fixed project groups for an entire semester, versus rotating group membership every few weeks, affects both project outcomes and individual skill development. Comparing 12 fixed-group and 12 rotating-group course sections, fixed groups produced higher-rated final projects, while rotating groups showed broader individual skill development across different technical roles."',
        response="Researchers compared students who stayed in the same project group all semester to students who rotated between different groups every few weeks. The students who stayed in fixed groups produced better final projects overall -- but students who rotated between groups developed broader skills across different technical roles, since they weren't stuck doing the same type of work with the same teammates the whole time.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether providing sample past exam questions, without answers, affects study time allocation and exam performance compared to providing a general study guide. Comparing 140 students given past exam questions to 140 given a general topic list, the past-questions group reported more targeted study time and scored 11% higher on the actual exam."',
        response='This study compared students given actual sample questions from past exams (without answers) to students given a general list of topics to study. Students with the sample questions reported studying in a more focused way, and scored 11% higher on the real exam -- suggesting that seeing the actual question format helped students prepare more effectively than a general topic list did.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper evaluates whether providing students with a rubric before starting an assignment, rather than only after submission, affects final submission quality. Comparing 160 students given the rubric upfront to 160 receiving it only alongside their graded feedback, upfront-rubric students scored 14% higher on average, with the largest gains observed on assignment criteria that were easy to overlook without explicit guidance."',
        response='Researchers tested whether giving students the grading rubric before they started an assignment, instead of only seeing it after grading, changed their results. Students who saw the rubric upfront scored 14% higher on average -- and the biggest improvements were on parts of the assignment that were easy to miss without knowing exactly what was being graded for.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether requiring students to write a one-paragraph reflection after each programming assignment affects long-term retention of programming concepts, tested three months later. Comparing 100 students who wrote reflections to 100 who did not, the reflection group scored 19% higher on a delayed concept-retention test, despite no difference in scores on the original assignments themselves."',
        response="This study tested whether having students write a short reflection after each programming assignment helped them remember the concepts three months later. Even though both groups scored about the same on the original assignments, the students who wrote reflections scored 19% higher on a test of the same concepts given three months afterward -- suggesting the reflection helped the learning stick, even if it didn't show up in the immediate assignment grade.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study investigates whether providing a searchable archive of previously answered student questions reduces duplicate questions asked in a course\'s help forum. Comparing forum activity six weeks before and after the archive was introduced, duplicate question volume dropped by 52%, while questions genuinely not covered in the archive continued at a stable rate."',
        response="Researchers looked at what happened when a course added a searchable archive of previously answered student questions to its help forum. Duplicate questions -- ones that had already been answered before -- dropped by 52% after the archive was introduced, while genuinely new questions that weren't already covered kept coming in at the same steady rate as before.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We assess whether allowing students to resubmit a corrected version of a failed assignment, for partial credit recovery, affects their performance on subsequent related assignments. Comparing 90 students given a resubmission option to 90 without one, resubmission-eligible students scored 16% higher on the next related assignment, with the effect strongest among students who had never previously failed an assignment in the course."',
        response="This study tested whether letting students resubmit a corrected version of a failed assignment, for partial credit, helped them do better on later related assignments. Students who had the resubmission option scored 16% higher on the next related assignment -- and this benefit was strongest for students who hadn't failed an assignment before, suggesting the chance to fix and understand their mistake helped it actually sink in.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )
    yield SFTExample(
        instruction="How do I convert a list of numbers into a comma-separated string, and back again?",
        response="""```python
numbers = [1, 2, 3, 4]
text = ",".join(str(n) for n in numbers)
print(text)  # "1,2,3,4"

back_to_numbers = [int(n) for n in text.split(",")]
print(back_to_numbers)  # [1, 2, 3, 4]
```

`.join()` requires strings specifically, so `str(n) for n in numbers` converts each number first -- `.join()` can't directly combine a list of integers, since it doesn't know how you'd want a number represented as text. Going back, `.split(",")` breaks the string apart at each comma, and `int(n)` converts each resulting piece back to a number, since everything from `.split()` comes back as strings regardless of what the original data looked like.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I check whether a list contains any items matching a condition, without writing a full loop?",
        response="""```python
grades = [65, 72, 58, 90]
has_failing = any(g < 60 for g in grades)
all_passing = all(g >= 60 for g in grades)

print(has_failing)  # True
print(all_passing)  # False
```

`any()` returns `True` if at least one element satisfies the condition; `all()` returns `True` only if every element does. Both take a generator expression (like `g < 60 for g in grades`) and short-circuit -- `any()` stops checking as soon as it finds one match, `all()` stops as soon as it finds one failure, so neither has to check the entire list unnecessarily in the common case. This is generally cleaner than writing a manual loop with a flag variable:
```python
has_failing = False
for g in grades:
    if g < 60:
        has_failing = True
        break
```
Both do the same thing; `any()` expresses the intent directly rather than building it up manually.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the purpose of a webhook, and how is it different from an API my app calls directly?",
        response="""When your app calls an API, your app initiates the request and waits for a response -- you're asking "has anything happened?" A webhook flips this: instead of you repeatedly asking, the other service calls *your* app automatically, the moment something relevant actually happens.

A concrete example: instead of your app repeatedly polling a payment processor every minute asking "has this payment completed yet?", you register a webhook URL with the payment processor. The moment the payment actually completes, the processor sends a request directly to your webhook URL, notifying you immediately -- no polling, no wasted requests asking about things that haven't happened yet.

This matters for both efficiency and timeliness: polling wastes requests checking on things that usually haven't changed, and introduces delay (you only find out at your next poll, not the moment it happens). Webhooks push information to you the instant it's available, at the cost of your app needing a publicly reachable endpoint for the other service to actually call.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this API client work fine for one request but fail on rapid repeated requests?

```python
import requests

def fetch_all_pages(base_url, total_pages):
    results = []
    for page in range(1, total_pages + 1):
        response = requests.get(f"{base_url}?page={page}")
        results.extend(response.json())
    return results
```

Fetching 200 pages quickly triggers a wave of 429 "Too Many Requests" errors partway through.""",
        response="""This function fires off requests as fast as the network allows, with no pause between them -- which is exactly what a rate limit (discussed earlier) exists to catch. The API is enforcing its own limit on requests per minute, and this loop blows straight through it without any awareness that a limit exists.

Fix by adding a small delay between requests, and handling the case where a limit is still hit anyway:
```python
import requests
import time

def fetch_all_pages(base_url, total_pages):
    results = []
    for page in range(1, total_pages + 1):
        response = requests.get(f"{base_url}?page={page}")
        if response.status_code == 429:
            time.sleep(5)  # back off and retry
            response = requests.get(f"{base_url}?page={page}")
        results.extend(response.json())
        time.sleep(0.2)  # small pause between every request
    return results
```
Real production code often uses a more sophisticated approach (reading the `Retry-After` header some APIs return, or exponential backoff), but the core idea is the same: don't assume an API will accept requests as fast as you can send them, and handle the rate-limit response explicitly rather than letting it crash your data collection partway through.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this dictionary lookup crash intermittently, only for some students?

```python
def get_letter_grade(score, grade_scale):
    for threshold, letter in grade_scale.items():
        if score >= threshold:
            return letter
```

`grade_scale` is `{90: "A", 80: "B", 70: "C", 60: "D"}`. Scores below 60 sometimes cause the function to return `None` instead of "F".""",
        response="""This isn't actually intermittent or a crash -- it's a real logic gap the function has for every single score below 60, it just wasn't obvious until someone happened to test with a failing score. The loop only returns a value if the score meets one of the defined thresholds (90, 80, 70, 60); for any score below 60, none of the `if score >= threshold:` checks are ever true, so the loop finishes without hitting any `return`, and the function implicitly returns `None`.

Fix by adding an explicit fallback after the loop:
```python
def get_letter_grade(score, grade_scale):
    for threshold, letter in sorted(grade_scale.items(), reverse=True):
        if score >= threshold:
            return letter
    return "F"
```
Also worth noting: dictionaries in Python do preserve insertion order, but that's not the same as being *sorted* -- `sorted(grade_scale.items(), reverse=True)` explicitly sorts by threshold, from highest to lowest, which this function actually depends on to check the highest applicable grade first. Without that explicit sort, the loop's behavior would depend on the dictionary's insertion order, which is easy to get wrong by accident.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I choose a good research question -- what separates a strong one from a weak one?",
        response="""A strong research question is specific, answerable with evidence you can realistically gather, and genuinely uncertain -- meaning you don't already know the answer with confidence before starting. A weak question tends to fail one of these three tests.

**Too broad, not specific:** "How does technology affect education?" -- this could be an entire book, not a single study.

**Not answerable with available evidence:** "Is online learning better than in-person learning?" -- "better" needs to be defined in measurable terms (test scores? engagement? completion rates?) before this is actually researchable.

**Not genuinely uncertain:** "Do students who never attend class perform worse than students who attend regularly?" -- this is close to definitionally true and unlikely to produce an interesting or informative finding.

A useful revision process: start broad, then keep asking "specifically what, measured how, in which population?" until you reach something like "Does weekly use of a specific study app improve quiz scores among first-year computer science students, compared to students who don't use it?" -- specific, measurable, and not a foregone conclusion.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a strong conclusion for a research paper, without just repeating my abstract?",
        response="""A conclusion that just restates the abstract wastes an opportunity -- by this point, the reader already knows what you found. A stronger conclusion does something the abstract can't: it reflects on what the findings actually mean, in a broader sense, now that the reader has seen your full argument and evidence.

A structure that works well:
1. **Briefly restate the core finding** -- one sentence, not a re-summary.
2. **Connect it to the bigger picture.** Why does this matter beyond your specific study? What broader question does it speak to?
3. **State the practical implication**, if there is one -- who should do something differently as a result of this finding?
4. **End with a genuine, forward-looking thought** -- not just "more research is needed" (too generic), but something specific this finding opens up.

Avoid introducing entirely new evidence or arguments in the conclusion -- anything substantive enough to change how a reader interprets your findings belongs earlier, in the discussion. The conclusion's job is to land the point you've already made, not to make a new one at the last minute.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is member checking in qualitative research, and how do I actually do it?",
        response="""Member checking means sharing your interpretation of a participant's data back with them, to check whether your understanding actually reflects what they meant -- a way of validating your analysis directly against the people whose experience you're describing, rather than relying solely on your own interpretation.

A practical approach: after coding interview data and identifying themes, share a summary of your interpretation (not necessarily the full analysis) with participants, and ask something like "does this capture your experience accurately? Is there anything here that doesn't feel right, or that you'd want to add?"

This isn't just a courtesy -- it's a real check against a genuine risk in qualitative analysis: a researcher's own framework or assumptions shaping how they interpret what someone said, in a way the original speaker wouldn't actually recognize or agree with. If several participants push back on the same interpretation, that's a real signal to revisit your analysis, not just note the disagreement and move on. Member checking works best when done specifically enough that participants can meaningfully react to it -- vague summaries ("participants generally felt positive") don't give anyone enough to actually confirm or challenge.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether university career centers\' use of mock technical interviews affects actual interview outcomes for computer science students. Comparing 130 students who completed at least two mock interviews to 130 who completed none, mock-interview students received job offers at a rate 28 percentage points higher, with the largest gains among students who had no prior professional interview experience."',
        response="Researchers compared computer science students who practiced with at least two mock technical interviews through their university career center to students who did none. The students who practiced got job offers at a rate 28 percentage points higher -- and this benefit was biggest for students who'd never been through a professional interview before at all.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether embedding short, low-stakes quizzes throughout online course video lectures, rather than only at the end of each module, affects concept retention. Comparing 175 students with embedded quizzes to 175 with end-of-module quizzes only, embedded-quiz students scored 24% higher on a comprehensive final assessment, despite spending roughly the same total time watching lecture content."',
        response='This study compared students who got short quiz questions embedded throughout online video lectures to students who only got a quiz at the end of each module. Students with the embedded quizzes scored 24% higher on the final comprehensive test -- even though both groups spent about the same total time watching the lectures, suggesting the more frequent quizzing helped concepts stick better along the way.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether providing students with access to anonymized examples of previous top-scoring submissions affects their own submission quality on a capstone project. Comparing 95 students given access to past examples to 95 without, the examples group scored 13% higher on average, though instructors noted a modest increase in submissions following overly similar structural patterns to the shared examples."',
        response="Researchers looked at whether giving students access to anonymized examples of previous top-scoring capstone projects helped their own work. Students who saw the examples scored 13% higher on average -- though instructors also noticed a downside: some students' projects ended up following the structure of the example projects a bit too closely, rather than developing their own approach.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether scheduling optional office hours in the evening, rather than only during standard daytime hours, affects attendance among students who work part-time jobs. Comparing attendance data across 20 course sections before and after evening office hours were introduced alongside existing daytime hours, overall office hours attendance increased by 45%, driven almost entirely by students who self-identified as working 15 or more hours per week."',
        response="This study looked at what happened when a course added evening office hours in addition to the usual daytime ones. Overall attendance at office hours went up by 45% -- and almost all of that increase came from students who worked 15 or more hours a week at part-time jobs, suggesting the evening option specifically helped students who couldn't make it during the day because of work.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether requiring students to estimate their expected grade before receiving actual feedback affects their engagement with that feedback afterward. Comparing 110 students who predicted their grade first to 110 who did not, prediction-first students spent 37% more time reviewing detailed feedback comments, with the effect strongest among students whose prediction was significantly higher than their actual grade."',
        response='Researchers tested whether having students guess their own grade before seeing the real one changed how much attention they paid to the feedback afterward. Students who predicted their grade first spent 37% more time actually reading through the detailed feedback -- and this effect was strongest for students whose guess was way higher than the grade they actually got, suggesting the surprise made them want to understand what happened.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students who use a personal coding portfolio website during their studies have different early-career job search outcomes than students who do not. Comparing 200 students with an active portfolio site to 200 without one, portfolio-owning students received their first interview request an average of 3.2 weeks earlier, with no significant difference in the number of applications submitted between the two groups."',
        response="This study compared computer science students who maintained a personal coding portfolio website to those who didn't, looking at their job search outcomes. Students with a portfolio site got their first interview request 3.2 weeks earlier on average -- and interestingly, both groups submitted roughly the same number of job applications, suggesting the portfolio made each application more effective rather than the students simply applying to more jobs.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether short daily coding practice sessions (15 minutes) produce different skill outcomes than fewer, longer weekly sessions (roughly 105 minutes total) among self-taught programmers. Comparing 80 participants in each condition over eight weeks, the daily-short-session group showed stronger consistency in applying concepts to new problems, while the weekly-long-session group reported covering more distinct topics overall."',
        response="Researchers compared self-taught programmers who practiced coding for 15 minutes every day to those who practiced in fewer, longer weekly sessions adding up to about the same total time. After eight weeks, the daily-practice group was better at consistently applying what they'd learned to new problems, while the weekly-session group had covered a wider range of topics overall -- suggesting each approach has a real trade-off rather than one being simply better than the other.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction="What's the difference between PUT, PATCH, and POST in a REST API, and when should each be used?",
        response="""`POST` creates a new resource -- calling it repeatedly typically creates multiple new records, which is why it's not idempotent. `PUT` replaces an entire existing resource with the data you send -- if you omit a field, it's often treated as cleared, since you're sending the complete new state. `PATCH` updates only the specific fields you include, leaving everything else on the resource unchanged.

```
POST /students          -- create a new student
PUT /students/5         -- replace student 5 entirely with the sent data
PATCH /students/5       -- update only the fields included in the request
```

A common mistake is using `PUT` when you only want to change one field -- if your `PUT` request only sends `{"name": "Omol"}` but the resource also has an `email` field, a strict `PUT` implementation might clear the email, since it interprets the request as "this is the complete new resource." `PATCH` avoids that risk by design, since it's explicitly meant for partial updates.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the N+1 query problem, and why does it slow down applications so much?",
        response="""The N+1 problem happens when code fetches a list of N items with one query, then separately queries the database once *per item* to get related data -- resulting in 1 + N total queries instead of a single efficient one.

```python
students = db.query("SELECT * FROM students")  # 1 query
for student in students:
    grades = db.query(f"SELECT * FROM grades WHERE student_id = {student.id}")  # N more queries
```

For 500 students, this fires 501 separate database queries where a single well-written query could return everything at once:
```python
results = db.query("SELECT students.*, grades.* FROM students JOIN grades ON students.id = grades.student_id")
```
Each database round-trip has real overhead beyond just the query execution itself -- network latency, connection handling -- so 501 small queries are almost always dramatically slower than 1 larger one, even though the total amount of data returned is similar. This is a genuinely common performance bug, especially in code that uses an ORM, where the extra queries can be hidden behind convenient-looking syntax that doesn't obviously reveal it's making N separate database calls.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I write a Python class with a custom string representation, so printing an instance shows something readable instead of a memory address?",
        response="""```python
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def __str__(self):
        return f"{self.name} (grade: {self.grade})"

s = Student("Omol", 85)
print(s)  # "Omol (grade: 85)"
```

Without `__str__`, printing an object shows something unhelpful like `<__main__.Student object at 0x7f8b2c0a1d90>` -- a memory address, not useful information. Defining `__str__` tells Python exactly what to show instead whenever the object is converted to a string, whether by `print()`, `str()`, or an f-string.

There's also `__repr__`, a related method meant for a more precise, often code-like representation useful for debugging (ideally one that could recreate the object if evaluated). If you only define one, `__str__` is usually the more immediately useful choice for everyday printing, though defining both is common practice in more polished code.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I round a number to two decimal places in Python, and format it consistently for display?",
        response="""```python
price = 19.9
print(f"{price:.2f}")  # "19.90"

total = 19.876
print(round(total, 2))  # 19.88
```

`:.2f` inside an f-string is a format specifier -- `f` means fixed-point notation, `.2` means two digits after the decimal point. This is specifically for *display* formatting; the underlying number isn't changed, just how it's shown as text. `round(total, 2)` actually rounds the number itself to two decimal places, returning a new number rather than a formatted string.

The difference matters for output consistency: `f"{price:.2f}"` on `19.9` always shows `"19.90"` (with the trailing zero), while `round(19.9, 2)` gives back `19.9` (Python doesn't display trailing zeros on a plain number). For anything meant to look consistent to a user -- like prices -- the format specifier approach is usually what you actually want.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a static method in Python, and how is it different from a regular instance method?",
        response="""```python
class MathHelper:
    @staticmethod
    def add(a, b):
        return a + b

print(MathHelper.add(2, 3))  # 5 -- no instance needed
```

A regular instance method automatically receives `self` (the specific object it's called on) as its first argument, and typically reads or modifies that object's own data. A `@staticmethod` doesn't receive `self` at all -- it behaves like a plain function that just happens to live inside the class, usually because it's logically related to the class even though it doesn't need any specific instance's data to do its job.

Use a static method when the logic genuinely doesn't depend on any particular instance's state -- a validation helper, a conversion utility -- and a regular instance method whenever the logic needs to actually read or change `self`'s own data. If you find yourself writing a method that never uses `self`, that's usually a sign it should be a static method instead.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this event listener only ever show the first item's name, no matter which button is clicked?

```javascript
const items = document.querySelectorAll(".item");
for (var i = 0; i < items.length; i++) {
    items[i].addEventListener("click", function() {
        console.log(items[i].name);
    });
}
```""",
        response="""`var` isn't block-scoped -- by the time any button is actually clicked (after the loop has already finished running), `i` has settled at its final value (`items.length`), and every single click handler shares that same `i`, which is now out of bounds, not the value it "was" during that specific loop iteration.

Fixed by using `let` instead, which creates a fresh, separate `i` for each iteration:
```javascript
const items = document.querySelectorAll(".item");
for (let i = 0; i < items.length; i++) {
    items[i].addEventListener("click", function() {
        console.log(items[i].name);
    });
}
```
This is the same underlying `var`-versus-`let` scoping issue that caused the earlier hoisting bug, showing up in a different, very common real-world context: event listeners created inside a loop. It's specifically why modern JavaScript style strongly prefers `let`/`const` over `var` -- this exact bug pattern was extremely common back when `var` was the only option.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this code proceed as if all three requests succeeded, even though one of them actually failed?

```javascript
async function loadDashboard() {
    const [students, grades, attendance] = await Promise.all([
        fetchStudents(),
        fetchGrades(),
        fetchAttendance()
    ]);
    render(students, grades, attendance);
}
```

`fetchGrades()` actually threw an error, but `render()` still ran with `undefined` data.""",
        response="""This description doesn't quite match how `Promise.all` actually behaves -- if any one of the promises passed to it rejects, `Promise.all` itself rejects immediately, and none of the results (including the successful ones) are returned; `render()` should never run at all in that case. If `render()` did run with `undefined` data, the more likely explanation is that `fetchGrades()` didn't actually *throw*, but instead resolved successfully with `undefined` as its value -- a silent failure inside `fetchGrades()` itself, not a `Promise.all` behavior issue.

Either way, this is worth wrapping in proper error handling regardless of the exact cause:
```javascript
async function loadDashboard() {
    try {
        const [students, grades, attendance] = await Promise.all([
            fetchStudents(),
            fetchGrades(),
            fetchAttendance()
        ]);
        render(students, grades, attendance);
    } catch (error) {
        console.error("Failed to load dashboard:", error);
    }
}
```
Worth knowing as a related fact: `Promise.all` fails fast on the first rejection, while `Promise.allSettled` waits for every promise to finish regardless of success or failure, giving you the status of each individually -- useful when partial success (some data loaded, some didn't) is an acceptable outcome, unlike here where all three pieces are presumably needed together.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is construct validity in research, and how is it different from the validity concept discussed earlier (measuring the right thing)?",
        response="""Construct validity specifically asks: does your operationalized measurement genuinely capture the underlying abstract concept ("construct") you claim it measures? It's a more precise version of the general validity question -- specifically focused on the gap between an abstract idea (like "motivation" or "engagement") and the concrete thing you actually measured to represent it.

A concrete example: if you operationalize "student engagement" as "number of forum posts," construct validity asks whether forum posting genuinely reflects engagement, or whether it might actually reflect something else entirely -- comfort with writing, personality traits like extroversion, or simply having more free time. A student could be deeply engaged with course material while rarely posting, and posting frequently without being especially engaged.

Establishing construct validity often involves checking whether your measure correlates appropriately with other measures it theoretically should relate to (convergent validity), and doesn't correlate with measures it shouldn't (discriminant validity). This is a genuinely difficult, often underexamined part of research design -- it's much easier to operationalize a concept than to rigorously verify that your operationalization actually captures what you intended.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is internal validity versus external validity in a study's design?",
        response="""Internal validity is about whether your study design actually supports the causal claim you're making -- did the intervention really cause the observed effect, or could something else explain it? External validity is about whether your findings generalize beyond your specific study's sample and setting to the broader population or other contexts.

A tightly controlled lab experiment with random assignment to treatment and control groups tends to have strong internal validity (you can be fairly confident the intervention caused the effect, since confounding factors were controlled for) but potentially weaker external validity (does this artificial setting reflect real-world conditions?). A large-scale field study across diverse real-world settings might have the opposite trade-off -- strong external validity, but weaker internal validity if it's harder to rule out alternative explanations for what you observed.

These two often trade off against each other, which is why no single study design is universally "best" -- the right balance depends on your specific research question. If you're trying to establish that an effect exists at all, internal validity matters more. If you're trying to argue a finding applies broadly in real-world practice, external validity becomes the bigger concern.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What does 'saturation' mean in qualitative research, and how do I know when I've reached it?",
        response="""Saturation is the point at which collecting additional data (more interviews, more observations) stops revealing genuinely new themes or insights -- new data starts confirming and reinforcing what you've already found, rather than adding anything substantially new.

In practice, researchers often track this by noting whether each additional interview is still surfacing new codes or themes during analysis. If your last several interviews haven't introduced anything you haven't already seen, that's a practical signal you may have reached saturation for your current research question.

This matters for justifying your sample size in qualitative research, where there's no formulaic sample size calculation the way there often is in quantitative work. Rather than justifying "20 interviews" with a statistical power calculation, a qualitative study justifies its sample size by demonstrating that saturation was reached -- new data stopped adding meaningfully to the analysis. Worth being honest in your methodology section about whether you formally tracked this, or estimated it based on general judgment -- claiming saturation without describing how you actually assessed it reads as less rigorous than it could.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether providing students with automated code style feedback (formatting, naming conventions) alongside functional correctness feedback affects long-term code quality habits. Comparing 130 students receiving both types of feedback to 130 receiving only functional correctness feedback, the combined-feedback group maintained better code style in a follow-up assignment three months later, with no difference in functional correctness between the two groups at any point."',
        response='Researchers compared students who got feedback on both whether their code worked correctly and how well-formatted and readable it was, to students who only got feedback on whether it worked. Three months later, the group that got both types of feedback still had noticeably better code style habits -- though both groups were equally good at getting their code to actually work correctly throughout.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether requiring a brief planning document before starting a coding assignment, outlining the intended approach, affects time-to-completion and final code quality. Comparing 100 students required to submit a plan first to 100 who could start coding immediately, planning-first students completed assignments 18% faster on average, with no measurable difference in final code quality between the two groups."',
        response='This study tested whether making students write a short plan before starting a coding assignment -- rather than jumping straight into writing code -- changed how long it took them to finish and how good the final result was. Students who planned first finished 18% faster on average, even though the final code quality ended up about the same either way, suggesting the planning step saved time without costing quality.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who use an integrated development environment with real-time error highlighting develop different debugging strategies than students using a plain text editor with separate compilation. Comparing 70 students in each condition over a semester, IDE users resolved simple syntax errors faster, while plain-editor users developed stronger systematic debugging habits for complex logic errors specifically."',
        response='Researchers compared students who coded using a modern editor that highlights errors as you type to students using a plain text editor where you only find out about errors by compiling separately. Students with the fancier editor fixed simple typo-style errors faster -- but students using the plain editor actually developed stronger systematic debugging skills for more complex logic problems, since they had to work harder to track down issues on their own.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who explain their code to a non-technical family member as a study technique perform differently on conceptual exam questions than students who only study alone. Comparing 90 students who explained concepts to a non-technical person weekly to 90 who studied independently, the explanation group scored 16% higher on conceptual exam questions specifically, with no difference on purely syntax-based questions."',
        response="This study tested whether explaining programming concepts to a family member who doesn't code -- as a weekly study habit -- helped students understand the material better than studying alone. Students who did this scored 16% higher specifically on exam questions that tested conceptual understanding, though there was no difference on questions that just tested knowing the correct syntax, suggesting the explaining helped build deeper understanding rather than just memorization.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction="What is the difference between a class method and a static method in Python?",
        response="""```python
class Student:
    school = "Starford"

    @classmethod
    def change_school(cls, new_school):
        cls.school = new_school

    @staticmethod
    def is_valid_grade(grade):
        return 0 <= grade <= 100
```

A `@classmethod` receives the class itself (`cls`) as its first argument, not a specific instance -- it's used when a method needs to work with class-level data (like `school` here, shared across all students) rather than one particular object's data. A `@staticmethod` receives neither `self` nor `cls` -- it's a plain function that happens to live inside the class because it's logically related, but needs no access to the class or any instance at all.

A practical way to tell them apart: if the method needs to read or change something shared across the whole class, use `@classmethod`. If it's just a utility function that's thematically related to the class but doesn't touch any class or instance data, use `@staticmethod`.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )
    yield SFTExample(
        instruction="What is memoization, and how is it different from just caching in general?",
        response="""Memoization is a specific form of caching applied to function calls -- storing a function's return value keyed by its input arguments, so calling it again with the same arguments returns the stored result instantly instead of recomputing it.

```python
def memoize(func):
    cache = {}
    def wrapper(n):
        if n not in cache:
            cache[n] = func(n)
        return cache[n]
    return wrapper

@memoize
def slow_square(n):
    print(f"Computing square of {n}")
    return n * n

slow_square(5)  # prints "Computing square of 5", returns 25
slow_square(5)  # returns 25 instantly, no print -- served from cache
```

General caching can apply to anything (a database query result, an API response); memoization specifically means caching a pure function's output based on its inputs. It only works correctly for functions that always return the same output for the same input (no randomness, no dependence on external state) -- memoizing a function that returns different results for identical inputs would silently return stale, incorrect results.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I define an Enum in Python, and why use one instead of just plain strings?",
        response="""```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

def process(status):
    if status == Status.APPROVED:
        print("Proceeding")
```

An `Enum` defines a fixed, named set of valid values. Compare this to using plain strings directly (`if status == "approved":`), which has a real weakness: nothing stops a typo like `"aproved"` from silently passing through as a valid-looking value that never matches anything, with no error raised anywhere.

With an `Enum`, `Status.APROVED` (typo) would raise an `AttributeError` immediately, since it doesn't exist -- catching the mistake at the point it's written rather than as a silent bug discovered much later. Enums also make valid values self-documenting: `Status.__members__` lists every valid option in one place, rather than valid strings being scattered informally across comments or documentation.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a dataclass in Python, and how does it save time compared to writing a regular class?",
        response="""```python
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    grade: int
    email: str = ""

s = Student("Omol", 85)
print(s)  # Student(name='Omol', grade=85, email='')
```

`@dataclass` automatically generates several methods a regular class would need written by hand: `__init__` (accepting each field as a parameter), `__repr__` (a readable printed representation, shown above), and `__eq__` (so two instances with the same field values compare as equal with `==`). Writing the equivalent regular class means manually writing all of that boilerplate yourself:
```python
class Student:
    def __init__(self, name, grade, email=""):
        self.name = name
        self.grade = grade
        self.email = email
    def __repr__(self):
        return f"Student(name={self.name!r}, grade={self.grade!r}, email={self.email!r})"
    # plus __eq__, if you need it
```
`@dataclass` is specifically useful for classes that are mostly just structured data (like this `Student`), rather than classes with a lot of custom behavior -- for those, the boilerplate savings matter less relative to the actual logic you're writing.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I use `collections.defaultdict` to avoid checking whether a key exists before appending to it?",
        response="""```python
from collections import defaultdict

groups = defaultdict(list)
students = [("A", "Omol"), ("B", "Sara"), ("A", "Andrew")]

for grade, name in students:
    groups[grade].append(name)

print(dict(groups))  # {"A": ["Omol", "Andrew"], "B": ["Sara"]}
```

A regular dictionary raises `KeyError` if you try to `.append()` to a key that doesn't exist yet, which normally means checking first:
```python
if grade not in groups:
    groups[grade] = []
groups[grade].append(name)
```
`defaultdict(list)` eliminates that check entirely -- the first time any key is accessed, it's automatically created with an empty list (or whatever the given factory function produces) before your code even runs, so `.append()` always has something valid to work with. `defaultdict(int)` is another common pattern, useful for counting, since accessing a missing key gives you `0` to start incrementing from instead of a `KeyError`.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this code raise an AttributeError when trying to call a method that clearly exists on the class?

```python
class Student:
    def get_average(self):
        return sum(self.grades) / len(self.grades)

s = Student()
s.grades = [85, 92, 78]
print(s.get_average())
```

Error: AttributeError: 'Student' object has no attribute 'grades'""",
        response="""This error is actually misleading relative to what the code shown does -- as written, `s.grades = [85, 92, 78]` is set right before calling `get_average()`, so this specific sequence should work. The real, more common version of this bug happens when `get_average()` is called *before* `grades` has been set on that particular instance at all -- for example, if `Student` has no `__init__` setting a default `grades` value, and something calls `get_average()` on a freshly created student before any grades were ever assigned.

The fix is to give every instance a starting value in `__init__`, so the attribute always exists from the moment the object is created:
```python
class Student:
    def __init__(self):
        self.grades = []

    def get_average(self):
        if not self.grades:
            return 0
        return sum(self.grades) / len(self.grades)
```
Relying on some other code to set an attribute *after* creating an object, before using it, is fragile -- any code path that skips that step (even accidentally) crashes. Setting sensible defaults in `__init__` means every instance is always in a valid, usable state from the moment it exists.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this list comprehension raise a NameError instead of building the filtered list?

```python
students = [{"name": "Omol", "passed": True}, {"name": "Sara", "passed": False}]
passed_names = [s["name"] for s in students if passed]
```""",
        response="""`passed` on its own isn't defined anywhere -- the loop variable is `s`, and the actual boolean value lives at `s["passed"]`, not in a standalone variable called `passed`. Python looks for a variable named `passed` in the surrounding scope, doesn't find one, and raises `NameError: name 'passed' is not defined`.

Fixed version, referencing the actual key on `s`:
```python
passed_names = [s["name"] for s in students if s["passed"]]
```
This is an easy typo to make specifically because `passed` reads like a natural English word describing what you're filtering for -- but Python has no idea what you mean by it unless it's an actual defined variable or, as corrected here, a lookup on the loop variable itself. Whenever a comprehension's filter condition references something that isn't the loop variable (or derived from it), double-check it's actually defined somewhere accessible.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is a mixed-methods research design, and what are the common ways of actually integrating the quantitative and qualitative parts, rather than just running them side by side?",
        response="""A mixed-methods design deliberately combines quantitative and qualitative data within a single study, specifically because the combination answers the research question better than either alone -- not just because more data feels more thorough.

Three common integration structures:
1. **Explanatory sequential** -- quantitative data collected first, then qualitative data (often interviews) used to help explain surprising or unclear quantitative findings. "Why did this subgroup respond so differently?"
2. **Exploratory sequential** -- qualitative data collected first, used to identify themes or develop a survey instrument, then quantitative data tests how widespread those themes are across a larger sample.
3. **Convergent** -- both types of data collected around the same time, independently, then compared to see whether they tell a consistent story or reveal a genuine discrepancy worth investigating.

The real integration work happens in how you *discuss* the combined findings -- a common weakness is presenting quantitative results in one section and qualitative results in a completely separate section, with no real connection drawn between them. True integration means your discussion actively uses each type of data to illuminate the other, not just reports both side by side.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a case study as a research method, and when is it actually the right choice rather than a broader study across many participants?",
        response="""A case study is an in-depth examination of one instance -- a single organization, event, community, or individual -- studied intensively rather than as one data point among many. It's the right choice specifically when the "how" or "why" of a complex, real-world phenomenon matters more than establishing how common something is across a population.

A case study makes sense when: the phenomenon is genuinely rare or unique (studying one specific successful program's implementation in unusual detail), when you need deep contextual understanding that a survey couldn't capture, or as an early exploratory step before a larger study, to identify what factors and questions are actually worth investigating more broadly later.

The trade-off, worth stating honestly in your own writing: a case study's findings are specific to that case, and shouldn't be presented as automatically generalizable to other contexts. A well-written case study makes a clear, bounded claim -- "in this specific organization, under these specific conditions, this is what happened and why" -- rather than implying the finding necessarily applies elsewhere without further investigation.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether allowing students to choose their own final project topic, versus assigning a fixed topic, affects both project quality and reported motivation. Comparing 130 students with topic choice to 130 assigned a fixed topic, choice students reported significantly higher motivation, though final grades showed no significant difference between the two groups."',
        response='Researchers compared students who got to pick their own final project topic to students who were assigned a fixed topic. Students who had a choice reported feeling much more motivated about the project -- though when it came to actual grades, both groups ended up performing about the same.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether providing students access to an AI coding assistant during homework affects their independent problem-solving ability on unassisted exams. Comparing 200 students with AI assistant access to 200 without, assisted students completed homework 34% faster, but scored 9% lower on unassisted exam problems testing the same underlying concepts."',
        response="This study looked at what happened when students had access to an AI coding assistant while doing homework. They finished homework 34% faster with the assistant -- but on exams where they had to solve similar problems without any help, students who'd used the assistant scored 9% lower, suggesting the help sped up homework without necessarily building the same independent problem-solving skill.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper evaluates whether students who participate in open-source contribution before graduation report different levels of confidence in professional coding environments during their first job. Comparing 95 graduates with pre-graduation open-source experience to 95 without, the open-source group reported significantly higher confidence navigating unfamiliar codebases in their first three months of employment."',
        response="Researchers compared new graduates who had contributed to open-source projects before finishing their degree to those who hadn't, looking at how confident they felt in their first job. The graduates with open-source experience felt much more confident navigating unfamiliar code written by other people during their first few months at work.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether requiring students to estimate task completion time before starting an assignment, then comparing their estimate to actual time spent, improves time estimation accuracy over a semester. Comparing 80 students who practiced this estimation exercise weekly to 80 who did not, the practicing group\'s estimation accuracy improved by 47% by semester end, a skill instructors noted as valuable for later professional project planning."',
        response='This study tested whether having students guess how long an assignment would take, then compare that guess to how long it actually took, helped them get better at estimating time over a semester. Students who practiced this every week improved their estimation accuracy by 47% by the end of the semester -- a skill that matters a lot later when estimating timelines for real professional projects.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who participate in a structured code-reading exercise (analyzing existing well-written code before writing their own) produce higher-quality code on subsequent assignments than students who only practice writing code. Comparing 110 students doing code-reading exercises to 110 practicing only writing, the code-reading group\'s subsequent assignments scored 13% higher on code organization specifically, with no difference in functional correctness."',
        response='Researchers tested whether having students spend time reading and analyzing well-written existing code, before writing their own, improved the quality of the code they later wrote. Students who did these reading exercises scored 13% higher specifically on how well-organized their own later code was -- though both groups were equally good at making their code actually work correctly.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who use spaced repetition flashcard tools to review programming syntax and concepts show different long-term retention than students using traditional re-reading of notes. Comparing 90 students in each condition, the spaced-repetition group retained 38% more concept knowledge on a test given two months after the course ended, despite reporting similar total study time."',
        response='This study compared students who used spaced repetition flashcards to review programming concepts against students who just re-read their notes. Two months after the course ended, the flashcard group remembered 38% more of the material -- even though both groups reported spending roughly the same total amount of time studying, suggesting how you study matters as much as how much you study.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who work through programming exercises in a randomized order, rather than the textbook\'s original sequential order, show different problem-solving flexibility on novel problems. Comparing 75 students in each condition, the randomized-order group scored 21% higher on problems requiring them to combine concepts from different chapters, though scored slightly lower on problems matching a single chapter\'s specific technique."',
        response='Researchers compared students who practiced programming exercises in the order a textbook presented them to students who practiced the same exercises in random order instead. Students who practiced in random order did 21% better on problems that required combining ideas from different chapters -- though they did slightly worse on problems that just tested one specific technique in isolation, suggesting mixed-up practice builds more flexible problem-solving at a small cost to narrow technique mastery.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )
    yield SFTExample(
        instruction="How do I use the `@property` decorator in Python, and what problem does it actually solve?",
        response="""```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.14159 * self.radius ** 2

c = Circle(5)
print(c.area)  # 78.54 -- accessed like an attribute, not called like a method
```

`@property` lets a method be accessed with plain attribute syntax (`c.area`), not method-call syntax (`c.area()`), while still running actual code every time it's accessed. This matters because it lets you start with a plain attribute and later convert it into computed logic without breaking any code that already uses it -- if `area` had originally been a normal stored attribute and you later needed to compute it dynamically, converting it to a `@property` keeps `c.area` working identically for everyone using the class, with no change needed on their end.

Properties can also have a matching setter (`@area.setter`) if you want assignment (`c.area = 10`) to trigger custom logic too, like validation -- rejecting a negative radius, for instance -- rather than blindly accepting whatever value is assigned.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What are ARIA labels in HTML, and when do I actually need them?",
        response="""ARIA (Accessible Rich Internet Applications) attributes provide extra information to assistive technologies, like screen readers, when the visual markup alone doesn't convey what an element means or does.

```html
<button aria-label="Close dialog">×</button>
```

Here, the visible button just shows "×" -- meaningless to a screen reader on its own. `aria-label="Close dialog"` tells assistive technology what the button actually does, since the visual symbol alone doesn't communicate that.

The general rule: prefer real semantic HTML first (a `<button>` rather than a `<div>` styled to look like one, since real buttons already communicate their role automatically). Reach for ARIA attributes specifically to fill in gaps semantic HTML alone can't cover -- icon-only buttons, custom interactive widgets without a natural HTML equivalent, or dynamic content changes a screen reader wouldn't otherwise notice. Overusing ARIA on elements that are already semantically clear can actually make things more confusing, not less, so it's a targeted tool, not something to sprinkle everywhere by default.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I write a CSS media query to change the layout on small screens, like phones?",
        response="""```css
.container {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
}

@media (max-width: 600px) {
    .container {
        grid-template-columns: 1fr;
    }
}
```

`@media (max-width: 600px)` wraps a block of CSS that only applies when the browser's viewport is 600 pixels wide or narrower -- typically phone-sized screens. Here, the default is a 3-column grid, but on narrow screens, it switches to a single column, which usually reads far better on a small screen than three cramped columns would.

This "mobile-first" alternative pattern is also common: write the simple, single-column styles as the default (no media query needed), then use `min-width` media queries to add complexity for larger screens:
```css
.container {
    grid-template-columns: 1fr; /* mobile default */
}
@media (min-width: 600px) {
    .container {
        grid-template-columns: 1fr 1fr 1fr; /* larger screens */
    }
}
```
Both approaches work; mobile-first is often considered better practice since it means phones (increasingly the majority of traffic) get simple, minimal CSS by default, rather than overriding a more complex desktop layout.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is database normalization, and why would I deliberately split data across multiple tables instead of keeping it all in one?",
        response="""Normalization organizes data to minimize redundancy -- avoiding storing the same piece of information in multiple places, which risks it going out of sync if one copy gets updated but another doesn't.

Un-normalized example, storing everything in one table:
```
enrollments: student_name, student_email, course_name, course_instructor
```
If a student's email changes, you'd need to update it in every single row where that student appears -- miss one, and now your data disagrees with itself about that student's actual email.

Normalized version splits this into separate tables:
```
students: id, name, email
courses: id, name, instructor
enrollments: student_id, course_id
```
Now each student's email exists in exactly one place. Updating it means changing one row, and every enrollment automatically reflects the correct, current email through the relationship (`student_id`), rather than needing to be manually kept in sync across many duplicated rows. This trade-off isn't free -- normalized data usually requires `JOIN`s to reassemble a full picture, which has its own performance cost -- but for most applications, the consistency benefit is well worth that cost.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this dictionary comprehension raise a TypeError instead of building the lookup table?

```python
students = [{"id": 1, "name": "Omol"}, {"id": 2, "name": "Sara"}]
lookup = {student for student in students}
```""",
        response="""`{student for student in students}` uses curly braces, but with only one expression per item (`student`) rather than a `key: value` pair -- that syntax actually builds a *set*, not a dictionary. Since `student` here is a dictionary, and dictionaries aren't hashable (a required property for set membership), this raises `TypeError: unhashable type: 'dict'`.

The fix is providing an actual key and value, using dictionary comprehension syntax:
```python
lookup = {student["id"]: student["name"] for student in students}
# {1: "Omol", 2: "Sara"}
```
The visual similarity between set comprehensions (`{x for x in ...}`) and dict comprehensions (`{k: v for x in ...}`) is exactly what makes this an easy typo -- missing the `:` silently changes what kind of collection you're building, rather than raising an error at the point of the actual mistake. If you want the full objects preserved, not flattened, keying by ID with the full dict as the value also works: `{student["id"]: student for student in students}`.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this recursive function work for small inputs but crash for larger ones with a RecursionError?

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

print(factorial(3000))
```""",
        response="""The function itself is logically correct -- it has a proper base case and eventually terminates. The problem is that Python has a default recursion depth limit (typically 1000), and computing `factorial(3000)` requires 3000 nested function calls, which exceeds that limit before the recursion can complete.

For genuinely large inputs like this, an iterative version avoids the recursion depth entirely:
```python
def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```
This computes the exact same result without ever needing more than one function call's worth of stack space, since there's no recursion at all -- just a loop.

More generally: recursion is often more elegant to read and write, but it comes with real limits on how deep it can go, and each recursive call uses actual memory on the call stack. For problems where the "depth" scales with a potentially large input size, an iterative approach (or an increased recursion limit, if genuinely necessary and safe) is usually the more robust choice.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I handle missing data in a dataset -- what are my actual options, and how do I decide between them?",
        response="""Missing data needs an explicit decision, not silent ignoring -- how you handle it can genuinely change your results, sometimes significantly.

A few common approaches, with real trade-offs:
1. **Listwise deletion** -- drop any row with missing data in a relevant field. Simple, but if missingness isn't random (say, lower-income participants are more likely to skip an income question), this can bias your remaining sample.
2. **Mean/median imputation** -- fill missing values with the average of what's observed. Simple, but can understate the real variability in your data.
3. **Multiple imputation** -- a more sophisticated statistical technique that estimates missing values based on relationships with other variables, done multiple times to reflect genuine uncertainty about what the missing value actually was.

Before choosing, it's worth asking *why* data is missing -- data missing completely at random is far less concerning than data missing for a reason connected to the outcome you're studying (a survey where people who feel most stressed are also the ones most likely to skip a stress-related question, for instance). Whatever method you choose, report both how much data was missing and how you handled it -- silently imputing missing values without disclosing it undermines a reader's ability to evaluate your findings honestly.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I decide whether to remove an outlier from my dataset, rather than just deleting anything that looks unusual?",
        response="""An outlier is unusual, but "unusual" alone isn't a reason to delete it -- some outliers are genuine, meaningful data points (a real, unusually high performer), while others are data entry errors or measurement problems (someone accidentally typing an extra zero). Treating these two cases the same way is a common mistake.

A more careful process:
1. **Investigate before removing.** Is there a plausible explanation this is an error (impossible value, like a negative age) versus a genuine extreme case?
2. **If it's a genuine data point, consider whether it belongs in your analysis at all**, based on your actual research question -- not just whether it "looks weird" on a chart.
3. **If you do remove or adjust outliers, report it explicitly** -- how many, on what basis, and ideally show your key results both with and without them, so a reader can judge whether your conclusion depends heavily on that decision.

The real danger with outlier removal is that it's tempting to remove data points specifically because they don't fit your expected pattern, which can artificially inflate how strong your finding looks. A rule applied consistently and stated upfront (like "removing values more than 3 standard deviations from the mean") is far more defensible than removing data points case-by-case based on whether they happen to support your hypothesis.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who maintain a public coding blog documenting their learning process show different job application response rates than students without one. Comparing 120 students with an active blog to 120 without, blog-maintaining students received recruiter outreach messages at a rate 3.1 times higher, though self-reported technical skill was similar between the two groups."',
        response="Researchers compared computer science students who kept a public blog documenting what they were learning to students who didn't. Students with an active blog got contacted by recruiters more than three times as often -- even though both groups reported having similar technical skill levels, suggesting the blog itself made a real difference in visibility, not just underlying ability.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students taught using real-world messy datasets, rather than clean textbook examples, in an introductory data analysis course show different confidence when encountering unfamiliar real datasets after the course. Comparing 100 students taught with messy real-world data to 100 taught with clean textbook data, the messy-data group reported significantly higher confidence handling new real datasets, despite slower initial progress through course material."',
        response='This study compared students taught data analysis using messy, real-world datasets to students taught with clean, tidy textbook examples. Students who practiced with messy data felt much more confident handling new, unfamiliar real datasets afterward -- even though they moved through the course material more slowly at first because messy data is harder to work with.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether requiring students to write their own test cases before receiving instructor-provided tests affects their understanding of edge cases in programming assignments. Comparing 85 students who wrote tests first to 85 who received instructor tests immediately, the write-first group identified 29% more edge cases in a subsequent unrelated assignment, suggesting a transferable skill rather than assignment-specific learning."',
        response="Researchers tested whether having students write their own test cases before seeing the instructor's tests helped them get better at spotting edge cases in general. Students who wrote their own tests first identified 29% more edge cases on a completely different, later assignment -- suggesting they'd actually learned a transferable skill, not just memorized answers for one specific assignment.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who receive feedback within 24 hours of submission show different revision engagement than students receiving feedback after one week, holding feedback content constant. Comparing 140 students receiving fast feedback to 140 receiving delayed feedback on identical assignments, fast-feedback students were 52% more likely to actually read and act on detailed comments, based on tracked engagement with the feedback document."',
        response='This study looked at whether how quickly students got feedback on their work -- within a day versus after a week -- affected whether they actually engaged with it, even when the feedback content itself was identical. Students who got fast feedback were 52% more likely to actually read and act on the detailed comments, suggesting that speed of feedback matters almost as much as its quality for whether students actually use it.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether pairing students with a slightly more experienced peer mentor, rather than a same-level study partner, affects problem-solving persistence when stuck on a difficult programming problem. Comparing 90 students paired with a more experienced mentor to 90 paired with a same-level partner, mentor-paired students persisted 41% longer on unsolved problems before giving up or seeking additional help."',
        response='Researchers compared students who worked with a slightly more experienced peer mentor to students paired with someone at the same skill level, looking at how they handled getting stuck on a hard problem. Students paired with the more experienced mentor kept trying 41% longer before giving up or asking for more help, suggesting having someone slightly ahead of you nearby helps you push through difficulty rather than give up early.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether providing students with a checklist of common beginner mistakes, to review before submitting an assignment, reduces the frequency of those specific mistakes compared to a group given a general reminder to review their work. Comparing 130 students given the specific checklist to 130 given a general review reminder, checklist students made 44% fewer of the listed common mistakes, with no difference in mistakes not covered by the checklist."',
        response="This study tested whether giving students a specific checklist of common beginner mistakes to review before submitting an assignment actually reduced those mistakes, compared to just telling students generally to review their work. Students with the specific checklist made 44% fewer of exactly those listed mistakes -- though it made no difference at all for other mistakes that weren't on the checklist, suggesting the checklist worked by directly targeting known problem areas rather than improving overall carefulness.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who alternate between two programming languages throughout a course show different conceptual transfer ability than students who learn a single language exclusively. Comparing 70 students learning two languages in parallel to 70 learning one language deeply, the two-language group scored higher on questions requiring them to identify which underlying programming concepts were language-independent versus language-specific."',
        response="Researchers compared students who learned two programming languages side by side throughout a course to students who focused deeply on just one language. The students learning two languages at once were better at recognizing which programming concepts were truly universal ideas versus which were just specific quirks of one particular language -- a kind of understanding that's harder to develop when you've only ever seen concepts expressed one way.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )
    yield SFTExample(
        instruction="How do I use `itertools.groupby` to group a list of items by a shared attribute?",
        response="""```python
from itertools import groupby

students = [
    {"name": "Omol", "grade": "A"},
    {"name": "Sara", "grade": "B"},
    {"name": "Andrew", "grade": "A"},
]
students.sort(key=lambda s: s["grade"])  # groupby requires sorted input

for grade, group in groupby(students, key=lambda s: s["grade"]):
    names = [s["name"] for s in group]
    print(f"{grade}: {names}")
```

`groupby` only groups *consecutive* matching items -- it doesn't scan the whole list looking for all matches the way a dictionary-building approach would, which is exactly why the list must be sorted by the grouping key first. If you skip the sort, items with the same grade but separated by a different grade in between get split into separate groups instead of one combined group.

For many everyday cases, building a dictionary manually (as shown in an earlier example) is simpler and doesn't require pre-sorting:
```python
from collections import defaultdict
groups = defaultdict(list)
for s in students:
    groups[s["grade"]].append(s["name"])
```
`groupby` is more specialized -- useful specifically when working with data that's already naturally sorted or streamed, where building a full dictionary in memory first isn't necessary or desirable.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the purpose of `.env.example` files that show up in some repositories alongside a gitignored `.env`?",
        response="""`.env.example` is a template showing which environment variables a project needs, with placeholder or dummy values -- committed to the repository, unlike the real `.env` file, which stays gitignored since it holds actual secrets.

```
# .env.example
SANADI_API_KEY=your-api-key-here
SANADI_JWT_SECRET=your-jwt-secret-here
SANADI_ALLOWED_ORIGINS=http://localhost:3000
```

Anyone cloning the project sees immediately which variables they need to set, without any real secrets being exposed in the repository's history. The typical workflow: copy `.env.example` to `.env`, then fill in real values. This solves a genuine, common problem -- without this file, a new contributor has no way to know a project even *needs* certain environment variables until the app crashes on startup complaining about a missing one, which is a much worse way to discover the requirement than reading it directly in a template file.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What are npm scripts, and how does running `npm run dev` actually know what to do?",
        response="""npm scripts are named shortcuts for commands, defined in a project's `package.json`:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "jest"
  }
}
```

`npm run dev` looks up `"dev"` in this `scripts` section and runs whatever command is defined there -- in this case, `next dev`. This matters because the actual underlying command can be long or project-specific, while the shortcut name stays simple and consistent across projects: `npm run dev` starts development mode whether the actual tool underneath is Next.js, Vite, or something else entirely, as long as the project defines a `dev` script.

A few script names are common enough to have shorthand -- `npm start` and `npm test` work without the word `run`, for historical reasons, while every other custom script name needs the full `npm run <name>` form. This is why you've been running `npm run dev` rather than `npm dev` throughout this project.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this async function return a Promise object instead of the actual data, even though it looks like it should return the data directly?

```javascript
async function getStudentName() {
    return "Omol";
}

const name = getStudentName();
console.log(name); // Promise {<fulfilled>: 'Omol'} -- not "Omol" directly
```""",
        response="""Any function marked `async` *always* returns a Promise, regardless of what you `return` inside it -- this isn't optional or conditional, it's how `async` functions work by definition. `return "Omol"` inside an `async` function doesn't hand back the string directly to the caller; it resolves the automatically-created Promise with that value.

To actually get the plain value out, you need `await`:
```javascript
async function printName() {
    const name = await getStudentName();
    console.log(name); // "Omol"
}
```
`await` can only be used inside another `async` function (or at the top level in modern JavaScript modules) -- it's what unwraps the Promise and gives you the actual resolved value. This is a genuinely common point of confusion when first learning `async`/`await`: marking a function `async` changes its return type fundamentally, even for functions that don't appear to do anything asynchronous internally.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this SQL query return duplicate student rows instead of one row per student?

```sql
SELECT students.name, enrollments.course
FROM students
JOIN enrollments ON students.id = enrollments.student_id;
```

A student enrolled in 3 courses appears 3 times in the results.""",
        response="""This is actually correct, expected behavior for a `JOIN`, not a bug -- but it's a common misunderstanding of what a join actually produces. A `JOIN` returns one row for every *matching pair* between the two tables, not one row per student. A student enrolled in 3 courses genuinely has 3 matching rows in `enrollments`, so the join correctly produces 3 result rows for that student, one per course.

If you actually want one row per student, with their courses combined, you need to aggregate:
```sql
SELECT students.name, GROUP_CONCAT(enrollments.course) AS courses
FROM students
JOIN enrollments ON students.id = enrollments.student_id
GROUP BY students.id;
```
`GROUP_CONCAT` (the exact function name varies by database -- `STRING_AGG` in some) combines all matching course values into a single comma-separated string per student, paired with `GROUP BY` to collapse the multiple rows into one per student. Which version you actually want -- one row per enrollment, or one row per student with courses combined -- depends entirely on what you're using the result for.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a conflict of interest disclosure in research, and when am I actually required to include one?",
        response="""A conflict of interest disclosure states any relationship or circumstance that could reasonably be seen as influencing your research's objectivity -- funding sources, financial relationships with an organization your research evaluates, or personal relationships with study participants that could bias your interpretation.

The standard isn't "did this actually bias my results" (which is often genuinely hard to know about yourself) -- it's "could a reasonable reader wonder whether this influenced the findings." If your study evaluates a company's product and that company funded your research, disclosing this lets readers weigh your findings with that context in mind, rather than assuming complete independence they'd naturally expect otherwise.

A simple disclosure statement, even when there's genuinely nothing to disclose, is standard practice: "The authors declare no conflicts of interest" or "This research was funded by [organization], which had no role in study design, data analysis, or the decision to publish." When in doubt about whether something counts as worth disclosing, the safer choice is almost always to disclose it -- an unnecessary disclosure costs little, while an undisclosed real conflict, if discovered later, seriously damages trust in the entire body of work.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is grey literature in research, and should I actually cite it in an academic paper?",
        response="""Grey literature refers to research and reports produced outside traditional peer-reviewed academic publishing -- government reports, NGO reports, conference proceedings, theses, white papers, and similar sources that haven't gone through formal peer review.

It's not automatically lower quality than peer-reviewed work, and it's not automatically off-limits to cite -- but it does carry different, generally weaker quality-control guarantees, since it hasn't been through the same independent review process. Whether it's appropriate to cite depends heavily on context: a government statistics report or an NGO's field data might be the *only* available source for certain practical, real-world information that academic journals haven't covered yet, particularly for emerging or applied topics.

A reasonable practice: use grey literature when it's genuinely the best or only available source for a specific factual claim, cite it clearly as what it is (not represented as peer-reviewed when it isn't), and where possible, note in your own writing that a specific claim rests on non-peer-reviewed evidence, especially if it's central to your argument rather than peripheral supporting context. Checking your specific field's or supervisor's conventions on grey literature is worth doing before relying heavily on it, since acceptance varies meaningfully by discipline.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who present their capstone projects to a panel of external industry professionals, rather than only to course instructors, report different perceived project value. Comparing 100 students presenting to industry panels to 100 presenting only to instructors, industry-panel students rated their project experience as significantly more valuable for career preparation, though final grades were assigned identically by course instructors regardless of audience."',
        response='Researchers compared students who presented their final capstone projects to a panel of real industry professionals to students who only presented to their course instructors. Students who presented to industry professionals felt their project experience was much more valuable for their career -- even though their actual grades were determined the same way by instructors either way.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students who track their own coding practice time using a visible personal dashboard show different consistency in daily practice than students without such tracking. Comparing 90 students using a practice-tracking dashboard to 90 without one, dashboard users practiced on 34% more days over an eight-week period, with the effect strongest in the first two weeks before gradually diminishing."',
        response='This study tested whether giving students a personal dashboard to track their own daily coding practice actually helped them practice more consistently. Students using the dashboard practiced on 34% more days over eight weeks compared to students without one -- though the effect was strongest in the first two weeks and gradually faded afterward, suggesting the novelty of tracking may have driven some of the early motivation boost.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper evaluates whether requiring students to submit a brief post-mortem reflection after a failed or buggy project affects their approach to risk-taking in subsequent projects. Comparing 75 students required to write post-mortems to 75 who were not, post-mortem students attempted more technically ambitious approaches in later projects, with no significant difference in overall project completion rates."',
        response="Researchers tested whether having students write a short reflection after a project that failed or had major bugs changed how they approached later projects. Students who wrote these reflections took on more ambitious technical approaches in their next projects -- and importantly, this didn't come at the cost of actually finishing their projects, since completion rates stayed about the same either way.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who learn to read compiler error messages through a dedicated short tutorial show different independent debugging speed than students who learn through trial and error alone. Comparing 110 students given the tutorial to 110 without it, tutorial students resolved compiler errors 39% faster on average during a subsequent timed exercise, with the largest improvement on errors involving type mismatches specifically."',
        response='This study tested whether a short, dedicated tutorial on how to actually read and understand compiler error messages helped students debug faster, compared to students who just learned through trial and error on their own. Students who got the tutorial resolved compiler errors 39% faster on a later timed exercise -- with the biggest improvement specifically on errors related to mismatched data types.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study investigates whether students working on projects with clearly defined, incremental milestones show different completion rates than students given only a final deadline for the same overall project. Comparing 130 students with incremental milestones to 130 with only a final deadline, milestone students had an 88% completion rate compared to 61% for final-deadline-only students, with the gap widest among students who had historically struggled with time management."',
        response='Researchers compared students given a project broken into smaller milestones with their own deadlines to students given only one final deadline for the whole project. Students with incremental milestones completed their projects at a rate of 88%, compared to just 61% for students who only had a final deadline -- and this gap was even bigger among students who had a history of struggling with time management.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who receive feedback framed around specific next actions (\'add error handling for empty input\') rather than general evaluative comments (\'needs more robustness\') show different revision quality. Comparing 100 students receiving action-framed feedback to 100 receiving general evaluative feedback, action-framed students made revisions that directly addressed the noted issue 76% of the time, compared to 41% for general feedback."',
        response="This study compared two ways of giving feedback on code: specific actionable suggestions versus general evaluative comments. Students who got specific, action-based feedback like 'add error handling for empty input' actually addressed that exact issue in their revision 76% of the time -- compared to only 41% for students who got vaguer feedback like 'needs more robustness,' suggesting specificity matters a lot for whether feedback actually gets acted on.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who work on a shared, persistent group codebase across an entire semester develop different collaboration skills than students who work on separate short-term group projects. Comparing 60 students in a semester-long shared codebase model to 60 in traditional short-term group projects, the shared-codebase group reported significantly higher comfort working with unfamiliar existing code by semester end, a skill closely resembling real workplace conditions."',
        response="Researchers compared students who worked together on one shared codebase that persisted across an entire semester to students who did separate, shorter group projects throughout the term. The students working on the long-term shared codebase felt much more comfortable working with code that other people had written by the end of the semester -- a skill that closely mirrors what it's actually like working on a real software team.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether requiring students to estimate their own confidence level alongside each exam answer affects their study behavior on a subsequent exam. Comparing 95 students who rated their confidence on each answer to 95 who did not, confidence-rating students spent 26% more subsequent study time specifically on topics where they had rated their confidence as low but answered incorrectly, compared to a control group\'s more evenly distributed study time."',
        response="This study tested whether having students rate how confident they felt about each exam answer, in addition to just answering it, changed how they studied afterward. Students who rated their confidence spent 26% more of their later study time specifically on topics where they'd felt confident but actually gotten wrong -- meaning the confidence ratings helped them target exactly the gaps in their understanding, rather than studying everything equally.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )
    yield SFTExample(
        instruction="How do I write a generator expression instead of a list comprehension, and why would I choose one over the other?",
        response="""```python
squares_list = [x**2 for x in range(1000000)]      # builds the whole list in memory now
squares_gen = (x**2 for x in range(1000000))        # produces values one at a time, on demand
```

The only syntax difference is `[]` versus `()`, but the memory behavior is very different. The list comprehension computes and stores all million values immediately. The generator expression computes each value only when you actually ask for it (via a loop, or `next()`), and never holds the full sequence in memory at once.

```python
total = sum(x**2 for x in range(1000000))  # generator -- efficient, no full list built
```
Use a generator expression when you're consuming the values once, in sequence (like feeding them into `sum()` or a `for` loop), and don't need to access them by index or iterate multiple times. Use a list comprehension when you genuinely need the full list -- to index into it, iterate over it more than once, or pass it somewhere that specifically expects a list rather than any iterable.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I write a function with type hints in Python, and do they actually change how the code runs?",
        response="""```python
def calculate_average(grades: list[float]) -> float:
    return sum(grades) / len(grades)
```

`grades: list[float]` and `-> float` are type hints -- they document what types the function expects and returns. Importantly, Python doesn't actually enforce these at runtime by default; calling `calculate_average("not a list")` won't be blocked by the type hint itself, it'll just fail later when the function tries to use it as a list.

So why bother? Type hints let your editor and tools like `mypy` catch type mismatches *before* running the code, by statically analyzing your code against the declared types. They also make function signatures self-documenting -- `grades: list[float]` tells anyone reading the code exactly what's expected, without needing to read the function body or trust a comment that might be outdated. For a solo project, hints are optional convenience; for any codebase with more than one contributor, they meaningfully reduce the "what does this function actually expect" guesswork.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What are CSS custom properties (CSS variables), and how do they help with maintaining a consistent design?",
        response="""```css
:root {
    --primary-color: #111111;
    --spacing-unit: 8px;
}

.button {
    background-color: var(--primary-color);
    padding: var(--spacing-unit);
}

.card {
    border-color: var(--primary-color);
    margin: calc(var(--spacing-unit) * 2);
}
```

`--primary-color` and `--spacing-unit`, defined once on `:root`, can be reused anywhere via `var(--primary-color)`. If the brand color needs to change later, updating it in that one `:root` declaration updates every single place it's used throughout the stylesheet, instead of hunting down and replacing the same hex code scattered across dozens of rules.

This is similar in spirit to avoiding magic numbers in regular code -- a hardcoded `#111111` repeated in fifty places is fragile and error-prone to update; a named variable referenced fifty times is a one-line change. CSS custom properties can also be changed dynamically with JavaScript, or overridden differently within a specific section of a page, which a plain hardcoded value can't do.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function silently ignore the second argument no matter what's passed?

```python
def create_user(name, role="student", role="admin"):
    return {"name": name, "role": role}
```""",
        response="""This is actually a `SyntaxError` in real Python -- `role` is listed as a parameter name twice, and Python doesn't allow duplicate parameter names in a function definition at all. It would fail immediately when the module loads, before the function is ever called, with `SyntaxError: duplicate argument 'role' in function definition`.

This specific mistake usually happens from copy-pasting or editing a function signature carelessly -- perhaps intending to change the default value of `role` but accidentally leaving both the old and new parameter declarations in place:
```python
def create_user(name, role="admin"):  # correct -- one role parameter, new default
    return {"name": name, "role": role}
```
Whenever editing a function signature, it's worth reading the full parameter list back afterward to confirm each parameter name appears exactly once -- Python will catch an exact duplicate like this with a clear error, but it's still worth catching before running the code at all.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this JavaScript comparison behave unexpectedly, treating two seemingly equal arrays as different?

```javascript
const a = [1, 2, 3];
const b = [1, 2, 3];
console.log(a === b); // false
```""",
        response="""Same underlying reason as the earlier Python `is` versus `==` example: `===` in JavaScript checks reference equality for objects and arrays -- whether two variables point to the *exact same* object in memory -- not whether their contents look the same. `a` and `b` are two separate array objects that happen to hold identical values, so `a === b` is `false`.

To compare contents, you need a different approach -- JavaScript has no single built-in operator for deep array equality:
```javascript
console.log(JSON.stringify(a) === JSON.stringify(b)); // true -- compares as strings
```
This works for simple cases but has real limits -- it depends on key/element order matching exactly, and doesn't handle more complex nested structures elegantly. For robust deep equality checks, a library function (like `_.isEqual` from Lodash) is generally more reliable than a homemade comparison, especially once objects and arrays get more deeply nested.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is action research, and how is it different from traditional academic research methods?",
        response="""Action research is conducted by practitioners studying and improving their own practice in real time, in a cyclical process: act, observe the results, reflect, adjust, and act again. It blurs the traditional line between "researcher" and "the people being studied" -- a teacher studying and iteratively improving their own classroom's outcomes is a classic example.

This differs from traditional academic research in a few real ways: the goal is often direct, immediate practical improvement in a specific context, not necessarily generalizable knowledge for a broader field. The researcher is typically an active participant, not a neutral outside observer -- which is a deliberate feature of the method, not a limitation to apologize for, though it does require being explicit about that involvement rather than pretending to a false objectivity.

Action research is well-suited when your goal is genuinely to improve a specific, real situation you're personally part of -- and less suited when your goal is to establish a claim you want to generalize confidently to other contexts you're not directly involved in.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a quasi-experimental design, and why would a researcher use one instead of a true randomized experiment?",
        response="""A true experiment randomly assigns participants to treatment and control groups. A quasi-experimental design compares groups that already exist or were assigned by some non-random process -- comparing two existing school classes, or comparing outcomes before and after a policy change, without the ability to randomly assign who experiences the intervention.

Researchers use quasi-experimental designs when true random assignment isn't ethically or practically possible. You generally can't randomly assign which students get a scholarship, which region gets a new health policy, or which company adopts a new practice -- these situations happen in the real world for reasons outside a researcher's control, and studying them at all means working with the groups as they naturally occur.

The real cost is weaker internal validity -- since groups weren't randomly assigned, there's more room for other pre-existing differences between the groups to explain an observed effect, rather than the intervention itself. Careful quasi-experimental design tries to minimize this (matching similar groups, controlling statistically for known differences), but it can never fully replace the confidence a true random assignment provides.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether displaying a class-wide anonymized distribution of quiz scores (without individual comparison) affects student study effort compared to no distribution shown at all. Comparing 100 students shown the anonymized distribution to 100 not shown it, distribution-shown students reported 22% more subsequent study time, with the effect concentrated among students who scored below the median."',
        response='Researchers tested whether showing students an anonymous chart of how the whole class scored on a quiz -- without identifying individuals -- changed how much they studied afterward. Students who saw the distribution reported studying 22% more afterward, and this effect was mostly driven by students who had scored below the class median, suggesting seeing where they stood motivated extra effort.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who annotate their own code with comments explaining their reasoning, before submitting, show different scores on questions testing their own understanding of that code weeks later. Comparing 85 students required to annotate their reasoning to 85 who were not, annotation students scored 31% higher when asked to explain their own submitted code four weeks after submission."',
        response="This study tested whether having students write comments explaining their own reasoning while coding helped them remember and understand their own code better weeks later. Students who annotated their reasoning scored 31% higher when asked, four weeks afterward, to explain what their own code did and why -- suggesting the act of writing out their reasoning helped it stick in a way just writing the code alone didn't.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether requiring students to predict their exam score before receiving results, then reflecting on any gap between prediction and actual performance, improves calibration accuracy on subsequent exams. Comparing 120 students doing this prediction-reflection exercise to 120 who did not, the exercise group\'s score predictions became 43% more accurate by the course\'s third exam, compared to no significant improvement in the control group."',
        response="Researchers tested whether having students predict their own exam score beforehand, then reflect on how far off they were once they got the real result, helped them get better at accurately judging their own performance over time. Students who did this exercise became 43% more accurate at predicting their scores by the third exam of the course, while students who didn't do the exercise showed no real improvement at all.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students taught to use a systematic debugging checklist (check inputs, check assumptions, check edge cases, in order) resolve bugs faster than students using an unstructured trial-and-error approach. Comparing 95 students trained on the checklist method to 95 using their own approach, checklist-trained students resolved a standardized set of test bugs 27% faster on average, with the largest speed advantage on bugs involving incorrect assumptions about input data."',
        response='This study compared students taught a specific, structured checklist for debugging -- checking inputs, then assumptions, then edge cases in order -- to students who just used whatever approach felt natural to them. The students trained on the checklist resolved a standard set of test bugs 27% faster on average, with the biggest advantage on bugs caused by incorrect assumptions about the input data.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether students who work through programming problems using pseudocode planning before writing actual code show different final code correctness than students who code directly without a planning step. Comparing 105 students required to write pseudocode first to 105 coding directly, pseudocode-first students had 24% fewer logic errors in their final code, with no significant difference in total time spent."',
        response="Researchers tested whether having students plan out their approach in pseudocode before writing actual code led to fewer errors, compared to students who just started coding directly. Students who planned in pseudocode first ended up with 24% fewer logic errors in their final code -- and importantly, this planning step didn't actually take any extra total time overall.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students given access to previous semesters\' anonymized common mistake patterns, specific to each assignment, make fewer of those same documented mistakes. Comparing 130 students given assignment-specific common mistake summaries to 130 without them, students with the summaries made 38% fewer of the specifically documented mistakes, though overall assignment scores showed a smaller, non-significant improvement."',
        response="This study tested whether showing students a summary of common mistakes previous students made on the exact same assignment helped them avoid those same mistakes. Students who saw the mistake summaries made 38% fewer of those specific documented errors -- though their overall assignment scores only improved slightly, suggesting avoiding known pitfalls didn't fully translate into a big overall grade boost.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who complete a brief metacognitive check-in (rating their own understanding) at the midpoint of a lecture show different end-of-lecture comprehension than students without the check-in. Comparing 140 students with a midpoint check-in to 140 without one, check-in students scored 17% higher on an end-of-lecture comprehension quiz, with instructors also reporting more mid-lecture clarifying questions from the check-in group."',
        response='Researchers tested whether pausing partway through a lecture to have students rate how well they were understanding the material improved their overall comprehension by the end. Students who did this mid-lecture check-in scored 17% higher on a quiz given right after the lecture -- and instructors also noticed these students asked more clarifying questions during the lecture itself, suggesting the check-in helped students notice confusion early enough to actually address it.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who participate in cross-institutional virtual study groups, connecting with students from partner universities, report different exposure to alternative problem-solving approaches than students in single-institution study groups. Comparing 60 students in cross-institutional groups to 60 in single-institution groups, cross-institutional students reported encountering significantly more varied solution approaches to the same problems, correlating with higher self-reported adaptability in later technical interviews."',
        response='This study compared students who joined virtual study groups with students from other partner universities to students who only studied with classmates from their own school. Students in the cross-institutional groups reported seeing a much wider variety of approaches to solving the same problems -- and this was linked to them feeling more adaptable later on during technical job interviews.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction="How do I write a Python function that flattens a deeply nested list of arbitrary depth, not just one level?",
        response="""```python
def flatten(nested):
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

print(flatten([1, [2, 3, [4, 5, [6]]], 7]))  # [1, 2, 3, 4, 5, 6, 7]
```

This uses recursion to handle any depth of nesting, unlike the earlier single-level flatten. For each item, it checks whether that item is itself a list -- if so, it recursively flattens *that* sublist first, then adds its results. If the item isn't a list, it's added directly. `result.extend(...)` merges the recursive call's results into the outer list, rather than `.append()`, which would nest them as a single sub-list instead of merging them flat.

The base case here is implicit: a list with no nested lists inside it simply appends every item directly, with no further recursive calls needed, naturally ending the recursion once there's nothing left to flatten.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="How do I use Python's `Counter` to find the most common items in a list?",
        response="""```python
from collections import Counter

words = ["python", "sql", "python", "javascript", "python", "sql"]
counts = Counter(words)

print(counts.most_common(2))  # [("python", 3), ("sql", 2)]
```

`Counter(words)` builds a dictionary-like object counting occurrences of each item automatically, in one step -- equivalent to the manual frequency-dictionary pattern shown earlier, but built directly into Python's standard library. `.most_common(n)` returns the `n` most frequent items as a list of `(item, count)` tuples, sorted from most to least common, saving you from writing your own sorting logic on top of the counts.

Call `.most_common()` with no argument to get every item, sorted by frequency, rather than a limited top-N -- useful when you want the complete ranked list rather than just the top few.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the difference between a shallow copy and a deep copy in Python?",
        response="""```python
import copy

original = {"name": "Omol", "grades": [85, 90]}
shallow = original.copy()
deep = copy.deepcopy(original)

shallow["grades"].append(100)
print(original["grades"])  # [85, 90, 100] -- changed! shallow copy shared the nested list
```

A shallow copy creates a new outer container, but the objects *inside* it (like the `grades` list) are still the same shared objects as the original -- modifying a nested mutable object through the copy also affects the original, since there's really only one `grades` list being referenced by both.

A deep copy recursively copies every nested object too, so the copy is genuinely independent all the way down:
```python
deep["grades"].append(200)
print(original["grades"])  # still [85, 90, 100] -- unaffected, deep copy was fully independent
```
For simple data with no nested mutable objects (like a dict of plain numbers and strings), a shallow copy and deep copy behave identically. The distinction only matters once mutable objects (lists, dicts) are nested inside other mutable objects -- exactly the situation that causes this kind of subtle, hard-to-spot bug.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does modifying a copy of this list also change the original, even though `.copy()` was used?

```python
original = [[1, 2], [3, 4]]
copy_of_list = original.copy()
copy_of_list[0].append(99)
print(original)  # [[1, 2, 99], [3, 4]] -- unexpectedly changed
```""",
        response="""This is exactly the shallow-copy trap: `.copy()` creates a new outer list, but the inner lists (`[1, 2]` and `[3, 4]`) are the *same* objects referenced by both `original` and `copy_of_list` -- the copy only duplicated the outer container, not what's inside it. Calling `.append(99)` on `copy_of_list[0]` modifies that shared inner list directly, which is why the change shows up in `original` too.

Fix by using a deep copy instead, when your data contains nested mutable structures:
```python
import copy
original = [[1, 2], [3, 4]]
copy_of_list = copy.deepcopy(original)
copy_of_list[0].append(99)
print(original)  # [[1, 2], [3, 4]] -- unaffected now
```
This is a genuinely common source of confusing bugs specifically because `.copy()` *sounds* like it should create full independence -- the fact that it only copies one level deep is easy to overlook until nested mutable data is involved.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this dictionary iteration crash with a RuntimeError instead of removing the expired entries?

```python
sessions = {"a": 100, "b": 5, "c": 200}
for key in sessions:
    if sessions[key] < 50:
        del sessions[key]
```""",
        response="""Same root problem as the earlier list-mutation-during-iteration bug, applied to a dictionary: Python doesn't allow changing a dictionary's size while you're actively iterating over it. `del sessions[key]` removes an entry mid-loop, and Python detects this and raises `RuntimeError: dictionary changed size during iteration` to protect you from undefined, inconsistent behavior.

Fix by building a list of keys to remove first, then deleting them after the iteration finishes:
```python
sessions = {"a": 100, "b": 5, "c": 200}
keys_to_remove = [key for key in sessions if sessions[key] < 50]
for key in keys_to_remove:
    del sessions[key]
```
Or more concisely, build an entirely new dictionary instead of mutating the original in place:
```python
sessions = {key: value for key, value in sessions.items() if value >= 50}
```
As a general rule: never modify the size of a list, dict, or set while directly iterating over that same structure -- collect what needs to change first, then apply the changes afterward, or build a new structure rather than mutating the one you're looping over.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a preprint, and what should I know before citing one in my own research?",
        response="""A preprint is a research paper shared publicly before undergoing formal peer review -- researchers post their work to make it immediately available, rather than waiting the months (sometimes years) peer review can take. Preprint servers exist across many fields now, making early findings accessible faster than traditional publishing timelines allow.

The key thing to know before citing one: a preprint hasn't been independently vetted the way a peer-reviewed publication has. It might be entirely solid, or it might contain errors or claims that wouldn't survive peer review -- there's no way to know without evaluating it yourself, since the usual external quality check hasn't happened yet.

If you do cite a preprint, it's worth explicitly noting in your text that it's a preprint, not a peer-reviewed publication -- this is standard practice, not an unusual caveat, and lets your own readers weigh that source appropriately. It's also worth checking whether the preprint has since been formally published (many are, sometimes with revisions) -- citing the peer-reviewed version, once available, is generally preferable to citing the earlier preprint if both exist.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a systematic review, and how is it different from a regular literature review section in a paper?",
        response="""A regular literature review section, as part of a larger paper, selectively discusses relevant prior work to set up the paper's own contribution -- the selection process is often not explicitly documented and doesn't aim to be exhaustive. A systematic review is a distinct type of research output in itself, with a rigorous, explicitly documented methodology for finding and including *every* relevant study meeting defined criteria, not just a representative or convenient sample.

A systematic review typically documents: the exact databases searched, the exact search terms used, explicit inclusion and exclusion criteria (why some found studies were excluded), and often a flow diagram showing how many studies were found, screened, and ultimately included. This documentation exists specifically so another researcher could, in principle, replicate the same search and arrive at the same set of included studies.

This rigor matters because it directly addresses publication bias (discussed earlier) and selective citation -- a systematic review is a much stronger basis for claiming "the evidence on this topic shows X" than an informally selected literature review, precisely because its inclusion process is transparent and reproducible, not left to the author's individual judgment about what to include.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who participate in a structured \'explain it to a beginner\' exercise, writing an explanation of a concept for someone with no prior programming knowledge, show different depth of understanding than students who write technical notes for themselves. Comparing 90 students doing the beginner-explanation exercise to 90 writing standard technical notes, beginner-explanation students scored 21% higher on questions requiring them to identify conceptual misunderstandings in sample code."',
        response="Researchers compared students who practiced explaining programming concepts as if teaching a complete beginner to students who just wrote regular technical notes for themselves. The students who practiced simplifying explanations for beginners scored 21% higher on questions that required spotting conceptual misunderstandings in someone else's code, suggesting that having to explain things simply builds a deeper kind of understanding.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether providing students with a visual diagram of program execution flow, alongside the actual code, improves comprehension of control flow concepts compared to code alone. Comparing 110 students given execution flow diagrams to 110 given code only, diagram-assisted students scored 26% higher on questions predicting program output for unfamiliar code, with the largest gap on code involving nested conditional logic."',
        response='This study tested whether showing students a visual diagram of how a program actually executes, alongside the code itself, helped them understand control flow better than just showing the code alone. Students who saw the diagrams scored 26% higher on questions asking them to predict what unfamiliar code would output -- with the biggest advantage specifically on code involving nested if-statements, which tend to be genuinely harder to trace mentally.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who receive immediate automated feedback on code style violations, integrated directly into their editor, develop different long-term coding habits than students who only see style feedback during manual code review weeks later. Comparing 100 students with real-time style feedback to 100 with delayed manual feedback, real-time-feedback students showed 45% fewer style violations in a final project completed a full semester after the feedback tool was removed."',
        response='Researchers compared students who got instant automated feedback on their code style right in their editor to students who only found out about style issues from a manual review weeks later. The students with instant feedback had 45% fewer style violations in a final project completed a whole semester later -- even after the automated feedback tool was taken away, suggesting the immediate feedback helped build a lasting habit rather than just a temporary fix.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students taught using a spiral curriculum (revisiting core concepts with increasing complexity across the course) show different retention of foundational concepts than students taught with a linear curriculum covering each topic once in depth. Comparing 80 students in a spiral-curriculum course to 80 in a linear-curriculum course, spiral-curriculum students scored 19% higher on a foundational concepts test given at course completion, despite covering fewer total distinct topics."',
        response='This study compared students taught with a spiral curriculum -- where core concepts get revisited multiple times with increasing complexity -- to students taught with a linear curriculum that covers each topic once in depth. The spiral-curriculum students scored 19% higher on a test of foundational concepts at the end of the course, even though their course actually covered fewer total distinct topics, suggesting the repeated revisiting helped the fundamentals stick better.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether students who work through programming challenges with an increasing difficulty curve, rather than randomly ordered difficulty, report different persistence and completion rates. Comparing 120 students with progressively increasing difficulty to 120 with randomly ordered difficulty, progressive-difficulty students completed 31% more challenges overall and reported significantly lower frustration ratings throughout."',
        response='Researchers compared students who worked through coding challenges arranged from easiest to hardest to students who got the same challenges in random difficulty order. Students with the progressively increasing difficulty completed 31% more challenges overall and reported feeling much less frustrated throughout, suggesting that a sense of building momentum matters for both how much students finish and how they feel about the process.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether requiring students to identify which line of their own failing code they suspect is the problem, before receiving instructor help, affects how much they learn from that help session. Comparing 75 students required to make a prediction first to 75 who received help without predicting, prediction-first students were 52% more likely to correctly diagnose a similar bug independently on a later assignment."',
        response='This study tested whether having students guess which line of their broken code was probably causing the problem, before asking an instructor for help, changed how much they actually learned from that help. Students who made a prediction first were 52% more likely to correctly diagnose a similar bug completely on their own on a later assignment, suggesting the act of guessing first made the help session teach a transferable skill rather than just fixing the immediate problem.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who use version control commit messages as a structured reflection tool (writing what changed and why for every commit) show different project organization skills than students who use minimal or no commit messages. Comparing 90 students required to write detailed commit messages to 90 with no such requirement, detailed-commit students\' final projects were rated significantly higher on overall code organization by independent graders unaware of the study condition."',
        response="Researchers compared students required to write detailed git commit messages explaining what changed and why, throughout a project, to students who wrote minimal or no commit messages. Independent graders, who didn't know which students were in which group, rated the detailed-commit-message students' final projects as significantly better organized -- suggesting that the discipline of explaining your changes as you go actually improves how you structure the project overall.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who participate in structured \'code golf\' exercises (solving problems with minimal code) alongside standard assignments show different code conciseness habits in subsequent standard assignments, and whether this affects readability. Comparing 70 students doing code golf exercises to 70 without them, code-golf students wrote 24% shorter solutions on subsequent standard assignments, but independent readability ratings of their code were significantly lower than the control group\'s."',
        response="This study tested whether practicing 'code golf' -- solving problems with the fewest possible lines of code -- as a side exercise changed how students wrote code on their regular assignments afterward. Students who practiced code golf did write 24% shorter code on their later regular assignments -- but when independent reviewers rated how readable that code was, the code-golf group scored notably lower, suggesting the drive for brevity came at a real cost to clarity.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )
    yield SFTExample(
        instruction="How do I write a Python function that safely converts a string to a number, returning a default value instead of crashing if it's not a valid number?",
        response="""```python
def safe_to_int(text, default=0):
    try:
        return int(text)
    except (ValueError, TypeError):
        return default

print(safe_to_int("42"))     # 42
print(safe_to_int("abc"))    # 0 -- invalid, falls back to default
print(safe_to_int(None))     # 0 -- also handled, TypeError caught too
```

Catching both `ValueError` (raised for genuinely non-numeric text like `"abc"`) and `TypeError` (raised if `text` is `None` or some other non-string type entirely) covers the two realistic ways this conversion can fail. The `default` parameter lets callers choose what "invalid input" should mean for their specific use case -- `0` here, but a different default (like `None`, to distinguish "invalid" from "genuinely zero") might be more appropriate depending on context.

This pattern -- wrap risky conversion in a small reusable helper -- is generally cleaner than scattering individual `try`/`except` blocks around every place you convert user input, especially once the same conversion logic is needed in several places throughout a codebase.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I check if two floating-point numbers are 'close enough' to be considered equal in Python, using a built-in tool rather than writing my own tolerance check?",
        response="""```python
import math

a = 0.1 + 0.2
b = 0.3

print(math.isclose(a, b))  # True
```

`math.isclose()` handles the floating-point precision problem discussed earlier (`0.1 + 0.2` not exactly equaling `0.3`) using a sensible default relative tolerance, so you don't need to write and tune your own `abs(a - b) < some_threshold` check manually. It accepts optional `rel_tol` and `abs_tol` parameters if you need to adjust how strict the comparison is for your specific case:
```python
math.isclose(a, b, rel_tol=1e-9)
```
Using the built-in function over a hand-rolled tolerance check is generally preferable -- it's a well-tested, standard tool other developers reading your code will immediately recognize, rather than a custom comparison whose exact behavior they'd need to read and verify themselves.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the difference between `==` and `.equals()`-style comparison across different languages, and why does Python only need `==`?",
        response="""In some languages (like Java), `==` on objects checks reference identity (are these the same object in memory?), while a separate `.equals()` method checks logical value equality (do these represent the same value?) -- two genuinely different comparisons, requiring two different tools.

Python handles this differently: `==` itself checks value equality by default for built-in types (numbers, strings, lists), and Python's `is` operator is the one that checks identity, as covered earlier. This means Python doesn't need a separate `.equals()` method the way Java does -- `==` already does the value-comparison job.

For your own custom classes, `==`'s behavior is actually determined by whether you've defined a `__eq__` method -- without one, `==` falls back to identity comparison (equivalent to `is`) by default:
```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
```
Without this `__eq__` method, two `Point` objects with identical `x`/`y` values would compare as unequal with `==`, since Python would just be checking whether they're the same object in memory -- defining `__eq__` explicitly tells Python what "equal" should actually mean for your class.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this function return an incorrect count when checking for duplicate emails, even though the emails look identical?

```python
emails = ["Omol@Example.com", "omol@example.com", "sara@example.com"]
unique_count = len(set(emails))
print(unique_count)  # 3 -- but the first two are really the same email
```""",
        response="""`set()` compares strings exactly, character by character, including case -- `"Omol@Example.com"` and `"omol@example.com"` differ in capitalization, so Python treats them as two genuinely different strings, even though email addresses are conventionally treated as case-insensitive by mail systems in practice.

Fix by normalizing case before comparing:
```python
emails = ["Omol@Example.com", "omol@example.com", "sara@example.com"]
unique_count = len(set(email.lower() for email in emails))
print(unique_count)  # 2 -- correctly recognizes the duplicate
```
This is a genuinely important pattern any time you're comparing user-provided text that has a conventional case-insensitive meaning -- emails, usernames on many platforms, file extensions. The comparison itself (`==` or `set()` deduplication) is working exactly as designed; the bug is really about not normalizing the data *before* comparing it, given what the data actually represents.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this password validation function accept a password that's clearly too short?

```python
def is_valid_password(password):
    if len(password) > 8:
        has_upper = any(c.isupper() for c in password)
    return has_upper
```

Calling `is_valid_password("short")` returns unexpected behavior rather than clearly rejecting it.""",
        response="""`has_upper` is only ever assigned *inside* the `if len(password) > 8:` block -- if the password is 8 characters or shorter, that line never runs, and `has_upper` was never defined at all. Calling `is_valid_password("short")` (5 characters, so the `if` is false) would actually raise `UnboundLocalError: local variable 'has_upper' referenced before assignment`, not silently accept the short password -- a crash, not a silent bypass, though the crash itself reveals a real logic gap in what the function was meant to check.

The actual bug is that password length was never properly gated as its own condition:
```python
def is_valid_password(password):
    if len(password) <= 8:
        return False
    return any(c.isupper() for c in password)
```
This checks length as an explicit early return, then separately checks for an uppercase letter, rather than tangling the two conditions together in a way that leaves `has_upper` undefined on one path. Whenever a variable is only assigned inside a conditional block but used outside that block, check whether every possible path through the function actually assigns it first.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a data management plan in research, and why do many funders now require one before approving a grant?",
        response="""A data management plan describes how a research project will handle its data throughout the project's life -- how it will be collected, stored securely, backed up, documented, and eventually shared or archived once the study is complete.

Funders increasingly require this upfront, before any funding is granted, for a few concrete reasons: it forces researchers to think through data security and participant privacy protections before collection starts, rather than as an afterthought; it increases the odds that data will actually be usable and shareable after the project ends, rather than existing only in a format or location only the original researcher understands; and it supports the broader push toward reproducibility discussed earlier, since data that's properly documented and preserved can actually be reused or checked by others later.

A basic data management plan typically covers: what data will be collected and in what format, where and how it will be stored during the project, who has access, how participant privacy is protected (especially important for anything involving personal identifying information), and what happens to the data after the project ends -- destroyed, archived, or shared openly, and under what conditions.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What are the FAIR data principles in research, and what do each of the four letters actually mean in practice?",
        response="""FAIR stands for Findable, Accessible, Interoperable, and Reusable -- a set of guiding principles for how research data should be managed so it retains genuine value beyond the original study that produced it.

**Findable** means the data has enough metadata and a persistent identifier that someone could actually locate it later, rather than it existing only as an unlabeled file on someone's personal computer. **Accessible** means there's a clear, documented way to actually obtain the data, even if access requires following a specific request process for privacy reasons -- accessible doesn't necessarily mean unrestricted, just that the path to access is clear and documented. **Interoperable** means the data uses standard, well-documented formats that other tools and researchers can actually work with, rather than a proprietary or undocumented format only the original software can open. **Reusable** means the data is documented well enough (what each column means, how it was collected, any known limitations) that someone else could genuinely understand and correctly use it, not just technically open the file.

These principles matter practically because a huge amount of research data becomes effectively unusable within a few years of a project ending -- not because it was deleted, but because it was never documented or stored in a way that anyone besides the original researcher could actually make sense of.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who review and annotate peer code as part of coursework, before writing their own similar assignments, show different awareness of common design pitfalls. Comparing 100 students who reviewed peer code first to 100 who did not, peer-review students avoided 33% more of a documented set of common design pitfalls in their own subsequent work."',
        response="Researchers tested whether having students review and comment on their classmates' code before writing a similar assignment themselves helped them avoid common design mistakes. Students who reviewed peer code first avoided 33% more of a known set of common pitfalls in their own later work, suggesting that seeing mistakes in someone else's code first helped students recognize and avoid the same patterns in their own.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who set specific, measurable weekly learning goals (rather than general intentions to \'study more\') show different course completion rates in self-paced online programming courses. Comparing 150 students setting specific weekly goals to 150 with only general intentions, specific-goal students had a course completion rate 37 percentage points higher."',
        response="This study compared students in a self-paced online programming course who set specific, measurable weekly goals to students who only had a general intention to study more without specifics. Students with specific weekly goals completed the course at a rate 37 percentage points higher -- a big difference that suggests vague intentions to study more aren't nearly as effective as concrete, specific weekly targets.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether providing students with a glossary of technical terms embedded directly in assignment instructions, versus requiring students to look terms up independently, affects task initiation time and reported anxiety. Comparing 95 students given an embedded glossary to 95 without one, embedded-glossary students began working on assignments 41% faster and reported lower task-related anxiety on a standardized scale."',
        response='Researchers tested whether embedding a glossary of technical terms directly in assignment instructions -- instead of making students look terms up themselves -- changed how quickly students got started and how anxious they felt. Students with the embedded glossary started working 41% faster and reported feeling less anxious about the task, suggesting that removing the friction of looking up unfamiliar terms had a real, measurable effect on both behavior and how students felt.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who use a \'rubber duck\' style AI chat tool -- one that only asks clarifying questions rather than providing direct answers -- show different independent problem-solving development than students using a tool that provides direct solutions. Comparing 90 students using the question-only tool to 90 using a direct-answer tool over a semester, question-only-tool students scored 22% higher on unassisted final exam problem-solving questions."',
        response='This study compared students using an AI tool that only asked clarifying questions, forcing them to work through problems themselves, to students using a tool that gave direct answers. Over a semester, the students using the question-only tool scored 22% higher on problem-solving questions on their final exam, where they had no AI help at all -- suggesting that a tool designed to guide rather than answer directly builds stronger independent skills.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether students who receive a brief explanation of why an assignment\'s requirements matter, connected to real-world use cases, show different assignment engagement than students receiving only the technical requirements. Comparing 130 students given real-world context to 130 given requirements only, context-provided students spent 28% more time voluntarily exploring extensions beyond the minimum requirements."',
        response="Researchers tested whether explaining why an assignment's requirements actually mattered in real-world terms, rather than just listing the technical requirements, changed how engaged students were. Students who got the real-world context spent 28% more time voluntarily going beyond the minimum requirements to explore extra features, suggesting that understanding the 'why' behind an assignment genuinely increases motivation to go further with it.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students taught to write commit messages following a specific conventional format (type, scope, description) show different ability to navigate an unfamiliar project\'s git history compared to students taught with no specific format guidance. Comparing 75 students trained on conventional commit format to 75 without formal training, format-trained students located a specific historical bug-introducing commit 58% faster when navigating an unfamiliar codebase\'s history."',
        response="This study tested whether teaching students to write git commit messages in a specific standardized format -- type, scope, and description -- helped them later navigate an unfamiliar project's history more effectively. Students trained on this format found a specific bug-introducing commit in someone else's project history 58% faster than students with no formal training, suggesting that consistent commit message formatting makes project history genuinely more useful to search through later.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who practice technical communication by writing documentation for their own code, intended for a future maintainer, show different code structure choices than students who write code without a documentation requirement. Comparing 85 students required to write maintainer-facing documentation to 85 without this requirement, documentation-required students\' code was rated significantly higher on modularity by independent reviewers blind to the study condition."',
        response="Researchers compared students required to write documentation for their code, aimed at a future person who'd need to maintain it, to students with no documentation requirement at all. Independent reviewers who didn't know which group was which rated the documented-code group's actual code structure as significantly more modular and well-organized, suggesting that writing for a future reader changes how students structure their code in the first place, not just how well it's explained afterward.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who track and reflect on their own most frequent error types across a semester show different error frequency in a final comprehensive project. Comparing 100 students who tracked personal error patterns to 100 who did not, error-tracking students showed a 36% reduction in their own previously most-frequent error type by the final project, with no significant change in other, non-tracked error types."',
        response="This study tested whether having students track which specific mistakes they made most often throughout a semester, and reflect on those patterns, helped reduce those same mistakes later. Students who tracked their own error patterns reduced their previously most common mistake by 36% in their final project -- though this improvement was specific to the exact error types they'd tracked, with no real change in other kinds of mistakes they hadn't been paying attention to.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )
    yield SFTExample(
        instruction="How do I use Python's `functools.reduce` to combine a list into a single value, and when should I use it instead of a plain loop?",
        response="""```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]
product = reduce(lambda acc, n: acc * n, numbers)
print(product)  # 120 -- 1*2*3*4*5
```

`reduce` applies a function cumulatively to items in a sequence, carrying an accumulated result forward -- here, each step multiplies the running total (`acc`) by the next number. It's equivalent to:
```python
product = 1
for n in numbers:
    product *= n
```
Honestly, for a simple case like this, the plain loop (or Python's built-in `sum()`/`math.prod()` for exactly this kind of task) is usually more readable than `reduce` with a lambda. `reduce` becomes more genuinely useful for less common combining operations that don't have a dedicated built-in -- if you find yourself reaching for `reduce` frequently for common operations, it's worth checking whether Python already has a more direct built-in for that specific case first.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between `.map()`, `.filter()`, and `.reduce()` conceptually, even across different languages that all have some version of these three?",
        response="""These three represent three distinct, common shapes of data transformation, and most modern languages provide some version of all three (Python has list comprehensions, `filter()`, and `functools.reduce`; JavaScript has `.map()`, `.filter()`, `.reduce()` directly as array methods).

**`map`** transforms each element into something else, one-to-one -- input and output have the same number of elements, just changed. **`filter`** removes elements that don't match a condition -- output has the same or fewer elements, unchanged in value, just a subset. **`reduce`** combines all elements down into a single value -- many elements in, one result out.

Recognizing which shape a task actually needs helps pick the right tool immediately: "convert each price to include tax" is a `map`. "Keep only the students who passed" is a `filter`. "Calculate the total of all prices" is a `reduce`. Many real tasks chain several of these together -- filter first, then map, then reduce -- which is often clearer than one large loop trying to do all three things in a single pass.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this function return a negative average when all the grades are positive numbers?

```python
def get_average(grades):
    total = 0
    count = 0
    for grade in grades:
        total += grade
        count -= 1
    return total / count
```""",
        response="""`count -= 1` decrements `count` on every iteration instead of incrementing it -- `count` starts at `0` and goes negative with each grade processed, ending at a negative number equal to the negative of the grade count. Dividing a positive `total` by a negative `count` produces a negative result, even though every individual grade was positive.

This is very likely a simple typo -- `-=` instead of `+=` -- easy to type by accident and easy to miss on a quick read, since both look similar and the code still runs without crashing, just producing a wrong (and here, obviously implausible) result.
```python
def get_average(grades):
    total = 0
    count = 0
    for grade in grades:
        total += grade
        count += 1
    return total / count
```
A negative average for a set of positive numbers is a strong, immediately visible signal something is wrong -- when you see an obviously implausible result like this, checking each individual operator (`+=` vs `-=`, `<` vs `>`) in the relevant code is often faster than assuming the bug is somewhere more complex.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this API endpoint return stale data even after the underlying record was updated?

```python
cache = {}

def get_student(student_id):
    if student_id in cache:
        return cache[student_id]
    student = db.query(f"SELECT * FROM students WHERE id = {student_id}")
    cache[student_id] = student
    return student

def update_student(student_id, new_data):
    db.execute(f"UPDATE students SET ... WHERE id = {student_id}")
```""",
        response="""`update_student` writes the change directly to the database, but never touches `cache` -- so the next call to `get_student` for that same ID finds the old, now-outdated value still sitting in the cache and returns it, never realizing the underlying data has actually changed. This is a real, common instance of the "caching staleness" trade-off mentioned earlier: caching improves speed but introduces exactly this risk if not handled carefully.

Fix by explicitly invalidating (removing) the cached entry whenever the underlying data changes:
```python
def update_student(student_id, new_data):
    db.execute(f"UPDATE students SET ... WHERE id = {student_id}")
    cache.pop(student_id, None)  # remove stale entry so next read fetches fresh data
```
`.pop(student_id, None)` removes the entry if present, and does nothing (rather than crashing) if it wasn't cached in the first place. The general principle: any code path that changes data needs to also know about, and properly invalidate, any cache that might be holding a now-outdated copy of that same data -- caching and the corresponding invalidation logic have to be maintained together, not just the caching half alone.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between a Type I error and simply making a mistake in your analysis -- how do reviewers tell the two apart?",
        response="""A Type I error (discussed earlier -- a false positive) is an inherent statistical possibility even in a correctly-run study: even with perfect methodology, there's always some chance of concluding an effect is real when it's actually due to chance, which is exactly why significance thresholds exist as a probabilistic acknowledgment of this risk. A mistake in analysis is a genuine error in how the study or analysis was actually conducted -- using the wrong statistical test, a coding error in your analysis script, or misreading your own output.

The distinction matters for how a finding should be treated. A Type I error is an accepted, quantified risk of any properly-run study -- it doesn't mean anything was done wrong, just that the specific result happened to be a false positive, statistically expected to occur some known percentage of the time. A genuine mistake means the study's actual conclusions may be unreliable regardless of statistical theory, because something in the process itself was done incorrectly.

Reviewers typically distinguish these by checking your actual methodology and analysis code (where available) for genuine errors, separately from evaluating whether your statistical approach and reported uncertainty are appropriate given the inherent Type I/Type II trade-offs of your chosen methods. Being transparent about your actual analysis process -- sharing code, being specific about exact procedures -- is what allows this distinction to be checked at all, rather than trusting your conclusions on faith.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a meta-analysis, and how is it different from a systematic review?",
        response="""A systematic review (covered earlier) rigorously identifies and synthesizes existing studies on a question, typically summarized in prose. A meta-analysis goes a step further: it statistically combines the actual numerical results from multiple studies into a single, more precise combined estimate -- essentially treating multiple separate studies as if they were one larger, pooled study.

This matters because a single study might have too small a sample to detect a real but modest effect confidently, while combining several similar studies' data can reveal a real pattern that no individual study had quite enough statistical power to establish on its own.

Not every systematic review can become a meta-analysis -- combining results statistically requires the underlying studies to have measured things in comparable enough ways (similar outcome measures, similar populations) that pooling them actually makes sense. If included studies are too different from each other in method or measurement, forcing a statistical combination can produce a misleading combined number that doesn't represent any of the individual studies well -- in that case, a systematic review without a formal meta-analysis, just a careful narrative synthesis, is the more honest choice.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who participate in structured hackathon-style events during their studies report different comfort with ambiguous, open-ended technical requirements in later coursework. Comparing 90 students with hackathon participation to 90 without, hackathon-experienced students scored significantly higher on a task requiring them to define their own scope for a deliberately vague assignment prompt."',
        response="Researchers compared students who had participated in hackathon-style events to students who hadn't, looking at how comfortable they were handling assignments with deliberately vague, open-ended requirements. The hackathon-experienced students did noticeably better at figuring out their own scope and approach when given an intentionally ambiguous assignment, suggesting hackathon experience builds comfort with the kind of open-ended problem-solving real projects often require.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who receive a short orientation to their course\'s online help forum, including norms for asking effective questions, use the forum differently than students receiving no such orientation. Comparing 130 students given the orientation to 130 without it, oriented students received helpful responses 44% faster on average, largely attributed to asking more specific, well-formed questions from the start."',
        response="This study tested whether giving students a short orientation on how to ask good questions on their course's help forum changed how effectively they used it. Students who got the orientation received helpful responses 44% faster on average -- mostly because they asked more specific, well-formed questions from the beginning, rather than vague ones that took longer for others to understand and answer.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who work on assignments requiring integration with a partially undocumented existing codebase develop different code-reading strategies than students working exclusively on greenfield (from-scratch) projects. Comparing 70 students in each condition, undocumented-codebase students reported using systematic exploration strategies (tracing function calls, testing assumptions) significantly more often when starting new unfamiliar code later in the course."',
        response="Researchers compared students who had to work with an existing, partially undocumented codebase to students who only ever built projects entirely from scratch. Students who'd worked with the undocumented codebase later used much more systematic strategies -- like tracing through function calls and testing their assumptions -- when approaching new unfamiliar code, suggesting that grappling with messy real code built a transferable exploration skill.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who set up automated tests for their own code early in a project, rather than only at the end, show different total debugging time across the full project lifecycle. Comparing 100 students setting up tests early to 100 adding tests only near submission, early-testing students spent 29% less total time debugging across the whole project, despite spending more upfront time on initial test setup."',
        response='This study compared students who wrote automated tests for their code early in a project to students who only added tests near the end, right before submission. Students who tested early spent 29% less total time debugging across the entire project -- even though they spent more time upfront setting up the tests, the early investment paid off by catching problems sooner rather than later.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether students who receive structured feedback specifically on their error message reading and interpretation, separate from general code review, show faster improvement in independent debugging speed. Comparing 85 students given error-message-specific coaching to 85 given only general code feedback, error-message-coached students reduced their average time-to-resolution for compiler errors by 33% over four weeks, compared to 12% in the control group."',
        response='Researchers tested whether giving students feedback specifically on how they read and interpreted error messages, separate from general code feedback, sped up their debugging over time. Students who got this targeted coaching cut their average time to resolve compiler errors by 33% over four weeks, compared to only a 12% improvement for students who just got general code feedback -- suggesting that specifically teaching error-message literacy is more effective than general feedback alone.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students who complete a brief self-assessment quiz before starting a new topic, identifying gaps in prerequisite knowledge, show different learning speed on the new topic compared to students who begin without this self-assessment step. Comparing 110 students doing prerequisite self-assessment to 110 without it, self-assessment students completed the new topic\'s exercises 24% faster, with instructors noting fewer prerequisite-related confusion questions during the unit."',
        response="This study tested whether having students take a quick self-assessment quiz on prerequisite knowledge before starting a new topic -- to identify their own gaps -- helped them learn the new material faster. Students who did the self-assessment completed the new topic's exercises 24% faster, and instructors noticed fewer confused questions related to missing prerequisite knowledge during the unit, suggesting the self-assessment helped students identify and address gaps before they became a bigger problem.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who participate in cross-team code review exercises (reviewing a different team\'s project, not their own) develop different critical evaluation skills than students who only review their own team\'s code. Comparing 75 students doing cross-team review to 75 reviewing only their own team\'s work, cross-team-review students identified 41% more design issues when evaluating an unfamiliar sample project in a later assessment."',
        response="Researchers compared students who reviewed a completely different team's code, versus only their own team's code, to see how it affected their critical evaluation skills. Students who did cross-team reviews identified 41% more design issues when later assessed on an unfamiliar sample project, suggesting that reviewing unfamiliar code -- rather than code you already know well -- builds a stronger, more transferable evaluation skill.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who receive a brief explanation of an algorithm\'s real-world applications before learning its implementation show different long-term recall of the algorithm\'s mechanics compared to students taught implementation first, with applications discussed afterward. Comparing 95 students taught applications-first to 95 taught implementation-first, applications-first students scored 18% higher on a mechanics-recall test given six weeks after the unit ended."',
        response="This study compared students who learned about an algorithm's real-world uses before learning how it actually works, to students taught the implementation first and the applications afterward. Six weeks after the unit ended, students who'd heard about the real-world applications first scored 18% higher on a test of the algorithm's actual mechanics, suggesting that understanding why something matters before learning how it works helps the technical details stick better later.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study investigates whether students who are taught to write a one-sentence summary of what each function in their code does, before writing the function body, show different code clarity in later independent projects. Comparing 100 students taught this summary-first practice to 100 without it, summary-first students\' independent final projects were rated significantly clearer in function purpose by graders blind to the study condition, six months after the practice was taught."',
        response="Researchers tested whether teaching students to write a one-sentence summary of what a function should do, before actually writing the function, led to clearer code later on. Six months after learning this practice, students who'd used it had final projects rated as significantly clearer in terms of what each function actually did, according to graders who didn't know which students had learned the technique -- suggesting the habit stuck and genuinely improved how students structured their code long after the original lesson.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )
    yield SFTExample(
        instruction="How do I check whether a key exists in a dictionary before using it, using the cleanest approach?",
        response="""```python
config = {"api_url": "https://api.example.com"}

if "api_key" in config:
    print(config["api_key"])
else:
    print("No API key configured")
```

`in` checks dictionary keys directly and is the clearest, most idiomatic way to check existence before conditionally acting on it. For the common case of "use this value if present, otherwise use a default," `.get()` (covered earlier) is usually more concise than a full `if`/`else`:
```python
api_key = config.get("api_key", "default-key")
```
Use the explicit `if "key" in dict:` form when you need genuinely different logic for the present-versus-missing cases (like printing a different message, as above), and `.get()` with a default when you just need a fallback value to use directly, without branching logic around it.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="How do I convert a list of dictionaries into a pandas-style table structure without using pandas, just plain Python?",
        response="""```python
students = [
    {"name": "Omol", "grade": 85},
    {"name": "Sara", "grade": 92},
]

# Print as a simple aligned table
for student in students:
    print(f"{student['name']:<10} {student['grade']:>5}")
```

`{student['name']:<10}` left-aligns the name within a 10-character field; `{student['grade']:>5}` right-aligns the grade within 5 characters -- the `<` and `>` control alignment direction, the number sets the minimum field width. This produces a simple, readable aligned table directly in the terminal, without needing an external library for a task this small.

For genuinely larger datasets, or anything needing real tabular operations (filtering, sorting, aggregating across columns), a library like `pandas` becomes worth the dependency -- but for quick scripts or small datasets, plain Python with format specifiers like this is often sufficient and avoids adding a dependency for something this simple.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function raise a ZeroDivisionError intermittently, only for some inputs?

```python
def percentage_complete(done, total):
    return (done / total) * 100

print(percentage_complete(5, 10))  # 50.0, fine
print(percentage_complete(0, 0))   # crashes
```""",
        response="""This isn't actually intermittent -- it fails every single time `total` is `0`, which makes mathematical sense: dividing by zero is undefined, and Python raises `ZeroDivisionError` rather than returning some arbitrary value like `0` or `infinity`. The function happens to work for every input where `total` isn't zero, which can make it feel intermittent if `total=0` is a rare but real case in your actual data (like a student with zero total assignments yet).

Fix by explicitly handling that case before attempting the division:
```python
def percentage_complete(done, total):
    if total == 0:
        return 0
    return (done / total) * 100
```
What "correct" behavior actually means for a `0/0` case depends on your application -- returning `0` (nothing to complete, so 0% complete) is one reasonable choice; returning `None` to signal "not applicable" might be more honest in another context. Either way, the fix is deciding explicitly what should happen, rather than letting the math crash and force an unhandled error onto whoever calls this function.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this React component re-render infinitely, even though useEffect has a dependency array this time?

```jsx
function StudentList() {
    const [students, setStudents] = useState([]);
    const options = { sortBy: "name" };

    useEffect(() => {
        fetchStudents(options).then(data => setStudents(data));
    }, [options]);

    return <ul>{students.map(s => <li key={s.id}>{s.name}</li>)}</ul>;
}
```""",
        response="""`options` is a plain object literal, recreated fresh on *every single render* -- even though its contents (`{ sortBy: "name" }`) never actually change, it's a genuinely new object in memory each time, and React's dependency comparison checks reference equality, not deep content equality. Since `options` is "different" (a new object) on every render, `useEffect` sees its dependency as changed every time and re-runs, which triggers another render, which creates yet another new `options` object, and the cycle continues indefinitely.

Fix by moving the object outside the component (if it's genuinely constant) or memoizing it:
```jsx
const DEFAULT_OPTIONS = { sortBy: "name" };  // created once, outside the component

function StudentList() {
    const [students, setStudents] = useState([]);

    useEffect(() => {
        fetchStudents(DEFAULT_OPTIONS).then(data => setStudents(data));
    }, []);

    return <ul>{students.map(s => <li key={s.id}>{s.name}</li>)}</ul>;
}
```
This is a subtler version of the empty-dependency-array bug from earlier -- the array wasn't actually empty this time, but the dependency it listed was recreated fresh every render anyway, which has the same practical effect. Object and array literals defined directly inside a component's body are a common, easy-to-miss source of this exact problem.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between attrition and non-response in a longitudinal study, and why does the distinction matter for interpreting results?",
        response="""Attrition specifically refers to participants who started your study but dropped out before it finished -- they gave you some data, then stopped. Non-response refers to eligible people who never participated at all, or who skipped specific questions throughout. Both create missing data, but they arise from different points in the process and can bias your findings in different ways.

Attrition is a particular concern in longitudinal studies (discussed earlier) because *why* someone dropped out often connects directly to your research question. If you're studying student persistence in a program, and the students who dropped out of your study were disproportionately the ones who also dropped out of the program itself, your final analysis of "who persisted" is now working with a systematically biased remaining sample -- the very phenomenon you're studying caused some of your missing data.

Reporting attrition rates explicitly, and ideally comparing early characteristics of those who dropped out versus those who stayed (if you have any baseline data on them), helps a reader judge whether attrition likely biased your findings in a particular direction, rather than leaving this as an invisible, unexamined gap in an otherwise polished-looking final analysis.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What does 'matching' mean in the context of a quasi-experimental study design, and how does it help address the lack of random assignment?",
        response="""Matching pairs participants in a treatment group with similar participants in a comparison group, based on relevant characteristics (age, prior performance, background), specifically to make the two groups more comparable when true random assignment wasn't possible.

If you're studying a voluntary tutoring program's effect on grades, students who chose to attend tutoring likely already differ from those who didn't -- perhaps more motivated, or already struggling more. Directly comparing tutored and non-tutored students risks attributing a difference to tutoring itself when it's really about pre-existing differences between who chose to participate.

Matching addresses this by pairing each tutored student with a similar non-tutored student -- similar prior grades, similar demographic background -- so the comparison is between genuinely similar individuals, differing mainly in whether they received tutoring. This strengthens internal validity relative to an unmatched comparison, though it's worth being honest that matching can only control for characteristics you actually measured and matched on -- it can't account for unmeasured differences (like underlying motivation) that might still differ systematically between groups despite matching on the variables you did measure.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who receive a brief tutorial on reading official language documentation, before being directed to it as a primary resource, use documentation more effectively than students directed to documentation without such a tutorial. Comparing 100 students given the tutorial to 100 without it, tutorial students located correct information in official documentation 47% faster on a standardized set of lookup tasks."',
        response='Researchers tested whether teaching students specifically how to read and navigate official programming language documentation helped them use it more effectively later. Students who got this tutorial found correct information in the documentation 47% faster on a set of standardized lookup tasks, suggesting that documentation literacy itself is a skill worth teaching directly, not something students just figure out on their own.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who work through a structured exercise identifying the time and space complexity of their own submitted code show different algorithm choice patterns in later assignments. Comparing 90 students doing complexity self-analysis to 90 without it, self-analysis students chose measurably more efficient algorithms on 34% more subsequent assignments where an efficient approach was relevant."',
        response="This study tested whether having students analyze the time and space complexity of their own code, as a specific exercise, changed what algorithms they chose on later assignments. Students who did this self-analysis exercise chose more efficient algorithms on 34% more of their later assignments where efficiency actually mattered, suggesting that reflecting on your own code's complexity builds better instincts for choosing efficient approaches going forward.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who participate in structured \'rubber duck\' verbal debugging sessions with a non-judgmental listener show reduced debugging time compared to students debugging silently alone. Comparing 80 students in each condition on a matched set of debugging tasks, verbal-debugging students resolved bugs 26% faster on average, with the effect strongest on bugs involving incorrect assumptions rather than simple typos."',
        response='Researchers compared students who talked through their debugging process out loud to a listener, versus students debugging completely silently and alone. The students who talked it through resolved bugs 26% faster on average -- and this benefit was strongest specifically for bugs caused by incorrect assumptions, rather than simple typos, suggesting that verbalizing your reasoning helps most with catching flawed thinking rather than just careless mistakes.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who receive a structured introduction to reading stack traces, with annotated real examples, show different independent error resolution speed than students who learn to read stack traces through unstructured trial and error. Comparing 95 students given structured stack trace training to 95 without it, trained students correctly identified the root cause line in a stack trace 51% more often on a standardized assessment."',
        response='This study tested whether a structured lesson on how to actually read a stack trace -- the error output showing where a program crashed -- with annotated real examples, helped students more than learning through unstructured trial and error. Students who got the structured training correctly identified the actual root cause line in a stack trace 51% more often on a standardized test, suggesting this is a skill that benefits from being explicitly taught rather than picked up informally.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether students who use a personal error log, recording each bug encountered along with its cause and fix, show different repeat-error rates across a semester compared to students without such a log. Comparing 110 students maintaining an error log to 110 without one, error-log students showed a 39% reduction in repeating the exact same category of error across the semester."',
        response='Researchers tested whether having students keep a personal log of every bug they encountered, along with its cause and how they fixed it, reduced how often they made the same mistakes again. Students who kept this error log had a 39% reduction in repeating the same category of error across the semester, suggesting that actively recording and reviewing your own mistakes helps prevent them from becoming a recurring pattern.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students who practice explaining algorithmic time complexity using everyday, non-technical analogies show different ability to explain complexity concepts to a general audience in a later assessment. Comparing 85 students practicing analogy-based explanation to 85 practicing standard technical explanation only, analogy-practicing students scored significantly higher when later asked to explain a complexity concept to a simulated non-technical audience."',
        response="This study compared students who practiced explaining algorithm complexity using everyday analogies to students who only practiced standard technical explanations. When later asked to explain a complexity concept to a simulated non-technical audience, the students who'd practiced analogies did significantly better, suggesting that practicing plain-language explanation is itself a skill that needs deliberate practice, not something that automatically follows from understanding the technical concept.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who receive a short lesson on common cognitive biases in debugging (such as confirmation bias when testing a hypothesis about a bug\'s cause) show different debugging accuracy on ambiguous bug scenarios. Comparing 75 students given the cognitive bias lesson to 75 without it, bias-aware students were 32% less likely to prematurely conclude they\'d found the correct root cause when testing an ambiguous scenario with multiple plausible causes."',
        response="Researchers tested whether teaching students about common cognitive biases that affect debugging -- like the tendency to only look for evidence confirming your first guess -- changed how accurately they debugged tricky, ambiguous bugs. Students who learned about these biases were 32% less likely to jump to a premature, incorrect conclusion about a bug's cause when the scenario had multiple plausible explanations, suggesting that awareness of your own thinking patterns can genuinely improve debugging accuracy.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who set up a personal coding environment identical to what\'s used in professional settings (proper version control, linting, testing framework) from the start of their studies show different first-job onboarding speed than students who only encounter professional tooling for the first time at their job. Comparing 60 graduates with early professional-tooling exposure to 60 without it, early-exposure graduates reported reaching full productivity at their first job 3 weeks faster on average."',
        response="This study compared graduates who'd set up and used professional-grade coding tools -- proper version control, code linting, testing frameworks -- from early in their studies, to graduates who only encountered these tools for the first time once they started their job. The graduates with early exposure reported reaching full productivity at their new job about 3 weeks faster on average, suggesting that familiarity with professional tooling itself, not just coding skill, meaningfully affects how quickly someone can ramp up in a real job.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study investigates whether students who are taught to distinguish between symptoms and root causes when describing a bug (using a structured \'what I see\' versus \'what\'s actually wrong\' framework) resolve bugs with fewer wasted fix attempts than students without this framework. Comparing 100 students taught the framework to 100 without it, framework-trained students needed 28% fewer incorrect fix attempts before resolving each bug correctly."',
        response="Researchers tested whether teaching students to explicitly separate 'what symptom am I seeing' from 'what's actually causing it' -- using a structured framework -- helped them debug more efficiently. Students trained on this framework needed 28% fewer incorrect fix attempts before actually solving each bug, suggesting that clearly distinguishing symptoms from root causes helps students avoid guessing at fixes that don't address the real underlying problem.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )
    yield SFTExample(
        instruction="How do I write a Python function that removes duplicate items from a list while preserving their original order?",
        response="""```python
def remove_duplicates(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

print(remove_duplicates([3, 1, 3, 2, 1, 4]))  # [3, 1, 2, 4]
```

This tracks which items have already been added using a `set` (for fast O(1) membership checks), while building the actual result as a list to preserve the original order items first appeared in. This solves a real limitation of the earlier `list(set(items))` approach for deduplication -- that method drops duplicates but doesn't guarantee any particular order, since sets aren't ordered.

For Python 3.7+, `dict.fromkeys(items)` (shown in an earlier example) achieves the same order-preserving deduplication in one line, since dictionaries now preserve insertion order -- both approaches are valid; this explicit loop version is more readable if you're not already familiar with the `dict.fromkeys()` trick.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a function that finds the intersection of two lists -- items present in both?",
        response="""```python
def intersection(list_a, list_b):
    return list(set(list_a) & set(list_b))

print(intersection([1, 2, 3, 4], [3, 4, 5, 6]))  # [3, 4] (order may vary)
```

`&` between two sets computes their intersection directly -- items present in both. Converting each list to a set first is what makes this operation possible (and fast); sets support this kind of operation natively, while plain lists don't have a built-in intersection operator.

Worth knowing: converting to a set means duplicate values within either original list collapse to one, and the result's order isn't guaranteed to match either input list's original order, since sets are unordered. If you need to preserve the order of one specific list while filtering to only shared items, a list comprehension is more appropriate:
```python
def intersection_ordered(list_a, list_b):
    set_b = set(list_b)
    return [item for item in list_a if item in set_b]
```
This keeps `list_a`'s original order while still getting the speed benefit of checking membership against a set rather than repeatedly scanning `list_b` as a plain list.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function return `True` for a password that clearly doesn't meet the stated requirements?

```python
def is_strong_password(password):
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    return has_digit or has_upper or has_lower

print(is_strong_password("abc"))  # True -- but this has no digit or uppercase
```""",
        response="""The function uses `or` between the three checks, meaning it returns `True` if *any single one* of the three conditions is met -- and `"abc"` does contain lowercase letters, satisfying `has_lower`, which is enough to make the whole `or` expression `True` even though the password is missing a digit and an uppercase letter entirely.

If the actual intent was requiring *all three* conditions, `and` is what was needed instead:
```python
def is_strong_password(password):
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    return has_digit and has_upper and has_lower

print(is_strong_password("abc"))    # False -- correctly rejected
print(is_strong_password("Abc123")) # True -- has all three
```
Mixing up `and` and `or` is a genuinely common logic bug specifically because both produce a valid, running boolean result -- there's no error to alert you, just a condition that's silently more permissive (with `or`) or more restrictive (with `and`) than actually intended. Reading the requirement back in plain English -- "must have a digit AND an uppercase AND a lowercase" -- and matching that word-for-word to the code's actual logic is a good habit for catching this class of bug.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this pagination code sometimes show the same student twice across two pages?

```python
def get_page(students, page_number, page_size=10):
    start = page_number * page_size
    end = start + page_size
    return students[start:end]
```

Calling `get_page(students, 0)` then `get_page(students, 1)` shows student at index 10 in both results.""",
        response="""Looking at this carefully, this specific code is actually correct -- `get_page(students, 0)` returns indices 0-9, and `get_page(students, 1)` returns indices 10-19, with no overlap between them. If a duplicate is genuinely showing up in both pages, the more likely cause is `students` itself changing between the two calls (a new student inserted at the start of the list between the two fetches, shifting every existing student's index by one), not a bug in the slicing logic itself.

This points to a broader, real issue with offset-based pagination on data that can change between page requests: if the underlying list changes between fetching page 0 and page 1, the raw index-based `start`/`end` slicing can genuinely produce duplicates or skipped items, since "index 10" doesn't necessarily refer to the same student anymore. Real production APIs often use "cursor-based" pagination instead -- referencing "give me everything after student ID X" rather than "give me index 10 to 20" -- specifically because it's more robust against the underlying data changing between page requests.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between a research question and a hypothesis, and do I need both?",
        response="""A research question is open-ended, framed as a question you're investigating: "Does mobile banking adoption differ based on network reliability?" A hypothesis is a specific, testable prediction about what you expect to find, usually framed as a statement: "Households with less reliable network access will show lower mobile banking adoption rates."

Whether you need both depends on your study type. Quantitative studies testing a specific predicted relationship typically state an explicit hypothesis, since the statistical test itself is built around testing that specific prediction (recall the null hypothesis discussed earlier). Exploratory or qualitative studies often work from a research question alone, without a specific predicted answer, since the goal is genuinely open exploration rather than testing a predetermined expectation.

A useful check: if you can already state a specific, falsifiable prediction about what you expect to find and why, write it as a hypothesis alongside your research question -- it sharpens your study design and analysis plan. If your study is genuinely exploratory and you don't have a specific prediction (which is a legitimate research approach, not a weaker one), a well-stated research question alone is entirely appropriate, and forcing a hypothesis you don't actually have would misrepresent your study's actual goal.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What does it mean for a research finding to be 'robust,' and how do researchers actually check for this?",
        response="""A robust finding holds up under reasonable variations in how the analysis was done -- different but defensible choices in your analytical approach still point to roughly the same conclusion. A fragile finding only appears when analyzed one very specific way, and disappears or reverses under small, reasonable changes to the analysis.

A common way to check robustness is a "sensitivity analysis" -- deliberately rerunning your analysis with different reasonable choices (excluding potential outliers versus keeping them, using a slightly different statistical model, adjusting how a variable was operationalized) and checking whether your core conclusion changes. If the finding holds across these variations, that's real evidence of robustness. If it only appears under one specific set of analytical choices, that's a warning sign the original finding might be more fragile than it first appeared -- potentially the result of choices that happened to produce a positive-looking result, rather than a genuinely reliable pattern in the data.

Reporting a sensitivity analysis, even briefly, strengthens a paper considerably -- it pre-empts a skeptical reader's natural question ("would this still hold if you'd done it slightly differently?") by actually answering it, rather than leaving the reader to wonder.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who complete a brief self-reflection on their emotional response to receiving critical code review feedback show different subsequent engagement with future feedback. Comparing 90 students doing emotional-response reflection to 90 without it, reflection students were 43% more likely to actually implement suggested changes from their next round of feedback."',
        response='Researchers tested whether having students briefly reflect on how they emotionally reacted to receiving critical feedback on their code changed how they engaged with feedback afterward. Students who did this reflection exercise were 43% more likely to actually implement suggested changes the next time they got feedback, suggesting that processing the emotional reaction to criticism helps students engage with it more constructively rather than dismissing it.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students taught to write descriptive variable names using a specific naming convention framework show different code readability ratings compared to students given only general \'use descriptive names\' guidance. Comparing 100 students taught the specific framework to 100 given general guidance, framework-trained students\' code received significantly higher readability scores from independent reviewers on an unrelated later assignment."',
        response="This study compared students taught a specific, structured framework for naming variables descriptively to students who just got general advice to 'use descriptive names.' On a later, unrelated assignment, the students trained on the specific framework had their code rated as significantly more readable by independent reviewers, suggesting that concrete, structured guidance works better than vague general advice for building this particular habit.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who practice reading and predicting the output of unfamiliar code snippets, without running them, show different debugging accuracy than students who only practice writing their own code. Comparing 85 students doing code-reading prediction exercises to 85 practicing only writing, prediction-practice students identified the correct bug location 37% more often on a set of unfamiliar debugging challenges."',
        response="Researchers compared students who practiced reading unfamiliar code and predicting what it would output, without running it, to students who only practiced writing their own code. The students who practiced this reading-and-predicting exercise correctly identified the bug's actual location 37% more often when faced with unfamiliar debugging challenges, suggesting that reading code carefully is a distinct skill worth practicing on its own, separate from writing code.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who receive feedback that explicitly separates \'what you did well\' from \'what needs improvement,\' rather than blended feedback, show different motivation and revision behavior. Comparing 130 students receiving separated feedback to 130 receiving blended feedback covering the same points, separated-feedback students reported higher motivation and made 19% more substantive revisions to flagged issues."',
        response='This study compared students who got feedback with clearly separated sections for what they did well versus what needed improvement, to students who got the same points blended together in one narrative. Students who got the separated feedback reported feeling more motivated and made 19% more substantive revisions to the issues that were flagged, suggesting that how feedback is structured -- not just its content -- affects how students respond to it.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether students who are taught to write a brief \'assumptions\' section before starting a data analysis task show different awareness of how their analytical choices affected their results. Comparing 75 students writing an assumptions section first to 75 without this requirement, assumptions-first students were significantly more likely to correctly identify how a specific analytical choice could have changed their results when later questioned."',
        response='Researchers tested whether having students write down their assumptions before starting a data analysis task made them more aware of how their choices shaped their results. Students who wrote this assumptions section first were much better able to correctly explain, when later questioned, how a specific analytical choice could have changed their results -- suggesting the exercise built genuine awareness of the analysis process, not just documentation for its own sake.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students who use a structured pre-submission checklist covering common oversight categories (edge cases, error handling, naming) show different first-time assignment pass rates than students without such a checklist. Comparing 140 students using the checklist to 140 without it, checklist-using students had a first-submission pass rate 26 percentage points higher."',
        response='This study compared students who used a structured checklist before submitting assignments -- covering things like edge cases, error handling, and naming -- to students without one. Students using the checklist had a first-submission pass rate 26 percentage points higher, suggesting that a simple structured reminder of common oversight categories catches a meaningful number of avoidable mistakes before submission.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who practice explaining their code choices in terms of trade-offs (why this approach over an alternative) show different critical thinking scores on a later open-ended design assessment. Comparing 90 students practicing trade-off explanation to 90 practicing standard code explanation only, trade-off-practice students scored 24% higher on a later assessment requiring justification of design decisions among multiple valid options."',
        response='Researchers compared students who practiced explaining their code by discussing the trade-offs of their chosen approach versus alternatives, to students who just practiced explaining what their code did. On a later assessment requiring students to justify design decisions among several valid options, the trade-off-practicing group scored 24% higher, suggesting that practicing comparative reasoning specifically builds stronger critical thinking about design choices.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who receive a short lesson on interpreting warning messages (as distinct from errors) show different code quality outcomes than students who are only taught to address hard errors that stop execution. Comparing 100 students taught to address warnings to 100 taught to address only blocking errors, warning-aware students\' final projects had 31% fewer latent bugs identified during independent code review."',
        response="This study tested whether teaching students to pay attention to warning messages -- not just the hard errors that actually stop their code from running -- led to better code overall. Students taught to address warnings had 31% fewer hidden bugs found during independent code review of their final projects, suggesting that warnings often flag real problems that don't show up as an obvious crash but still matter for code quality.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study investigates whether students who work through a structured exercise distinguishing \'necessary complexity\' from \'accidental complexity\' in their own code show different code simplification behavior on subsequent revisions. Comparing 80 students doing this complexity-distinction exercise to 80 without it, exercise-trained students reduced unnecessary code complexity by 33% more when asked to revise a working but overly complicated solution."',
        response="Researchers tested whether teaching students to distinguish between complexity that's genuinely necessary to solve a problem and complexity that's just accidental clutter helped them simplify their own code better. When asked to revise an overly complicated but working solution, students who'd done this exercise reduced unnecessary complexity 33% more than students who hadn't, suggesting that explicitly naming this distinction helps students recognize and cut unnecessary complexity in their own work.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )
    yield SFTExample(
        instruction="How do I write a Python function that groups a list of numbers into 'buckets' based on ranges, like grouping exam scores into grade bands?",
        response="""```python
def grade_band(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

scores = [95, 82, 71, 45, 88]
bands = [grade_band(s) for s in scores]
print(bands)  # ["A", "B", "C", "F", "B"]
```

The order of the `if`/`elif` checks matters here, same principle as the earlier FizzBuzz example -- checking from highest threshold down to lowest means each score is correctly caught by the first (highest) threshold it actually qualifies for. If the checks were written in the opposite order (lowest threshold first), every score above 60 would incorrectly match the first, lowest check before ever reaching the higher ones.

Combined with a `Counter` (from earlier), this pattern lets you build a full grade distribution easily:
```python
from collections import Counter
distribution = Counter(grade_band(s) for s in scores)
```""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a function that checks whether a string is a valid palindrome, ignoring spaces, punctuation, and case?",
        response="""```python
import re

def is_palindrome(text):
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
    return cleaned == cleaned[::-1]

print(is_palindrome("A man, a plan, a canal: Panama"))  # True
```

`re.sub(r'[^a-zA-Z0-9]', '', text)` removes every character that isn't a letter or digit -- the `^` inside the brackets means "not," so this pattern matches anything that *isn't* alphanumeric and replaces it with an empty string, stripping spaces and punctuation. `.lower()` then normalizes case, so "A" and "a" compare as equal. From there, it's the same reverse-and-compare technique as the earlier simple palindrome example, just applied to genuinely messy real-world input instead of a single clean word.

This is a good example of how a "simple" problem (checking a palindrome) often has most of its real complexity in cleaning the input, not in the core logic itself -- the actual palindrome check is one line; getting the input into a comparable form takes the rest.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function raise a StopIteration error instead of returning a default value when no match is found?

```python
students = [{"name": "Omol", "id": 1}, {"name": "Sara", "id": 2}]
result = next(s for s in students if s["id"] == 99)
```""",
        response="""`next()` retrieves the next item from a generator or iterator -- here, a generator expression filtering for a matching student. When there's no matching item at all, there's nothing for `next()` to return, and it raises `StopIteration` rather than silently returning `None` or some other placeholder, since Python has no way to know what an appropriate "nothing found" value should be without being told.

Fix by providing a default as `next()`'s second argument:
```python
result = next((s for s in students if s["id"] == 99), None)
print(result)  # None -- no crash
```
The default (`None` here, but could be any fallback value) is returned instead of raising an error when the generator is exhausted with no match found. This is a genuinely easy mistake to make since `next()` without a default works perfectly fine as long as a match always exists -- the bug only surfaces once you hit a real case where nothing matches, which might not show up during casual testing with data that happens to always contain a match.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this CSS rule not apply, even though the class name is spelled correctly in both the HTML and CSS?

```html
<div class="student-card">Omol</div>
```

```css
.student_card {
    border: 1px solid black;
}
```""",
        response="""The class name in the HTML uses a hyphen (`student-card`), but the CSS selector uses an underscore (`student_card`) -- these are two different strings as far as CSS is concerned, so the selector simply doesn't match the element at all, and no error is raised anywhere to indicate the mismatch.

Fix by making them match exactly:
```css
.student-card {
    border: 1px solid black;
}
```
CSS class name mismatches like this are a common source of "why isn't my style applying" confusion, specifically because there's no error message pointing at the problem -- the browser just silently doesn't apply a rule that doesn't match anything, the same way a Python dictionary lookup with a slightly wrong key silently returns nothing rather than crashing. When a CSS rule seems to have no effect at all, comparing the exact class name spelling (including hyphens versus underscores) between the HTML and CSS is one of the first things worth checking.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="What is a pilot study, and what specifically should I be checking for when I run one before my main study?",
        response="""A pilot study is a small-scale trial run of your study design, conducted before the full study, specifically to catch problems while they're still cheap to fix -- before you've invested the time and resources of running the complete study.

Concrete things worth checking in a pilot: do your survey questions actually make sense to real participants, or do people interpret them differently than you intended? Does your data collection process work smoothly in practice, not just in theory? Is your estimated time-per-participant realistic? Are you actually recruiting participants at the rate you assumed you would, or is your sampling plan more difficult in practice than expected?

A pilot study doesn't need a large sample -- even 5-10 participants can reveal genuine problems with your instrument or process that would otherwise only become apparent once you're deep into full data collection, when fixing them is far more costly. Worth being honest in your final write-up about having run a pilot and what, if anything, you changed as a result -- it's a sign of careful preparation, not something to hide as though your study design emerged fully formed on the first attempt.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What does it mean to 'operationalize' versus 'conceptualize' a variable, and why does getting this order right matter for writing a clear methodology?",
        response="""Conceptualizing a variable means defining what you mean by it in abstract, theoretical terms -- what does "student engagement" mean as a concept? Operationalizing (discussed earlier) means turning that concept into something concretely measurable. The order matters: conceptualize first, then operationalize based on that clear conceptual definition -- not the reverse.

A common weakness in student research writing is operationalizing first, almost by convenience -- "I'll measure engagement as forum posts, since that data is easy to get" -- without first clearly stating what "engagement" conceptually means and checking whether forum posts genuinely represent that concept well. This risks a mismatch between what you claim to be studying and what you're actually measuring, discovered only after data collection when it's too late to fix.

A clear methodology section states both steps explicitly, in order: "We conceptualize engagement as active cognitive and behavioral investment in course material. This was operationalized as: forum post frequency, assignment submission timing relative to deadline, and video lecture completion rate." This makes your reasoning traceable -- a reader can independently judge whether your operational measures genuinely capture your stated concept, rather than having to trust that judgment was made carefully without seeing the reasoning itself.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who use collaborative real-time code editing tools during pair programming exercises show different communication patterns than students using traditional \'driver-navigator\' turn-taking with a single shared screen. Comparing 70 pairs using real-time collaborative editing to 70 pairs using traditional turn-taking, real-time-editing pairs showed 41% more simultaneous verbal discussion during coding, though final code quality was similar between the two groups."',
        response='Researchers compared pairs of students using a real-time collaborative code editor, where both could type at once, to pairs using the traditional method of one person typing while the other watches and suggests. The pairs using real-time collaborative editing talked and discussed the problem together 41% more during coding -- though the final code quality ended up similar either way, suggesting the tool changed how they collaborated without necessarily changing the outcome.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who receive a structured introduction to reading open-source project contribution guidelines, before attempting their first contribution, show different contribution acceptance rates than students attempting contributions without this introduction. Comparing 60 students given the introduction to 60 without it, introduction-trained students had first-contribution pull requests accepted at a rate 2.4 times higher."',
        response="This study tested whether teaching students how to properly read an open-source project's contribution guidelines, before making their first contribution, affected whether that contribution actually got accepted. Students who got this introduction had their first pull requests accepted at a rate 2.4 times higher than students who dove in without reading the guidelines carefully first, suggesting that understanding a project's specific expectations matters a lot for a successful first contribution.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who practice writing precise, falsifiable bug reports (specific steps to reproduce, expected versus actual behavior) show different collaboration efficiency when working with a partner to resolve reported bugs. Comparing 80 student pairs where one partner used structured bug reports to 80 pairs using informal descriptions, structured-report pairs resolved reported bugs 35% faster on average."',
        response='Researchers compared pairs of students where one partner wrote precise, structured bug reports -- specific reproduction steps and expected versus actual behavior -- to pairs using informal, casual bug descriptions. The pairs using structured bug reports resolved the reported bugs 35% faster on average, suggesting that the discipline of writing a precise bug report saves real time for whoever has to actually fix it.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who are taught to distinguish between \'the code doesn\'t work\' and specific, precise problem descriptions when seeking help show different response quality and speed from teaching assistants. Comparing 100 students trained in precise problem description to 100 without such training, precisely-described help requests received substantive responses 58% faster from teaching assistants, based on logged help queue data."',
        response="This study looked at whether teaching students to describe their coding problems precisely -- instead of just saying 'it doesn't work' -- changed how quickly teaching assistants could actually help them. Students trained to describe problems precisely got substantive help 58% faster, based on real help queue data, suggesting that a clear problem description saves real time for both the student and whoever is trying to help them.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether students taught to use a \'five whys\' root cause analysis technique for debugging (repeatedly asking why a symptom occurs to trace back to the underlying cause) show different bug recurrence rates on similar future bugs. Comparing 85 students trained on this technique to 85 without it, trained students had 29% fewer recurrences of structurally similar bugs across the remainder of the semester."',
        response="Researchers tested whether teaching students the 'five whys' technique -- repeatedly asking why a problem occurred to trace back to its true root cause -- reduced how often they ran into similar bugs again later. Students trained on this technique had 29% fewer recurrences of structurally similar bugs for the rest of the semester, suggesting that tracing a bug back to its actual root cause, rather than just patching the visible symptom, prevents the same underlying problem from resurfacing.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students who review their own code against a personal \'lessons learned\' document, updated after each assignment, show different mistake repetition rates than students without such a document. Comparing 95 students maintaining a personal lessons-learned document to 95 without one, document-maintaining students showed a 44% reduction in repeating previously identified personal mistake patterns."',
        response="This study tested whether having students keep and regularly review a personal document of lessons learned from past assignments reduced how often they repeated their own previous mistakes. Students who maintained this document had a 44% reduction in repeating mistake patterns they'd already identified before, suggesting that actively reviewing your own documented lessons -- not just experiencing the mistake once -- is what actually helps it stick.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who practice technical writing by drafting API documentation for their own code show different code interface design quality than students who write code without a documentation-writing requirement. Comparing 70 students required to draft API documentation to 70 without this requirement, documentation-drafting students\' code interfaces were rated significantly more intuitive by independent evaluators unfamiliar with either group\'s code."',
        response="Researchers compared students required to write API documentation for their own code to students with no documentation requirement, looking at the actual quality of how their code was designed to be used. Independent evaluators who didn't know which group was which rated the documentation-writing students' code interfaces as significantly more intuitive, suggesting that the act of writing documentation for how your code should be used actually improves the underlying design, not just the explanation of it.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who complete a structured exercise mapping out data flow through their program before implementation show different bug rates related to state management compared to students who begin implementation without this planning step. Comparing 90 students doing data-flow mapping to 90 coding directly, mapping students had 37% fewer state-related bugs in their final submitted code."',
        response='This study tested whether having students map out how data flows through their program before writing any code reduced bugs related to program state, compared to students who just started coding directly. Students who did this data-flow mapping exercise had 37% fewer state-related bugs in their final code, suggesting that planning how data moves through a program before implementation helps prevent a specific, common category of bug.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study investigates whether students who receive training on writing effective code review comments (specific, actionable, respectful in tone) show different comment usefulness ratings from recipients compared to students without such training. Comparing 80 students trained in code review comment writing to 80 without training, trained students\' review comments were rated as significantly more useful by the students receiving them, based on blind ratings."',
        response="Researchers tested whether teaching students how to write effective code review comments -- specific, actionable, and respectful in tone -- led to more useful feedback for the people receiving it. Based on blind ratings from the recipients, comments from students who'd received this training were rated as significantly more useful than comments from untrained students, suggesting that giving good feedback is itself a skill worth teaching directly, not something people naturally do well without guidance.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )
    yield SFTExample(
        instruction="How do I write a function that validates a list of student records, returning which ones are missing required fields?",
        response="""```python
def find_incomplete_records(students, required_fields):
    incomplete = []
    for student in students:
        missing = [field for field in required_fields if field not in student]
        if missing:
            incomplete.append({"student": student, "missing_fields": missing})
    return incomplete

students = [
    {"name": "Omol", "email": "omol@example.com"},
    {"name": "Sara"},
]
result = find_incomplete_records(students, ["name", "email", "grade"])
```

For each student, an inner list comprehension checks which of the `required_fields` are actually missing from that record. If `missing` is non-empty (a truthy list), that student gets flagged along with exactly which fields it's missing -- more useful than just a pass/fail flag, since it tells you precisely what to fix.

This pattern -- validate a batch of records and collect specific, actionable details about each failure -- is genuinely common in real data-processing code, whether validating user input, imported CSV rows, or API request bodies before further processing.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I write a function that safely retries a flaky operation a limited number of times, with a short pause between attempts?",
        response="""```python
import time

def retry(func, max_attempts=3, delay=1):
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                time.sleep(delay)
    raise last_error

result = retry(lambda: fetch_data_from_flaky_api())
```

`retry` takes any zero-argument function and attempts to call it up to `max_attempts` times, pausing `delay` seconds between failures. If every attempt fails, it re-raises the last error rather than silently giving up -- the caller still finds out something genuinely went wrong, rather than getting back a misleading success or a vague generic failure.

This is a general-purpose wrapper you can reuse around any operation prone to transient failures -- a flaky network call, a database connection that occasionally times out -- without duplicating the retry loop logic at every single call site throughout your codebase.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this function's output change every time it's called, even with the same input?

```python
import random

def assign_group(student_id, groups=["A", "B", "C"]):
    return random.choice(groups)

print(assign_group(101))  # different result every call
```""",
        response="""This is actually working exactly as written -- `random.choice(groups)` deliberately picks a random element every time it's called, with no connection to `student_id` at all. The function's name and parameter suggest it should assign students to groups *consistently* based on their ID, but the actual implementation never uses `student_id` in the logic whatsoever -- it's accepted as a parameter but silently ignored.

If the intent was a consistent, ID-based (not random) assignment, the fix is to actually use the ID in the logic:
```python
def assign_group(student_id, groups=["A", "B", "C"]):
    return groups[student_id % len(groups)]
```
`student_id % len(groups)` maps each ID to a group index consistently -- the same `student_id` always produces the same result, since modulo of the same input always gives the same output. This is a good example of a bug that isn't really a broken line of code -- the `random.choice` call works exactly as intended -- but a mismatch between what the function's name promises and what its actual implementation does.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function's docstring say it returns a sorted list, but the actual output isn't sorted?

```python
def get_top_students(students, n=5):
    \"\"\"Returns the top n students sorted by grade, highest first.\"\"\"
    return students[:n]
```""",
        response="""The function slices the first `n` students from the list, but never actually sorts anything -- it just takes whatever order the list happened to already be in. If `students` isn't already sorted by grade before being passed in, `get_top_students` returns the first `n` students in whatever arbitrary order they arrived in, which has nothing to do with their actual grades.

The docstring makes a promise the code doesn't keep -- fixing it means actually sorting first:
```python
def get_top_students(students, n=5):
    \"\"\"Returns the top n students sorted by grade, highest first.\"\"\"
    sorted_students = sorted(students, key=lambda s: s["grade"], reverse=True)
    return sorted_students[:n]
```
This is a genuinely dangerous category of bug -- the docstring documents intended behavior, and anyone calling this function reasonably trusts that documentation rather than re-reading the implementation every time. A docstring that doesn't match what the code actually does is often worse than no docstring at all, since it actively misleads rather than just leaving a gap. Whenever changing a function's actual behavior, updating its docstring to match is just as important as the code change itself.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between a research paper's abstract and its introduction, given both seem to summarize what the paper is about?",
        response="""Both introduce the paper, but they serve different purposes and lengths. The abstract is a complete, standalone summary -- someone reading only the abstract should understand the study's question, method, key finding, and significance, without needing anything else. It's typically 150-250 words and often the only part many readers will actually read.

The introduction is longer and serves a different job: it builds the case for why the study matters, situates it within existing research, and leads the reader step by step toward your specific research question -- it's persuasive and contextual, not just a compressed summary. A reader shouldn't need the abstract to understand the introduction; the introduction should work as a self-contained argument on its own, distinct from a longer version of the abstract's content.

A common weakness in student writing is an introduction that's essentially just an expanded abstract, repeating the same points in the same order rather than actually building context and motivation. A useful check: does your introduction explain *why* your research question matters and what gap it fills, or does it just restate what you did and found (which belongs in the abstract, and later in the paper itself)?""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="How do I decide what to include in an appendix versus the main body of my paper?",
        response="""The main body should contain everything necessary to understand and evaluate your core argument, on a single read-through, without needing to flip back and forth to supplementary material. The appendix holds material that supports or documents your work but would interrupt the main narrative's flow if included directly -- the full survey instrument, detailed supplementary tables, extended derivations, or raw data summaries.

A useful test: if removing something from the main body would leave a reader confused about your core argument or unable to evaluate your key claims, it belongs in the body. If removing it would only affect a reader's ability to verify fine-grained details or reproduce your exact procedure, it likely belongs in an appendix instead, referenced from the body ("see Appendix A for the full survey instrument") rather than fully reproduced there.

A common mistake is dumping large blocks of raw data or lengthy technical detail directly into the main body "to be thorough," which actually hurts readability rather than helping it -- appendices exist precisely so the main argument stays focused and readable, while supporting detail remains available for anyone who specifically wants to dig into it.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who complete a structured retrospective after each group project (what worked, what didn\'t, what to change) show different team collaboration ratings across a sequence of multiple group projects. Comparing 60 teams doing structured retrospectives to 60 teams without them, retrospective teams showed steadily improving collaboration ratings across projects, while non-retrospective teams showed no significant change."',
        response='Researchers compared student teams that did a structured retrospective after each group project -- reflecting on what worked and what to change -- to teams that skipped this step. Teams that did the retrospectives showed steadily improving collaboration ratings with each new project, while teams without them showed no real improvement over time, suggesting that deliberate reflection is what actually drives improvement, not just repeated practice alone.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who are taught to write clear GitHub issue descriptions (steps to reproduce, expected behavior, environment details) before requesting help show different resolution time from peer helpers. Comparing 90 students trained in issue-writing to 90 without training, well-written issues were resolved by peers 46% faster on average."',
        response='This study tested whether teaching students to write clear, detailed GitHub issues -- including reproduction steps and environment details -- before asking for help changed how quickly peers could actually resolve their problems. Well-written issues from trained students got resolved 46% faster on average, suggesting that a clearly written issue saves real time for whoever ends up helping, not just the person asking.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who practice reading and interpreting API documentation through structured exercises show different independence when integrating a new, unfamiliar third-party library. Comparing 75 students given structured documentation-reading practice to 75 without it, practiced students successfully integrated an unfamiliar library independently 63% more often, without requesting instructor help."',
        response="Researchers compared students who got structured practice reading and interpreting API documentation to students without this practice, then had both groups try integrating an unfamiliar third-party library. Students who'd practiced reading documentation successfully integrated the new library on their own 63% more often, without needing to ask an instructor for help, suggesting that documentation literacy is a distinct, teachable skill that builds real independence.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We examine whether students who receive a brief lesson on distinguishing correlation from causation, applied specifically to their own data analysis projects, show different overreach in their own stated conclusions. Comparing 100 students given this applied lesson to 100 given only the general concept without applied practice, applied-lesson students were 41% less likely to state an unsupported causal claim in their own final project write-up."',
        response='This study tested whether teaching students the difference between correlation and causation, applied directly to their own data projects rather than just as an abstract concept, changed how they wrote up their own conclusions. Students who got this applied practice were 41% less likely to make an unsupported causal claim in their final project write-up, suggesting that applying the concept to your own real work sticks better than learning it only in the abstract.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study evaluates whether students who are taught to write clear pull request descriptions summarizing their changes show different review turnaround time from instructors grading via pull request. Comparing 85 students trained in pull request writing to 85 without training, well-described pull requests received instructor feedback 39% faster on average."',
        response='Researchers tested whether teaching students to write clear, informative pull request descriptions summarizing their changes affected how quickly instructors could review and grade their work. Well-described pull requests from trained students got feedback 39% faster on average, suggesting that a clear summary of what changed and why genuinely speeds up the review process for whoever has to evaluate it.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We investigate whether students who complete a short weekly self-check on their understanding of newly introduced terminology show different long-term retention of technical vocabulary across a semester. Comparing 110 students doing weekly terminology self-checks to 110 without them, self-check students scored 27% higher on a comprehensive terminology test given at course completion."',
        response="This study tested whether having students do a short weekly self-check on new technical vocabulary they'd learned, throughout a semester, improved their long-term retention of those terms. Students who did the weekly self-checks scored 27% higher on a comprehensive terminology test at the end of the course, suggesting that regular, low-stakes self-testing throughout the semester beats hoping vocabulary sticks just from occasional exposure.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper examines whether students who practice articulating the business or user value of a technical feature, before implementing it, show different prioritization decisions when given multiple possible features to build within limited time. Comparing 65 students trained in value-articulation to 65 without training, trained students more frequently chose to implement higher-user-value features first, when time was insufficient to complete every planned feature."',
        response='Researchers compared students who practiced explicitly articulating the actual user or business value of a technical feature, before building it, to students without this practice. When faced with more features to build than time allowed, students trained to think about value first more often chose to prioritize the higher-value features, suggesting that explicitly practicing this kind of reasoning changes how students make real prioritization decisions under time pressure.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='advanced',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who receive structured practice identifying which parts of an error message are relevant versus boilerplate noise show different time-to-diagnosis on unfamiliar errors. Comparing 90 students given this structured practice to 90 without it, practiced students correctly identified the relevant portion of an unfamiliar error message 49% faster on a standardized assessment."',
        response='This study tested whether teaching students to distinguish the genuinely relevant part of an error message from surrounding boilerplate noise helped them diagnose unfamiliar errors faster. Students who got this structured practice correctly identified the relevant part of an unfamiliar error message 49% faster on a standardized test, suggesting that error messages contain a real skill-gap in reading comprehension that benefits from direct teaching, not just experience.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study investigates whether students who maintain a running list of open questions during a project, revisited and updated weekly, show different final project completeness than students without this practice. Comparing 100 students maintaining a weekly open-questions list to 100 without one, list-maintaining students\' final projects had 32% fewer unaddressed edge cases identified during grading."',
        response='Researchers tested whether having students keep a running list of open questions during a project, updated weekly, led to more complete final projects. Students who maintained this list had 32% fewer unaddressed edge cases found in their final projects during grading, suggesting that actively tracking open questions throughout a project -- rather than only thinking about them once, early on -- helps prevent them from being forgotten by the end.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )
    yield SFTExample(
        instruction="How do I write a function that checks whether a list is sorted, without actually sorting it?",
        response="""```python
def is_sorted(items):
    return all(items[i] <= items[i + 1] for i in range(len(items) - 1))

print(is_sorted([1, 2, 2, 5]))  # True
print(is_sorted([3, 1, 2]))     # False
```

`all()` checks every consecutive pair -- `items[i] <= items[i + 1]` -- and returns `True` only if that holds for every adjacent pair in the list, meaning nothing is ever followed by something smaller. `all()` short-circuits, stopping at the first `False` it finds rather than checking every remaining pair unnecessarily, so this is efficient even on a long list that fails early.

This is a genuinely different, cheaper operation than sorting the list to check equality against the original -- `sorted(items) == items` also works, but it does real work building an entirely new sorted list just to answer a yes/no question, while `is_sorted` only needs to scan through once, comparing adjacent pairs directly.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="""Why does this function return an empty list instead of the expected filtered results?

```python
def get_passing_students(students):
    passing = []
    for student in students:
        if student["grade"] >= 60:
            passing = [student]
    return passing
```""",
        response="""`passing = [student]` reassigns `passing` to a brand-new single-item list on every matching iteration, completely overwriting whatever was collected before -- rather than adding to the existing list. By the end of the loop, `passing` only ever contains the *last* matching student, not all of them; it's not empty exactly, but it's silently wrong, missing every match except the final one.

Fix by appending rather than reassigning:
```python
def get_passing_students(students):
    passing = []
    for student in students:
        if student["grade"] >= 60:
            passing.append(student)
    return passing
```
`.append()` adds to the existing list; `=` replaces it entirely. This is an easy typo to make when writing quickly, since both look like reasonable ways to "put a value into passing" -- but they do fundamentally different things, and the resulting bug (silently keeping only the last match) is much subtler than a crash, since the function still runs and returns something that looks plausible at a glance.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the difference between a research summary written for a policy brief and one written for a general news audience?",
        response="""Both simplify academic findings for a non-specialist audience, but they serve different purposes and emphasize different things. A policy brief is written for decision-makers who need to act on the information -- it leads with concrete, actionable recommendations, and typically includes enough methodological detail (sample size, confidence in the finding) for a policymaker to judge how much weight the finding should carry in a real decision.

A general news summary is written for broad public understanding, without an expectation the reader will act on it directly -- it emphasizes what's interesting or relevant to people's everyday lives, and generally includes much less methodological detail, since most readers aren't evaluating it as a basis for a decision.

A useful distinction: a policy brief answers "what should I, a decision-maker, do based on this?" while a news summary answers "what does this mean for people in general, and why might they care?" The same underlying finding might be written up quite differently for each audience -- a policy brief on a study about tutoring effectiveness would emphasize implementation cost and scale; a news piece might emphasize the human story of the students involved.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who set explicit personal deadlines earlier than the official assignment deadline show different final submission quality than students relying only on the official deadline. Comparing 120 students setting self-imposed earlier deadlines to 120 relying on the official deadline alone, self-deadline students submitted work rated significantly higher in polish and completeness, despite no external enforcement of their personal deadline."',
        response='Researchers compared students who set their own personal deadline earlier than the official one to students who just worked toward the official deadline alone. Even though nobody was actually enforcing the personal deadlines, students who set them submitted noticeably more polished and complete work, suggesting that self-imposed earlier deadlines create real, effective pressure even without any outside enforcement.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intro',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who practice writing clear commit messages using a template (\'what changed, why, any side effects\') show different code archaeology speed when investigating an old unfamiliar codebase months later. Comparing 70 students using the template to 70 with no message structure, template-trained students located the reason behind a specific historical code change 54% faster when investigating an unfamiliar old project."',
        response="This study tested whether students who practiced writing commit messages with a structured template -- what changed, why, and any side effects -- could later navigate an old, unfamiliar codebase's history more effectively. Students trained on the template located the reason behind a specific past code change 54% faster than students with no structured message habit, suggesting that consistent commit message discipline pays off specifically when someone has to understand old code later.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This paper investigates whether students who receive a short lesson connecting common programming errors to their real-world consequences (a null pointer error causing a real system outage, for example) show different care and attention to error handling in their own code. Comparing 85 students given this real-world-consequence lesson to 85 given only abstract technical explanation, consequence-aware students included 28% more explicit error handling in a subsequent independent project."',
        response='Researchers tested whether teaching students about real-world consequences of common programming errors -- like a specific type of bug that caused an actual system outage -- changed how carefully they handled errors in their own code afterward. Students who got this real-world context included 28% more explicit error handling in a later independent project, suggesting that connecting abstract technical concepts to real consequences makes students take error handling more seriously in their own work.',
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction="How do I write a function that returns the second-to-last item in a list without knowing its length in advance?",
        response="""```python
def second_to_last(items):
    if len(items) < 2:
        return None
    return items[-2]

print(second_to_last([1, 2, 3, 4]))  # 3
```

Negative indices count from the end of the list: `-1` is the last item, `-2` is the second-to-last, and so on. This works regardless of the list's actual length, since Python resolves `-2` relative to wherever the end actually is, rather than needing you to calculate `len(items) - 2` yourself. The length check upfront handles the edge case of a list with 0 or 1 items, where there's no valid "second-to-last" item to return.""",
        task_type=TaskType.CODE_GENERATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intro",
    )

    yield SFTExample(
        instruction="""Why does this function raise an IndexError when checking for an empty cart, even though it looks like it should handle that case?

```python
def get_last_item(cart):
    if cart == []:
        return None
    return cart[-1]

print(get_last_item(()))  # crashes
```""",
        response="""The check `cart == []` only catches an empty *list* specifically -- but `()` is an empty *tuple*, not a list, so `cart == []` is `False` even though the tuple is genuinely empty. The function proceeds to `cart[-1]`, which raises `IndexError: tuple index out of range` on an empty tuple.

Fix by checking for emptiness in a way that works regardless of the specific container type:
```python
def get_last_item(cart):
    if not cart:
        return None
    return cart[-1]
```
`not cart` is `True` for any empty sequence -- empty list, empty tuple, empty string -- since Python treats empty containers as falsy in a boolean context. This is more robust than checking equality against one specific empty-container literal like `[]`, which only matches that exact type.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="intermediate",
    )

    yield SFTExample(
        instruction="What is the purpose of a Dockerfile, and what does a basic one for a Python web app actually do line by line?",
        response="""A Dockerfile defines a repeatable recipe for building a container image -- a self-contained package including your code, its dependencies, and the environment needed to run it, so it behaves identically regardless of what machine it actually runs on.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "scripts.serve:app", "--host", "0.0.0.0", "--port", "7860"]
```

`FROM` starts from a base image (a minimal Python installation here). `WORKDIR` sets the working directory inside the container. `COPY requirements.txt .` copies just that one file first, then `RUN pip install` installs dependencies -- done in this specific order (before copying the rest of the code) so Docker can reuse this step from cache on future builds if only your code changed, not your dependencies, meaningfully speeding up rebuilds. `CMD` defines what actually runs when the container starts.

This matters for exactly the "works on my machine" problem discussed earlier with environment variables -- a Docker container bundles the entire runtime environment, not just the code, so it behaves the same on your machine, a teammate's machine, or a cloud server.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is a WebSocket, and how is it fundamentally different from a normal HTTP request?",
        response="""A normal HTTP request is a one-shot exchange: the client asks, the server answers, and the connection closes. A WebSocket opens a persistent, two-way connection that stays open, allowing either side to send messages to the other at any time, without needing to start a new request each time.

This matters for anything needing real-time updates -- a live chat, a collaborative document, a live sports score. With plain HTTP, achieving something similar means the client repeatedly polling ("has anything changed yet? has anything changed yet?"), wasting requests and introducing delay. A WebSocket lets the server push a message the instant something happens, with no polling needed at all -- conceptually similar to the webhook pattern discussed earlier, but for an ongoing, bidirectional conversation rather than a single one-time notification.

The trade-off: WebSockets require the server to maintain an open connection per connected client, which uses more server resources than stateless HTTP requests that open and close quickly. For anything that doesn't genuinely need real-time, bidirectional communication, plain HTTP requests remain the simpler, more resource-efficient choice.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is continuous integration (CI), and what does it actually check when a pull request is opened?",
        response="""Continuous integration means automatically building and testing code every time changes are proposed, rather than only manually, occasionally, or right before a release. When a pull request is opened, a CI system typically runs automatically: installing dependencies, running the test suite, checking code style/linting, and sometimes building the project to confirm it compiles or bundles successfully.

The real value: catching problems immediately, while the change is small and fresh in the author's mind, rather than discovering a break days or weeks later after several other changes have piled on top. A failing CI check on a pull request is a clear, automated signal -- "don't merge this yet" -- that doesn't depend on a human remembering to manually run the test suite before merging.

A green (passing) CI check doesn't guarantee the code is bug-free -- it only confirms whatever was actually tested passed. Code with poor test coverage can pass CI while still containing real bugs in the untested parts, which is why CI is a valuable safety net, not a substitute for actually writing meaningful tests in the first place.""",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="""Why does this async function silently return `None` instead of the fetched data, even though the fetch itself succeeds?

```javascript
async function getGrades(studentId) {
    fetch(`/api/students/${studentId}/grades`)
        .then(response => response.json());
}
```""",
        response="""There's no `return` statement anywhere in this function -- the `fetch(...).then(...)` chain runs and does its work, but nothing hands the result back to whoever called `getGrades()`. Since the function is `async` with no explicit `return`, it implicitly resolves to `undefined` (or `None`-equivalent), regardless of what the fetch itself actually returned internally.

Fix by returning the result, either by returning the whole promise chain or using `await`:
```javascript
async function getGrades(studentId) {
    const response = await fetch(`/api/students/${studentId}/grades`);
    return response.json();
}
```
This is a variant of the earlier "forgot to return" bug pattern, specific to async code: it's easy to write a `.then()` chain that does real work internally, and forget that the *function itself* still needs an explicit `return` to actually hand that result back to its caller -- the promise chain completing successfully doesn't automatically mean the function returns anything useful.""",
        task_type=TaskType.CODE_DEBUGGING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )

    yield SFTExample(
        instruction="What is the difference between a research paper's 'implications' and its 'recommendations,' and do I need to write both?",
        response="""Implications describe what a finding *means* more broadly -- theoretical or practical consequences of the result, stated in general terms. Recommendations are specific, actionable suggestions for what someone should actually *do* as a result. A finding can have implications without translating into a clean recommendation, and it's worth being honest when that's the case.

Example: a finding that "mobile banking adoption is driven more by trust in reliability than by cost" has an implication (cost-focused interventions may be less effective than reliability-focused ones) and could support a recommendation (mobile banking providers should invest in visible reliability improvements and communicate them clearly to potential users).

Not every study needs to produce a specific recommendation -- a purely exploratory or theoretical study might reasonably stop at implications, since translating research into a specific action often requires additional context (cost, feasibility, competing priorities) beyond what the study itself examined. Forcing a recommendation your data doesn't actually support, just to seem more useful or applied, is a real overreach worth avoiding -- it's more honest to state implications clearly and note that specific recommendations would require further practical investigation.""",
        task_type=TaskType.RESEARCH_WRITING,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty="advanced",
    )


    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"This study examines whether students who receive a structured introduction to Docker and containerization, before their first team project requiring a shared development environment, report different environment-setup friction than students without this introduction. Comparing 70 students given the Docker introduction to 70 without it, introduced students reported spending 62% less time resolving \'works on my machine\' environment inconsistencies during their first team project."',
        response="Researchers tested whether teaching students about Docker and containerization before their first group project -- where everyone needs the same working environment -- reduced setup problems. Students who got this introduction reported spending 62% less time dealing with 'it works on my machine but not yours' problems during their project, suggesting that understanding containerization tools genuinely helps avoid a common, frustrating source of team friction.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
    )

    yield SFTExample(
        instruction='Summarize this abstract in plain language, in 2-3 sentences:\n\n"We evaluate whether students who set up automated CI checks (tests, linting) on their own personal projects show different code quality habits on assignments where CI is not required. Comparing 60 students with personal-project CI experience to 60 without it, CI-experienced students\' non-CI assignments had 24% fewer style violations and 19% fewer failing edge cases, suggesting the habits transferred beyond the specific context where CI was set up."',
        response="This study tested whether students who set up automated testing and style checks on their own personal coding projects developed better habits that carried over to assignments where those checks weren't required at all. Students with this personal-project CI experience had 24% fewer style violations and 19% fewer failing edge cases on their regular assignments, suggesting the habits they built using CI tools genuinely transferred to situations without those tools present.",
        task_type=TaskType.RESEARCH_SUMMARY,
        language=Language.ENGLISH,
        source="synthetic",
        difficulty='intermediate',
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
