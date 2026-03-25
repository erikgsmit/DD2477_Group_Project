from elasticsearch import Elasticsearch
import json

with open("config.local.json", "r", encoding="utf-8") as f:
    config = json.load(f)

es = Elasticsearch(
    config["url"],
    basic_auth=(config["username"], config["password"])
)

INDEX_NAME = config["index_name"]

with open("data/sample_article.json", "r") as f:
    doc = json.load(f)

es.index(index=INDEX_NAME, id=doc["id"], document=doc)
print("Document inserted")