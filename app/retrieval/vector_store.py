from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


COLLECTION_NAME = "siemens_documents"
VECTOR_SIZE = 384

client = QdrantClient(url="http://localhost:6333")


def recreate_collection():
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


def index_chunks(chunks, embedding_model):
    vectors = list(
        embedding_model.embed(
            [chunk["text"] for chunk in chunks]
        )
    )

    points = []

    for index, (chunk, vector) in enumerate(
        zip(chunks, vectors)
    ):
        points.append(
            PointStruct(
                id=index,
                vector=vector.tolist(),
                payload=chunk,
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )


def search_vectors(query_vector, top_k=5, query_filter=None):
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    ).points

    return results