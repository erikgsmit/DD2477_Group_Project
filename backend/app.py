from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from feedback_store import FeedbackStore
from search.es_search import search_articles
from search.reranker import expand_query_with_rocchio, rerank_with_rocchio


app = FastAPI(title="News Recommendation API")
feedback_store = FeedbackStore()


class FeedbackRequest(BaseModel):
    article_id: str = Field(min_length=1)
    query: str = ""
    feedback: Literal["like", "dislike"]
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


@app.post("/api/feedback")
def post_feedback(
    payload: FeedbackRequest,
) -> dict[str, list[dict] | dict[str, str | int] | str | list[str]]:
    """
    Endpoint to receive user feedback on articles. 
    Stores the feedback in Elasticsearch and returns an updated search result based on the feedback.
    """
    
    feedback_value = 1 if payload.feedback == "like" else -1
    
    # Add feedback event and optional article snapshot to the feedback index.
    entry = feedback_store.add_feedback(
        article_id=payload.article_id,
        query=payload.query,
        feedback=feedback_value,
        article=payload.article,
    )

    # Perform a search with relevance feedback to get updated results based on the new feedback.
    articles, expanded_query, expansion_terms = _search_with_relevance_feedback(
        query=payload.query,
        size=payload.size,
    )

    return {
        "feedback": entry,
        "expanded_query": expanded_query,
        "expansion_terms": expansion_terms,
        "articles": articles,
    }
