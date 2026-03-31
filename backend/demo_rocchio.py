"""
TO BE REMOVED!!!

Demo script to show how to use the Rocchio reranking function with sample articles and feedback entries.
This is a simplified example for demonstration purposes, and in a real system, the articles and feedback will
come from the search index and user interactions, respectively.

The basis is to have 2 indexes, one for articles and one for feedback. The articles index contains the news articles
with their metadata and content, while the feedback index stores user feedback entries that link back to the articles and queries.
"""

from __future__ import annotations

import json
from pathlib import Path

from search.reranker import rerank_with_rocchio

DATA_DIR = Path(__file__).parent / "data"


# Below is some sample data loading and a main function to demonstrate how to use the reranking with Rocchio based on the sample articles and feedback entries.
def load_sample_articles() -> list[dict]:
    with open(DATA_DIR / "sample_article.json", "r", encoding="utf-8") as handle:
        first_article = json.load(handle)

    return [
        {
            **first_article,
            "id": "test-1",
            "base_score": 1.4,
        },
        {
            "id": "test-2",
            "url": "https://example.com/news/ai-chip-design",
            "source": "Tech Chronicle",
            "title": "AI chip design speeds up data-center workloads",
            "author": "Jane Doe",
            "publishedAt": "2026-03-18T08:30:00Z",
            "language": "en",
            "topic": "technology",
            "summary": "New accelerator hardware improves machine learning throughput.",
            "content": "Researchers and hardware companies are improving accelerator design for AI workloads.",
            "tags": ["ai", "chips", "technology"],
            "base_score": 1.1,
        },
        {
            "id": "test-3",
            "url": "https://example.com/news/football-finals",
            "source": "Sports Daily",
            "title": "Local club reaches football finals after late comeback",
            "author": "Sam Smith",
            "publishedAt": "2026-03-17T18:00:00Z",
            "language": "en",
            "topic": "sports",
            "summary": "The team secured a dramatic win in the semifinal.",
            "content": "Fans celebrated after the club overturned a deficit and reached the finals.",
            "tags": ["sports", "football"],
            "base_score": 0.95,
        },
        {
            "id": "test-4",
            "url": "https://example.com/news/cloud-infrastructure",
            "source": "Infra Weekly",
            "title": "Cloud providers invest in AI-ready data center infrastructure",
            "author": "Alex Kim",
            "publishedAt": "2026-03-19T09:15:00Z",
            "language": "en",
            "topic": "technology",
            "summary": "Operators are redesigning data centers to support larger machine learning workloads.",
            "content": "New power, cooling, and server layouts are being deployed to support AI hardware and model training.",
            "tags": ["cloud", "ai", "infrastructure"],
            "base_score": 1.25,
        },
        {
            "id": "test-5",
            "url": "https://example.com/news/mobile-processors",
            "source": "Device World",
            "title": "Mobile processor vendors bring AI features to edge devices",
            "author": "Maria Chen",
            "publishedAt": "2026-03-16T13:20:00Z",
            "language": "en",
            "topic": "technology",
            "summary": "On-device inference is becoming more efficient on consumer hardware.",
            "content": "Chip vendors are optimizing mobile processors for local AI assistants and edge inference workloads.",
            "tags": ["ai", "hardware", "mobile"],
            "base_score": 1.05,
        },
        {
            "id": "test-6",
            "url": "https://example.com/news/energy-grid",
            "source": "World Report",
            "title": "Energy grid upgrades support growing industrial demand",
            "author": "Liam Patel",
            "publishedAt": "2026-03-15T07:45:00Z",
            "language": "en",
            "topic": "business",
            "summary": "Utilities are modernizing transmission systems for new factories and data centers.",
            "content": "Power grid investment is increasing as heavy industry and computing infrastructure require more stable supply.",
            "tags": ["energy", "infrastructure", "business"],
            "base_score": 0.88,
        },
        {
            "id": "test-7",
            "url": "https://example.com/news/robotics-lab",
            "source": "Future Science",
            "title": "Robotics lab combines vision models with custom hardware",
            "author": "Noah Eriksson",
            "publishedAt": "2026-03-14T11:10:00Z",
            "language": "en",
            "topic": "science",
            "summary": "Researchers are combining computer vision and optimized chips for autonomous systems.",
            "content": "A robotics team reported gains from pairing compact vision models with specialized hardware accelerators.",
            "tags": ["robotics", "vision", "hardware"],
            "base_score": 1.18,
        },
    ]


def load_sample_feedback() -> list[dict]:
    return [
        {
            "article_id": "test-2",
            "query": "ai hardware",
            "feedback": 1,
            "timestamp": "2026-03-31T08:00:00Z",
        },
        {
            "article_id": "test-3",
            "query": "football finals",
            "feedback": -1,
            "timestamp": "2026-03-31T08:05:00Z",
        },
        {
            "article_id": "test-1",
            "query": "sports finals",
            "feedback": 1,
            "timestamp": "2026-03-31T08:10:00Z",
        },
        {
            "article_id": "test-4",
            "query": "data center ai",
            "feedback": 1,
            "timestamp": "2026-03-31T08:12:00Z",
        },
        {
            "article_id": "test-5",
            "query": "edge ai devices",
            "feedback": 1,
            "timestamp": "2026-03-31T08:14:00Z",
        },
        {
            "article_id": "test-6",
            "query": "industrial energy",
            "feedback": -1,
            "timestamp": "2026-03-31T08:16:00Z",
        },
        {
            "article_id": "test-7",
            "query": "robotics hardware",
            "feedback": 1,
            "timestamp": "2026-03-31T08:18:00Z",
        },
    ]


def main() -> None:
    query = "technology ai hardware"

    # Load sample articles (in a real system, these would come from the search index based on the initial retrieval for the query)
    articles = load_sample_articles()

    # Get sample feedback (stored in memory for this demo, but in a real system this would come from the FeedbackStore and ultimately from user interactions)
    feedback_entries = load_sample_feedback()

    # Rerank the articles based on the query and the feedback entries using Rocchio
    reranked = rerank_with_rocchio(
        query=query,
        candidates=articles,
        feedback_entries=feedback_entries,
    )

    print(f"Query: {query}")
    print("Reranked articles:")
    for article in reranked:
        print(
            f"- {article['id']}: final_score={article['final_score']}, "
            f"base_score={article.get('base_score', 0.0)}, "
            f"feedback_score={article['feedback_score']}, title={article['title']}"
        )


if __name__ == "__main__":
    main()
