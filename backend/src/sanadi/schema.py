"""
Data schema for Sanadi AI phase 1 SFT examples.

Every training example is one of two task types: coding or research. Both share
a common envelope so the data pipeline, fine-tuning, and eval code can treat them
uniformly, while `task_type` lets you slice metrics and dataset composition by type.

Language is tracked explicitly rather than inferred, because a meaningful share of
phase 1 data is synthetically generated bilingual content (see prepare_data.py) —
knowing which language a given example targets matters for both training-data
balance and evaluation (a Juba Arabic response needs a Juba Arabic-fluent reviewer,
not an automated metric).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskType(str, Enum):
    CODE_GENERATION = "code_generation"
    CODE_DEBUGGING = "code_debugging"
    CODE_EXPLANATION = "code_explanation"
    RESEARCH_SUMMARY = "research_summary"
    RESEARCH_WRITING = "research_writing"


class Language(str, Enum):
    ENGLISH = "en"
    JUBA_ARABIC = "juba_ar"
    MIXED = "mixed"  # code-switched examples — common in real usage


@dataclass
class SFTExample:
    """One supervised fine-tuning example."""

    instruction: str          # the user-facing prompt / task
    response: str              # the target completion
    task_type: TaskType
    language: Language
    source: str                 # provenance: "synthetic", "curated", "user-collected", etc.
    difficulty: Optional[str] = None   # "intro" | "intermediate" | "advanced" — for eval slicing
    metadata: dict = field(default_factory=dict)

    def to_chat_format(self) -> list[dict]:
        """Convert to the chat-message format Qwen2.5-Coder-Instruct expects."""
        return [
            {"role": "user", "content": self.instruction},
            {"role": "assistant", "content": self.response},
        ]
