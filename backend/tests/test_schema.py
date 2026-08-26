"""Unit tests for src/sanadi/schema.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sanadi.schema import SFTExample, TaskType, Language


def test_to_chat_format():
    example = SFTExample(
        instruction="What does this function do?",
        response="It returns the sum of a list.",
        task_type=TaskType.CODE_EXPLANATION,
        language=Language.ENGLISH,
        source="unit-test",
    )
    chat = example.to_chat_format()
    assert chat == [
        {"role": "user", "content": "What does this function do?"},
        {"role": "assistant", "content": "It returns the sum of a list."},
    ]


def test_task_type_values():
    assert TaskType.CODE_GENERATION.value == "code_generation"
    assert TaskType.RESEARCH_SUMMARY.value == "research_summary"


def test_language_values():
    assert Language.JUBA_ARABIC.value == "juba_ar"
