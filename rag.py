import logging
import os

from anthropic import Anthropic
from anthropic.types import TextBlock
from dotenv import load_dotenv
from fastembed import TextEmbedding
from pymongo import MongoClient

load_dotenv()

logger = logging.getLogger(__name__)

VECTOR_INDEX_NAME = "vector_index"

# MongoDB
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["realestate"]
properties_collection = db["properties"]

# Embedding model — must match the model used in seed.py, since query
# vectors and stored vectors have to live in the same embedding space.
embedding_model = TextEmbedding()

# Anthropic
anthropic_client = Anthropic()


def retrieve_relevant_properties(question: str, n_results: int = 3) -> list[str]:
    """Retrieve most relevant property documents for a given question via Atlas Vector Search."""
    embeddings = list(embedding_model.embed([question]))
    query_vector = embeddings[0].tolist()

    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": n_results,
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    results = list(properties_collection.aggregate(pipeline))
    documents = [r["text"] for r in results]
    logger.info("Retrieved %d relevant properties for question", len(documents))
    return documents


def generate_answer(question: str, context: list[str]) -> str:
    """Generate a grounded answer using Claude with retrieved context."""
    context_text = "\n\n---\n\n".join(context)

    prompt = f"""You are a real estate investment analyst assistant.

Use ONLY the following property data to answer the question. Do not use any knowledge outside of this data.
If the answer cannot be found in the provided data, say so clearly.

PROPERTY DATA:
{context_text}

QUESTION: {question}

Provide a clear, specific, and helpful answer based strictly on the property data above."""

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    block = response.content[0]
    return block.text if isinstance(block, TextBlock) else ""


def ask_property_question(question: str) -> dict:
    """Main RAG pipeline — retrieve relevant properties and generate answer."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    logger.info("Processing question: %s", question)

    relevant_docs = retrieve_relevant_properties(question)
    answer = generate_answer(question, relevant_docs)

    return {
        "question": question,
        "answer": answer,
        "sources_used": len(relevant_docs)
    }
