"""Shared benchmark questions for GraphRAG and Flat RAG."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUESTIONS_FILE = PROJECT_ROOT / "data" / "benchmark_questions.json"


def _default_questions() -> List[str]:
    return [
        "Who founded OpenAI?",
        "What is the relationship between Microsoft and OpenAI?",
        "Which company invested in OpenAI?",
        "Which company provides cloud resources to OpenAI?",
        "What products did OpenAI develop?",
        "Who is the CEO of OpenAI?",
        "What is the relationship between Google and Alphabet?",
        "Who owns Google?",
        "What technology does NVIDIA develop?",
        "Which company uses Tensor Processing Units (TPUs)?",
        "What are the main business areas of Qualcomm?",
        "Where is Qualcomm headquartered?",
        "What products or technologies is Qualcomm associated with?",
        "What is Vingroup's main business?",
        "Which sectors does Vingroup operate in?",
        "What services does Viettel provide?",
        "In which markets or countries does Viettel expand?",
        "Which company in the corpus is linked to AI and cloud infrastructure?",
        "Which company partners with OpenAI besides Microsoft?",
        "What company developed ChatGPT?",
    ]


def load_benchmark_questions(filepath: str | None = None) -> List[str]:
    """Load benchmark questions from JSON file, falling back to defaults."""
    question_file = Path(filepath) if filepath else DEFAULT_QUESTIONS_FILE

    if question_file.exists():
        with open(question_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            if all(isinstance(item, str) for item in data):
                return data
            if all(isinstance(item, dict) and "question" in item for item in data):
                return [item["question"] for item in data]

    return _default_questions()