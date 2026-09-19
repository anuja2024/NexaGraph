from pathlib import Path

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.ingestion.document_processor import process_document


PDF_PATH = Path("data/raw/siemens_lagebericht.pdf")
COLLECTION_NAME = "siemens_documents"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

model = TextEmbedding(model_name=MODEL_NAME)
client = QdrantClient(url="http://localhost:6333")


def index_documents():
    chunks = process_document(str(PDF_PATH))

    points = []

    for index, chunk in enumerate(chunks):
        embedding = list(model.embed([chunk["text"]]))[0]

        points.append(
            PointStruct(
                id=index,
                vector=embedding.tolist(),
                payload=chunk,
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print(f"Total chunks: {len(chunks)}")
    print(f"Successfully indexed {len(points)} points!")


if __name__ == "__main__":
    index_documents()