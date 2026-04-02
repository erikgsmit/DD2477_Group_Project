from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from elasticsearch import Elasticsearch


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.local.json"
DEFAULT_RESULT_SIZE = 10
SEARCH_FIELDS = [
	"title^4",
	"summary^2",
	"content",
	"topic^2",
	"tags^2",
	"source",
]
RETURN_FIELDS = [
	"id",
	"url",
	"source",
	"title",
	"author",
	"publishedAt",
	"language",
	"topic",
	"summary",
	"content",
	"tags",
]


def load_config(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_client(config_path: Path = CONFIG_PATH) -> tuple[Elasticsearch, str]:
    config = load_config(config_path)
    client = Elasticsearch(
        config["url"],
        basic_auth=(config["username"], config["password"]),
    )
    return client, str(config["index_name"])


def build_search_body(query: str, size: int) -> dict[str, Any]:
    normalized_query = query.strip()

    if not normalized_query:
        return {
            "size": size,
            "_source": RETURN_FIELDS,
            "sort": [
                {"publishedAt": {"order": "desc", "missing": "_last"}},
                "_score",
            ],
            "query": {"match_all": {}},
        }

    return {
        "size": size,
        "_source": RETURN_FIELDS,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": normalized_query,
                            "fields": SEARCH_FIELDS,
                            "type": "best_fields",
                            "operator": "or",
                            "fuzziness": "AUTO",
                        }
                    }
                ],
                "should": [
                    {"match_phrase": {"title": {"query": normalized_query, "boost": 5}}},
                    {"match_phrase": {"summary": {"query": normalized_query, "boost": 2}}},
                    {"match_phrase": {"topic": {"query": normalized_query, "boost": 3}}},
                    {"match_phrase": {"tags": {"query": normalized_query, "boost": 3}}},
                ],
            }
        },
    }


def normalize_hit(hit: dict[str, Any]) -> dict[str, Any]:
    source = hit.get("_source", {})
    article_id = source.get("id") or hit.get("_id", "")

    return {
        "id": article_id,
        "url": source.get("url", ""),
        "source": source.get("source", ""),
        "title": source.get("title", ""),
        "author": source.get("author", ""),
        "publishedAt": source.get("publishedAt", ""),
        "language": source.get("language", ""),
        "topic": source.get("topic", ""),
        "summary": source.get("summary", ""),
        "content": source.get("content", ""),
        "tags": source.get("tags", []),
        "base_score": float(hit.get("_score") or 0.0),
    }


def search_articles(
	query: str,
	size: int = DEFAULT_RESULT_SIZE,
	client: Elasticsearch | None = None,
	index_name: str | None = None,
) -> list[dict[str, Any]]:
    effective_size = max(1, size)
    search_client = client
    search_index = index_name

    if search_client is None or search_index is None:
        search_client, configured_index_name = create_client()
        search_index = search_index or configured_index_name

    response = search_client.search(
        index=search_index,
        body=build_search_body(query, effective_size),
    )
    hits = response.get("hits", {}).get("hits", [])
    return [normalize_hit(hit) for hit in hits]


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()
    articles = search_articles(query)

    print(json.dumps({"articles": articles}, indent=2))


if __name__ == "__main__":
    main()
