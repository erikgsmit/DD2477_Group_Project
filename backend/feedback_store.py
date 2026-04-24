"""Feedback events and article snapshots stored in a dedicated Elasticsearch index."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from search.es_search import CONFIG_PATH, create_client, get_feedback_index_name

DOC_KIND_EVENT = "event"
DOC_KIND_SNAPSHOT = "snapshot"
DOC_KIND_TOTALS = "totals"
LIST_FEEDBACK_MAX_SIZE = 10_000

VoteAction = Literal["like", "dislike", "clear"]


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

    @staticmethod
    def _totals_document_id(article_id: str) -> str:
        return f"totals:{article_id}"

    def _get_totals_source(self, article_id: str) -> dict[str, Any]:
        doc_id = self._totals_document_id(article_id)
        try:
            response = self._client.get(index=self._feedback_index, id=doc_id)
        except NotFoundError:
            return {
                "kind": DOC_KIND_TOTALS,
                "article_id": article_id,
                "like_count": 0,
                "dislike_count": 0,
                "current": None,
            }
        source = response.get("_source") or {}
        return {
            "kind": DOC_KIND_TOTALS,
            "article_id": article_id,
            "like_count": int(source.get("like_count", 0)),
            "dislike_count": int(source.get("dislike_count", 0)),
            "current": source.get("current"),
        }

    def apply_totals_vote(self, article_id: str, vote: VoteAction) -> dict[str, Any]:
        """
        Update per-article like/dislike counters for the active vote (current). 
        Persists a single totals document per article.
        """
        doc = self._get_totals_source(article_id)
        like_count = int(doc["like_count"])
        dislike_count = int(doc["dislike_count"])
        current = doc.get("current")

        if vote == "clear":
            if current == "like":
                like_count = max(0, like_count - 1)
                current = None
            elif current == "dislike":
                dislike_count = max(0, dislike_count - 1)
                current = None
        elif vote == "like":
            if current == "like":
                like_count = max(0, like_count - 1)
                current = None
            else:
                if current == "dislike":
                    dislike_count = max(0, dislike_count - 1)
                like_count += 1
                current = "like"
        elif vote == "dislike":
            if current == "dislike":
                dislike_count = max(0, dislike_count - 1)
                current = None
            else:
                if current == "like":
                    like_count = max(0, like_count - 1)
                dislike_count += 1
                current = "dislike"

        payload = {
            "kind": DOC_KIND_TOTALS,
            "article_id": article_id,
            "like_count": like_count,
            "dislike_count": dislike_count,
            "current": current,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._client.index(
            index=self._feedback_index,
            id=self._totals_document_id(article_id),
            document=payload,
        )
        return {
            "like_count": like_count,
            "dislike_count": dislike_count,
            "current": current,
        }

    def list_feedback_totals(self) -> dict[str, dict[str, Any]]:
        """Return map article_id -> {like_count, dislike_count, current}."""
        response = self._client.search(
            index=self._feedback_index,
            body={
                "size": LIST_FEEDBACK_MAX_SIZE,
                "query": {"term": {"kind": DOC_KIND_TOTALS}},
                "_source": ["article_id", "like_count", "dislike_count", "current"],
            },
        )
        hits = response.get("hits", {}).get("hits", [])
        out: dict[str, dict[str, Any]] = {}
        for hit in hits:
            src = hit.get("_source") or {}
            aid = src.get("article_id")
            if not isinstance(aid, str) or not aid:
                continue
            out[aid] = {
                "like_count": int(src.get("like_count", 0)),
                "dislike_count": int(src.get("dislike_count", 0)),
                "current": src.get("current"),
            }
        return out

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
