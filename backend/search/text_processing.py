from __future__ import annotations

import re
from typing import Iterable

TOKEN_PATTERN = re.compile(r"\b[a-z0-9]+\b")


def tokenize(text: str) -> list[str]:
    """Split text into lowercase alphanumeric tokens."""
    return TOKEN_PATTERN.findall(text.lower())


def preprocess_text(text: str, stopwords: Iterable[str] | None = None) -> list[str]:
    """Tokenize text and remove simple stopwords."""
    return [token for token in tokenize(text)]


def article_to_text(article: dict) -> str:
    """Flatten the article fields used for retrieval and feedback into one string."""
    parts: list[str] = []

    for field in ("title", "summary", "content", "topic"):
        value = article.get(field)
        if isinstance(value, str) and value.strip():
            parts.append(value)

    tags = article.get("tags")
    if isinstance(tags, list):
        parts.extend(str(tag) for tag in tags if tag)

    return " ".join(parts)
