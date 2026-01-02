import re
from typing import Optional


def build_summary_headline(summary: str, max_words: int = 20, max_chars: int = 140) -> str:
    cleaned = summary.replace("*", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        return "No summary available"

    first_sentence = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)[0]
    words = first_sentence.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]).rstrip(",.;:") + "..."
    if len(first_sentence) > max_chars:
        return first_sentence[: max_chars - 3].rstrip(",.;:") + "..."
    return first_sentence
