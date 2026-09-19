from pathlib import Path

from rank_bm25 import BM25Okapi

from app.ingestion.document_processor import process_document


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PDF_PATH = Path(
    "data/raw/siemens_lagebericht.pdf"
)


# --------------------------------------------------
# Load document chunks
# --------------------------------------------------

chunks = process_document(
    str(PDF_PATH)
)

print(
    f"Loaded {len(chunks)} chunks"
)


# --------------------------------------------------
# Prepare documents for BM25
# --------------------------------------------------

documents = [
    chunk["text"]
    for chunk in chunks
]


tokenized_documents = [
    document.lower().split()
    for document in documents
]


# --------------------------------------------------
# Create BM25 index
# --------------------------------------------------

bm25 = BM25Okapi(
    tokenized_documents
)


# --------------------------------------------------
# Search function
# --------------------------------------------------

def search_bm25(
    query: str,
    top_k: int = 5
):

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked_indices = scores.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indices:

        results.append({
            "score": float(scores[index]),
            "chunk": chunks[index]
        })

    return results


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    query = "How many employees does Siemens have?"

    results = search_bm25(
        query,
        top_k=5
    )

    print("\n" + "=" * 70)
    print("BM25 SEARCH RESULTS")
    print("=" * 70)

    print(
        f"\nQuery: {query}"
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        chunk = result["chunk"]

        print("\n" + "-" * 70)

        print(
            f"Rank: {rank}"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Page: {chunk['page']}"
        )

        print(
            f"Chunk ID: {chunk['chunk_id']}"
        )

        print("\nText:")

        print(
            chunk["text"][:500]
        )