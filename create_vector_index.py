import time

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
import os

load_dotenv()

INDEX_NAME = "vector_index"


def create_vector_index():
    client = MongoClient(os.getenv("MONGODB_URI"))
    collection = client["realestate"]["properties"]

    existing = {idx["name"] for idx in collection.list_search_indexes()}
    if INDEX_NAME in existing:
        print(f"Index '{INDEX_NAME}' already exists, skipping creation")
        client.close()
        return

    model = SearchIndexModel(
        name=INDEX_NAME,
        type="vectorSearch",
        definition={
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 384,
                    "similarity": "cosine",
                }
            ]
        },
    )
    collection.create_search_index(model=model)
    print(f"Submitted index '{INDEX_NAME}' — waiting for it to become queryable...")

    while True:
        indexes = list(collection.list_search_indexes(INDEX_NAME))
        if indexes and indexes[0].get("queryable"):
            break
        time.sleep(5)

    print(f"Index '{INDEX_NAME}' is queryable")
    client.close()


if __name__ == "__main__":
    create_vector_index()
