# Backend

This folder includes a small Python scaffold for ranked retrieval with
Rocchio relevance feedback.

## API

Run the backend API with:

```bash
uvicorn app:app --reload
```

The search endpoint is:

```text
GET /api/search?query=technology&size=10
```

## Modules

- `search/text_processing.py`
  Tokenization and article text flattening.
- `search/vectorization.py`
  TF-IDF vector construction and cosine similarity.
- `search/rocchio.py`
  The Rocchio query update rule.
- `search/reranker.py`
  Combines base retrieval scores (ranked retrieval) with feedback reranking.
- `demo_rocchio.py`
  Runs the reranker on local sample data (will remove later).

## Expected article json shape

Each retrieved article should look roughly like this.

```python
{
    "id": "test-1",
    "title": "Test Article",
    "summary": "This is a test article.",
    "content": "This is the full content of the test article.",
    "topic": "technology",
    "tags": ["test", "technology"],
    "base_score": 1.42,
}
```

## Expected feedback json shape

Feedback is to be stored separately (seperate index) from the article documents and tied to the query that produced the result set:

```python
{
    "article_id": "test-2",
    "query": "technology ai hardware",
    "feedback": 1,
    "timestamp": "2026-03-31T12:00:00Z",
}
```

- `1` means liked
- `-1` means disliked
- `0` means neither liked or disliked

The idea is that feedback from similar past queries can be reused during reranking
and more similar past queries contribute more strongly to the Rocchio update

