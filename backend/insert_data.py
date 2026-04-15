from __future__ import annotations

from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.local.json"
DEFAULT_INPUT_PATH = BASE_DIR / "crawler" / "data" / "raw" / "articles_raw.json"

def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_articles(input_path: Path) -> list[dict]:
    with input_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, list):
        raise ValueError(f"Expected a list of articles in {input_path}")

    return [article for article in payload if isinstance(article, dict)]


def build_article_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def normalize_source(url: str, source_domain: str) -> str:
    domain = source_domain or urlparse(url).netloc
    return domain.removeprefix("www.")


def build_summary(content: str, limit: int = 320) -> str:
    if not content:
        return ""

    trimmed = " ".join(content.split())
    if len(trimmed) <= limit:
        return trimmed

    cut_off = trimmed[:limit].rsplit(" ", 1)[0]
    return f"{cut_off}..." if cut_off else f"{trimmed[:limit]}..."


def normalize_published_at(value: str) -> str | None:
    if not value:
        return None

    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError, IndexError, OverflowError):
        return None


def transform_article(raw_article: dict) -> dict | None:
    url = str(raw_article.get("url", "")).strip()
    title = str(raw_article.get("title", "")).strip()
    content = str(raw_article.get("content", "")).strip()

    if not url or not title or not content:
        return None

    source_domain = str(raw_article.get("source_domain", "")).strip()
    published = str(raw_article.get("published", "")).strip()
    source = normalize_source(url, source_domain)

    return {
        "id": build_article_id(url),
        "url": url,
        "source": source,
        "author": "",
        "title": title,
        "publishedAt": normalize_published_at(published),
        "language": "en",
        "topic": source,
        "summary": build_summary(content),
        "content": content,
        "tags": [source],
    }


def build_bulk_actions(index_name: str, articles: list[dict]) -> list[dict]:
    actions: list[dict] = []

    for raw_article in articles:
        document = transform_article(raw_article)
        if document is None:
            continue

        actions.append(
            {
                "_index": index_name,
                "_id": document["id"],
                "_source": document,
            }
        )

    return actions


def main() -> None:
    config = load_config(CONFIG_PATH)
    input_path = DEFAULT_INPUT_PATH

    if not input_path.exists():
        raise FileNotFoundError(
            f"Crawler output not found at {input_path}. Run the crawler first."
        )

    es = Elasticsearch(
        config["url"],
        basic_auth=(config["username"], config["password"]),
    )

    index_name = config["index_name"]
    raw_articles = load_articles(input_path)
    actions = build_bulk_actions(index_name, raw_articles)

    if not actions:
        print("No valid crawler articles found to index")
        return

    indexed_count, errors = bulk(es, actions, raise_on_error=False)

    print(f"Indexed {indexed_count} documents into '{index_name}'")
    if errors:
        print(f"Skipped {len(errors)} failed indexing operations")


if __name__ == "__main__":
    main()
