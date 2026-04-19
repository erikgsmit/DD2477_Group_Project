import json

from elasticsearch import Elasticsearch

with open("config.local.json", "r", encoding="utf-8") as f:
    config = json.load(f)

es = Elasticsearch(
    config["url"],
    basic_auth=(config["username"], config["password"]),
)

INDEX_NAME = config["index_name"]
FEEDBACK_INDEX_NAME = config.get("feedback_index_name", "news_feedback")

with open("data/index_mapping.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Index '{INDEX_NAME}' created")
else:
    print(f"Index '{INDEX_NAME}' already exists")

with open("data/feedback_index_mapping.json", "r", encoding="utf-8") as f:
    feedback_mapping = json.load(f)

if not es.indices.exists(index=FEEDBACK_INDEX_NAME):
    es.indices.create(index=FEEDBACK_INDEX_NAME, body=feedback_mapping)
    print(f"Feedback index '{FEEDBACK_INDEX_NAME}' created")
else:
    print(f"Feedback index '{FEEDBACK_INDEX_NAME}' already exists")