from elasticsearch import Elasticsearch
import json

with open("config.local.json", "r", encoding="utf-8") as f:
    config = json.load(f)

es = Elasticsearch(
    config["url"],
    basic_auth=(config["username"], config["password"])
)

INDEX_NAME = config["index_name"]

with open("data/index_mapping.json", "r") as f:
    mapping = json.load(f)

if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=mapping)
    print("Index created")
else:
    print("Index already exists")