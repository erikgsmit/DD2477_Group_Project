from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

load_dotenv(ROOT_DIR / ".env")


def get_es_config() -> dict[str, str]:
    return {
        "url": os.environ["ELASTIC_URL"],
        "username": os.environ["ELASTIC_USERNAME"],
        "password": os.environ["ELASTIC_PASSWORD"],
        "index_name": os.environ["ELASTIC_INDEX_NAME"],
    }