from fastembed import TextEmbedding
from qdrant_client import QdrantClient


COLLECTION_NAME = "siemens_documents"


# Load the embedding model once
model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


# Connect to Qdrant
client = QdrantClient(
    url="http://localhost:6333"
)


def search_documents(query: str, top_k: int = 5):
    """
    Search the Siemens document collection
    using semantic vector similarity.
    """

    # Convert query into embedding
    query_embedding = list(
        model.embed([query])
    )[0]

    # Search Qdrant
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=top_k,
        with_payload=True,
    ).points

    return results