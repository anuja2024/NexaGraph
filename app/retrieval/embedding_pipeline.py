from pathlib import Path

from fastembed import TextEmbedding

from app.ingestion.document_processor import process_document


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PDF_PATH = Path(
    "data/raw/siemens_lagebericht.pdf"
)

MODEL_NAME = "BAAI/bge-small-en-v1.5"


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

model = TextEmbedding(
    model_name=MODEL_NAME
)


# --------------------------------------------------
# Process document
# --------------------------------------------------

chunks = process_document(
    str(PDF_PATH)
)

print(
    f"Total chunks: {len(chunks)}"
)


# --------------------------------------------------
# Generate embeddings
# --------------------------------------------------

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = list(
    model.embed(texts)
)


# --------------------------------------------------
# Add embeddings to chunks
# --------------------------------------------------

for chunk, embedding in zip(
    chunks,
    embeddings
):

    chunk["embedding"] = embedding.tolist()


# --------------------------------------------------
# Verification
# --------------------------------------------------

print(
    f"Total embeddings: {len(embeddings)}"
)

print(
    f"Embedding dimension: {len(embeddings[0])}"
)

print(
    f"First chunk ID: {chunks[0]['chunk_id']}"
)

print(
    f"First chunk embedding length: "
    f"{len(chunks[0]['embedding'])}"
)