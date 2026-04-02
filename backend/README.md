# Backend

This folder includes a small Python scaffold for ranked retrieval with
Rocchio relevance feedback.

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

## For local elasticsearch

After setting up your own localelastic search on your docker (https://github.com/elastic/start-local?tab=readme-ov-file#-try-elasticsearch-and-kibana-locally) do a pip install 
elasticsearch (or run pip install -r requirements.txt). Then alter the information like username and password which apply to you on config.local.json (DO NOT PUSH THOSE CONFIG CHANGES) then run
"python create_index.py" which creates the index on your local elastic search. Then run "python insert_data.py" which should insert the articles from articles_raw.json into your
index. 
