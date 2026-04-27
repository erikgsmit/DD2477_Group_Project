# DD2477 Group Project
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/) [![React](https://img.shields.io/badge/React-18-20232A?logo=react&logoColor=61DAFB)](https://react.dev/) [![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript&logoColor=white)](https://www.typescriptlang.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![Elasticsearch](https://img.shields.io/badge/Elasticsearch-search-005571?logo=elasticsearch&logoColor=white)](https://www.elastic.co/elasticsearch) [![Vite](https://img.shields.io/badge/Vite-frontend-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/) [![Docker](https://img.shields.io/badge/Docker-containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

<p align="center">
<img width="500" alt="image" src="https://github.com/user-attachments/assets/52d51b60-6af3-4b48-b0b8-ebca8adbd92a" />
</p>

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
To start, we recommend setting up a virtual environment. In order to do this, you may run the following commands:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Frontend
To install the frontend dependencies, run the following commands:

```bash
cd web
npm install
```

### 3) Elasticsearch

This project uses a local Elasticsearch instance.

An example local configuration is already included in:

```text
backend/config.local.json
```

However, you will need to change this file slightly.

In order to start/setup a local Elasticsearch instance, please follow this guide [Elasticsearch start-local](https://github.com/elastic/start-local?tab=readme-ov-file#-try-elasticsearch-and-kibana-locally).

## How to Execute the Project

Run the project in this order.

### Step 1: Start Elasticsearch
In one terminal, run the following command after setting up your local Elasticsearch instance:
```bash
cd backend/elastic-start-local
./start.sh
```

Wait until Elasticsearch is fully up before continuing.

### Step 2: Crawl the news articles
In another terminal, run:
```bash
cd backend
source .venv/bin/activate
cd crawler
python fetch_links.py
python fetch_articles.py
```
This will retriev all articles from our RSS links.
### Step 3: Create the indices and load the article data
After fetching all the articles, in the same terminal as before, run:
```bash
python create_index.py
python insert_data.py
```

### Step 4: Run the backend API
Now run the following commands (make sure your virtual environment is activated):
```bash
cd backend
uvicorn app:app --reload
```

Default backend URL: `http://127.0.0.1:8000`

Example endpoint:

```text
GET /api/search?query=technology&size=10
```

Health check:

```text
GET /api/health
```

### Step 5: Run the frontend

In a new terminal:

```bash
cd web
npm run dev
```

Open the local Vite URL shown in the terminal, which is typically:

```text
http://127.0.0.1:5173
```

The frontend sends API requests to the backend at `http://127.0.0.1:8000`.

## Contributors
- [Erik Smit](https://github.com/erikgsmit)
- [Juozas Skarbalius](https://github.com/terahidro2003)
- [Daniel Hreggvidsson](https://github.com/DanielHreggvidsson)
- [Joachim Olsson](https://github.com/tipptapp)

