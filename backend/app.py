from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from search.es_search import search_articles


app = FastAPI(title="News Recommendation API")

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
    articles = search_articles(query=query, size=size)
    return {"articles": articles}