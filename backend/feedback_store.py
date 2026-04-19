"""Feedback events and article snapshots stored in a dedicated Elasticsearch index."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from elasticsearch import Elasticsearch

from search.es_search import CONFIG_PATH, create_client, get_feedback_index_name

DOC_KIND_EVENT = "event"
DOC_KIND_SNAPSHOT = "snapshot"
LIST_FEEDBACK_MAX_SIZE = 10_000


class FeedbackStore:
    """
    Elasticsearch-backed store: append-only feedback events plus replace-by-id
    article snapshots (document _id = article_id) for Rocchio vectors.
    """

    def __init__(
        self,
        client: Elasticsearch | None = None,
        feedback_index: str | None = None,
        config_path: Path | None = None,
    ) -> None:
        cfg = config_path or CONFIG_PATH
        if client is None:
            self._client, _ = create_client(cfg)
        else:
            self._client = client
        self._feedback_index = (
            feedback_index if feedback_index is not None else get_feedback_index_name(cfg)
        )

    def add_feedback(
        self,
        article_id: str,
        query: str,
        feedback: int,
        article: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "article_id": article_id,
            "query": query,
            "feedback": feedback,
            "timestamp": timestamp,
        }

        event_doc = {
            "kind": DOC_KIND_EVENT,
            **entry,
        }
        self._client.index(
            index=self._feedback_index,
            id=str(uuid.uuid4()),
            document=event_doc,
        )

        if article:
            snapshot_doc = {
                "kind": DOC_KIND_SNAPSHOT,
                "article_id": article_id,
                "article": article,
                "updated_at": timestamp,
            }
            self._client.index(
                index=self._feedback_index,
                id=article_id,
                document=snapshot_doc,
            )

        return entry

    def list_feedback(self) -> list[dict[str, Any]]:
        response = self._client.search(
            index=self._feedback_index,
            body={
                "size": LIST_FEEDBACK_MAX_SIZE,
                "query": {"term": {"kind": DOC_KIND_EVENT}},
                "sort": [{"timestamp": {"order": "asc"}}],
                "_source": ["article_id", "query", "feedback", "timestamp"],
            },
        )
        hits = response.get("hits", {}).get("hits", [])
        out: list[dict[str, Any]] = []
        for hit in hits:
            src = hit.get("_source") or {}
            out.append(
                {
                    "article_id": src.get("article_id", ""),
                    "query": src.get("query", ""),
                    "feedback": int(src.get("feedback", 0)),
                    "timestamp": src.get("timestamp", ""),
                }
            )
        return out

    def list_feedback_articles(self) -> list[dict[str, Any]]:
        response = self._client.search(
            index=self._feedback_index,
            body={
                "size": LIST_FEEDBACK_MAX_SIZE,
                "query": {"term": {"kind": DOC_KIND_SNAPSHOT}},
                "_source": ["article"],
            },
        )
        hits = response.get("hits", {}).get("hits", [])
        articles: list[dict[str, Any]] = []
        for hit in hits:
            src = hit.get("_source") or {}
            art = src.get("article")
            if isinstance(art, dict):
                articles.append(art)
        return articles
