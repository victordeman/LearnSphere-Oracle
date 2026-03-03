from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

def init_qdrant():
    client = QdrantClient(host="localhost", port=6333)
    
    collection_name = "student_profiles"
    
    # Try to recreate collection
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=8, distance=Distance.COSINE),
    )
    print(f"Collection '{collection_name}' initialized.")

if __name__ == "__main__":
    init_qdrant()
