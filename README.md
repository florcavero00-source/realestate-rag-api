# realestate-rag-api
A Retrieval-Augmented Generation (RAG) API for answering natural-language questions about property/real estate data, grounded strictly in a MongoDB Atlas vector store. Built as a hands-on exploration of production RAG patterns for a real estate investment analysis use case.

RAG API for querying real estate investment properties using natural language — built with Python, FastAPI, MongoDB, and Anthropic Claude.


How It Works


Embed — The incoming question is embedded using FastEmbed.
Retrieve — The embedding is used to run a MongoDB Atlas Vector Search ($vectorSearch) against a properties collection, returning the top-N most relevant property documents by cosine/vector similarity.
Generate — The retrieved property text is passed as context to Claude (Anthropic API), which is instructed to answer only from the supplied data — no outside knowledge, and an explicit "I don't know" if the answer isn't in the retrieved context.
Respond — The API returns the question, the grounded answer, and a count of how many source documents were used.


This keeps answers auditable and reduces hallucination risk: every answer traces back to specific property records in the vector store.

Tech Stack


Python — core language
FastAPI — API framework (assumed — update if different)
MongoDB Atlas — document store + native vector search index
FastEmbed — local embedding generation (no external embedding API calls)
Anthropic API (Claude) — grounded answer generation


Architecture

Question ──▶ FastEmbed (embed) ──▶ MongoDB Atlas $vectorSearch ──▶ Top-N property docs
                                                                          │
                                                                          ▼
                                                       Claude (grounded generation)
                                                                          │
                                                                          ▼
                                                        { question, answer, sources_used }

Prerequisites


Python 3.10+
A MongoDB Atlas cluster with a vector search index named vector_index on the properties collection, indexing the embedding field
An Anthropic API key
Property data seeded into MongoDB with matching embeddings (see seed.py)


Setup

bashgit clone https://github.com/flocavero00-source/realestate-rag-api.git
cd realestate-rag-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

Create a .env file:

MONGODB_URI=mongodb+srv://<user>:<password>@<cluster-url>/
ANTHROPIC_API_KEY=sk-ant-...

Seeding Data

Property documents must be embedded with the same FastEmbed model used at query time and stored in the properties collection with an embedding field, before the vector index can return meaningful results.

bashpython seed.py

(Update this section with the actual seeding process/data source once finalized.)

Usage

pythonfrom rag import ask_property_question

result = ask_property_question("What's the average cap rate for properties in the dataset?")
print(result)
# {
#   "question": "...",
#   "answer": "...",
#   "sources_used": 3
# }

API

(Fill in actual endpoint(s) once the FastAPI app is included — e.g.:)

POST /ask
Content-Type: application/json

{
  "question": "Which properties have the highest rental yield?"
}

Response:

json{
  "question": "Which properties have the highest rental yield?",
  "answer": "Based on the provided data, ...",
  "sources_used": 3
}

Project Structure

realestate-rag-api/
├── rag.py           # Core RAG pipeline (retrieval + generation)
├── seed.py          # Embeds and loads property data into MongoDB
├── main.py          # FastAPI app / route definitions (if applicable)
├── requirements.txt
└── .env.example

Design Notes


Grounded-only answers: the prompt explicitly restricts Claude to the retrieved context, reducing hallucination and keeping answers traceable to source documents.
Consistent embedding space: the same FastEmbed model must be used in both seed.py and rag.py — mismatched models will silently degrade retrieval quality.
Configurable retrieval depth: n_results (default 3) controls how many property documents are retrieved per query.


Status

Portfolio / in-progress project. Deployment status — running on AWS ECS, and local.
