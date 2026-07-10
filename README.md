# realestate-rag-api

A Retrieval-Augmented Generation (RAG) API for answering natural-language questions about real estate investment properties, grounded strictly in a MongoDB Atlas Vector Search store. Built as a hands-on project for learning production RAG patterns in Python — FastAPI, MongoDB, and the Anthropic API.

## How It Works

1. **Embed** — The incoming question is embedded locally using `fastembed` (`BAAI/bge-small-en-v1.5`, 384 dimensions).
2. **Retrieve** — That embedding is used to run a MongoDB Atlas `$vectorSearch` aggregation against the `properties` collection, returning the top-N most relevant property documents by cosine similarity.
3. **Generate** — The retrieved property text is passed as context to Claude (Anthropic API), instructed to answer only from the supplied data — no outside knowledge, and an explicit "I don't know" if the answer isn't in the retrieved context.
4. **Respond** — The API returns the question, the grounded answer, and a count of how many source documents were used.

This keeps answers auditable: every answer traces back to specific property records in the vector store.

```
Question ──▶ fastembed (embed) ──▶ MongoDB Atlas $vectorSearch ──▶ Top-N property docs
                                                                          │
                                                                          ▼
                                                       Claude (grounded generation)
                                                                          │
                                                                          ▼
                                                        { question, answer, sources_used }
```

## Tech Stack

- **Python** — core language
- **FastAPI** — API framework
- **MongoDB Atlas** — document store + native `$vectorSearch` index
- **fastembed** — local embedding generation (no external embedding API calls)
- **Anthropic API (Claude)** — grounded answer generation
- **pytest** — test suite (mocked unit tests + an opt-in integration test)

## Prerequisites

- Python 3.10+
- A MongoDB Atlas cluster with a vector search index named `vector_index` on the `properties` collection, indexing the `embedding` field (see `create_vector_index.py`)
- An Anthropic API key
- Property data seeded into MongoDB with matching embeddings (see `seed.py`)

## Setup

```bash
git clone https://github.com/florcavero00-source/realestate-rag-api.git
cd realestate-rag-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`):

```
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster-url>/
ANTHROPIC_API_KEY=sk-ant-...
```

## Seeding Data and Creating the Vector Index

Property documents must be embedded with the same `fastembed` model used at query time and stored in the `properties` collection with an `embedding` field. The Atlas Search index must exist before `$vectorSearch` queries will work.

```bash
python seed.py
python create_vector_index.py
```

## Running the API

```bash
uvicorn main:app --reload
```

### `GET /health`

```json
{ "status": "ok" }
```

### `POST /ask`

```json
{
  "question": "Which properties have the highest cap rate?"
}
```

Response:

```json
{
  "question": "Which properties have the highest cap rate?",
  "answer": "Based on the provided data, ...",
  "sources_used": 3
}
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest              # fast, mocked unit tests only
pytest -m integration  # also hits real MongoDB Atlas + Anthropic API
```

`test.http` (VS Code REST Client extension) is also included for manual, ad-hoc requests against a locally running server.

## Project Structure

```
realestate-rag-api/
├── main.py                   # FastAPI app and routes (/health, /ask)
├── rag.py                    # Core RAG pipeline (retrieval + generation)
├── seed.py                   # Embeds and loads property data into MongoDB
├── create_vector_index.py    # Creates the Atlas $vectorSearch index
├── test_main.py               # pytest suite
├── test.http                  # Manual REST Client requests
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt       # + test tooling
└── pytest.ini                 # pytest config / markers
```

## Design Notes

- **Grounded-only answers**: the prompt explicitly restricts Claude to the retrieved context, reducing hallucination and keeping answers traceable to source documents.
- **Consistent embedding space**: the same `fastembed` model must be used in both `seed.py` and `rag.py` — mismatched models will silently degrade retrieval quality.
- **Configurable retrieval depth**: `n_results` (default 3) controls how many property documents are retrieved per query.

## Status

Personal learning project, actively in progress. Not deployed anywhere — runs locally against a MongoDB Atlas cluster.
