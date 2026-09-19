from pathlib import Path

from app.ingestion.document_processor import process_document
from fastembed import TextEmbedding

from app.retrieval.vector_store import (
    index_chunks,
    recreate_collection,
)

RAW_DATA_DIR = Path("data/raw")

EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

embedding_model = TextEmbedding(
    model_name=EMBEDDING_MODEL
)


def generate_document_id(pdf_path: Path):
    return pdf_path.stem


def ingest_documents():
    pdf_files = sorted(RAW_DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {RAW_DATA_DIR}"
        )

    all_chunks = []

    for pdf_path in pdf_files:
        document_id = generate_document_id(pdf_path)

        print(f"Processing: {pdf_path.name}")
        print(f"Document ID: {document_id}")

        chunks = process_document(
            str(pdf_path),
            document_id,
        )

        all_chunks.extend(chunks)

        print(f"Chunks: {len(chunks)}")

    return all_chunks


if __name__ == "__main__":
    chunks = ingest_documents()

    recreate_collection()
    index_chunks(chunks, embedding_model)

    print("\n" + "=" * 70)
    print(f"Documents: {len(list(RAW_DATA_DIR.glob('*.pdf')))}")
    print(f"Total chunks: {len(chunks)}")
    print("Qdrant indexing completed.")
    print("=" * 70)