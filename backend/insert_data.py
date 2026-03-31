from elasticsearch import Elasticsearch
import json

with open("config.local.json", "r", encoding="utf-8") as f:
    config = json.load(f)

es = Elasticsearch(
    config["url"],
    basic_auth=(config["username"], config["password"])
)

INDEX_NAME = config["index_name"]

#CODE FROM FIRST ITERATION, KEPT FOR REFERENCE
#with open("data/sample_article.json", "r") as f:
    #doc = json.load(f)

#es.index(index=INDEX_NAME, id=doc["id"], document=doc)
#print("Document inserted")


# 1) source file (Might change this to cleaner data later)
with open("crawler/data/raw/articles_raw.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Expect articles is a list
if not isinstance(articles, list):
    raise ValueError("articles_raw.json must contain a JSON array of article objects")

inserted=0
#articles_raw has url, title, content, content_length, sourse_domain and published
for article in articles:
    article_id = article["url"]  # Using URL as the document ID for uniqueness
    if article_id is None:
        print(f"Skipping article with missing URL: {article}")
        continue

    doc = {
        "url": article["url"],
        "title": article["title"],
        "content": article["content"],
        "content_length": article.get("content_length", len(article["content"])),
        "source_domain": article.get("source_domain", ""),
        "published": article.get("published", "")
    }

    es.index(index=INDEX_NAME, id=article_id, document=doc)
    inserted += 1
print(f"Inserted {inserted} docs to {INDEX_NAME}")