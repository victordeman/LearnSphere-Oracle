from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os

def init_vector_store():
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    if qdrant_host == "localhost":
        client = QdrantClient(path="qdrant_local")
    else:
        client = QdrantClient(host=qdrant_host, port=6333)

    collection_name = "profiles"

    # Check if collection exists
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)

    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=8, distance=Distance.COSINE),
        )
        print(f"Collection '{collection_name}' created.")
    else:
        print(f"Collection '{collection_name}' already exists.")

if __name__ == "__main__":
    init_vector_store()
