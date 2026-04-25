# DD2477 Group Project

This repository contains a news retrieval and recommendation system with:
- a Python backend API for indexing/searching articles and relevance feedback
- crawler scripts for collecting recent news content
- a React web interface for running queries

## Requirements

Install the following before running:

- Python 3.10+ (recommended)
- Node.js 18+ and npm
- Docker (for local Elasticsearch)

## Project Layout

```text
.
├── backend/   # FastAPI service, search logic, crawler scripts
└── web/       # React + Vite frontend
```

## Setup

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Frontend

```bash
cd web
npm install
```

### 3) Elasticsearch

Start a local Elasticsearch instance with Docker, then configure:

```text
backend/config.local.json
```

Reference: [Elastic start-local guide](https://github.com/elastic/start-local?tab=readme-ov-file#-try-elasticsearch-and-kibana-locally)

## How to Execute the Project

### Step A: Create index and load data

```bash
cd backend
source .venv/bin/activate
python create_index.py
python insert_data.py
```

### Step B: Run backend API

```bash
cd backend
source .venv/bin/activate
uvicorn app:app --reload
```

Default backend URL: `http://127.0.0.1:8000`

Example endpoint:

```text
GET /api/search?query=technology&size=10
```

### Step C: Run frontend

In a new terminal:

```bash
cd web
npm run dev
```