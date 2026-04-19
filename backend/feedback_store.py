"""This file should be removed once we store our feedback in Elasticsearch"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any


class FeedbackStore:
    """Small in-memory store with the same shape as the future ES feedback index."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._articles_by_id: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def add_feedback(
        self,
        article_id: str,
        query: str,
        feedback: int,
        article: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = {
            "article_id": article_id,
            "query": query,
            "feedback": feedback,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        with self._lock:
            self._entries.append(entry)
            if article:
                self._articles_by_id[article_id] = article

        return entry

    def list_feedback(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._entries)

    def list_feedback_articles(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._articles_by_id.values())
