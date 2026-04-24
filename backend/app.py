from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from feedback_store import FeedbackStore, VoteAction
from search.es_search import search_articles
from search.reranker import expand_query_with_rocchio, rerank_with_rocchio


app = FastAPI(title="News Recommendation API")
feedback_store = FeedbackStore()


class FeedbackRequest(BaseModel):
    article_id: str = Field(min_length=1)
    query: str = ""
    feedback: Literal["like", "dislike", "clear"]
    article: dict | None = None
    size: int = Field(default=10, ge=1, le=50)


def _search_with_relevance_feedback(
    query: str,
    size: int,
) -> tuple[list[dict], str, list[str]]:
    """
    Perform a search with relevance feedback using the Rocchio algorithm.
    Returns the list of articles, the expanded query, and the expansion terms (for logging).
    
    Parameters:
        query: The original search query.
        size: The number of articles to return.
    Returns:
        A tuple containing the list of articles, the expanded query, and the expansion terms.
    """
    
    # Retrieve all feedback entries and their associated articles from the feedback index.
    feedback_entries = feedback_store.list_feedback()
    feedback_articles = feedback_store.list_feedback_articles()
    
    # Expand the query using Rocchio based on the feedback entries and articles. 
    expanded_query, expansion_terms = expand_query_with_rocchio(
        query=query,
        feedback_articles=feedback_articles,
        feedback_entries=feedback_entries,
    )
    
    # Perform a search with the expanded query.
    articles = search_articles(query=expanded_query, size=size)

    # If we have feedback, rerank the articles using Rocchio. 
    if feedback_entries:
        articles = rerank_with_rocchio(
            query=query,
            candidates=articles,
            feedback_entries=feedback_entries,
            feedback_articles=feedback_articles,
        )

    return articles, expanded_query, expansion_terms

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/search")
def get_search_results(
    query: str = Query(default="", description="Search query"),
    size: int = Query(default=10, ge=1, le=50),
) -> dict[str, list[dict]]:
    articles, _expanded_query, _expansion_terms = _search_with_relevance_feedback(
        query=query,
        size=size,
    )
    return {"articles": articles}


@app.get("/api/feedback/totals")
def get_feedback_totals() -> dict[str, dict[str, dict[str, Any]]]:
    """Per-article like/dislike counts and current vote from Elasticsearch."""
    return {"totals": feedback_store.list_feedback_totals()}


@app.post("/api/feedback")
def post_feedback(
    payload: FeedbackRequest,
) -> dict[str, Any]:
    """
    Endpoint to receive user feedback on articles.
    Updates vote totals in Elasticsearch, records Rocchio events for like/dislike
    (not for clear), and returns updated search results and all vote totals.
    """

    vote: VoteAction = payload.feedback
    feedback_store.apply_totals_vote(payload.article_id, vote)

    entry: dict[str, Any] | None = None
    if payload.feedback in ("like", "dislike"):
        feedback_value = 1 if payload.feedback == "like" else -1
        entry = feedback_store.add_feedback(
            article_id=payload.article_id,
            query=payload.query,
            feedback=feedback_value,
            article=payload.article,
        )

    articles, expanded_query, expansion_terms = _search_with_relevance_feedback(
        query=payload.query,
        size=payload.size,
    )

    return {
        "feedback": entry,
        "expanded_query": expanded_query,
        "expansion_terms": expansion_terms,
        "articles": articles,
        "totals": feedback_store.list_feedback_totals(),
    }
