from fastembed import TextEmbedding
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from app.graph.neo4j_client import get_entity_neighbors
from app.ingestion.pipeline import ingest_documents
from app.retrieval.vector_store import search_vectors


EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


embedding_model = TextEmbedding(
    model_name=EMBEDDING_MODEL
)

reranker = CrossEncoder(RERANKER_MODEL)

chunks = ingest_documents()

documents = [
    chunk["text"]
    for chunk in chunks
]

tokenized_documents = [
    document.lower().split()
    for document in documents
]

bm25 = BM25Okapi(tokenized_documents)


def build_metadata_filter(
    document_id=None,
    page=None,
    section=None,
):
    return {
        "document_id": document_id,
        "page": page,
        "section": section,
    }


def matches_filter(chunk, metadata_filter=None):
    if not metadata_filter:
        return True

    for key, value in metadata_filter.items():
        if value is not None and chunk.get(key) != value:
            return False

    return True


def semantic_search(
    query: str,
    top_k: int = 20,
    metadata_filter=None,
):
    query_vector = list(
        embedding_model.embed([query])
    )[0]

    qdrant_filter = None

    if metadata_filter:
        from qdrant_client.models import (
            FieldCondition,
            Filter,
            MatchValue,
        )

        conditions = [
            FieldCondition(
                key=key,
                match=MatchValue(value=value),
            )
            for key, value in metadata_filter.items()
            if value is not None
        ]

        if conditions:
            qdrant_filter = Filter(must=conditions)

    return search_vectors(
        query_vector.tolist(),
        top_k,
        qdrant_filter,
    )


def keyword_search(
    query: str,
    top_k: int = 20,
    metadata_filter=None,
):
    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    filtered_indices = [
        index
        for index, chunk in enumerate(chunks)
        if matches_filter(
            chunk,
            metadata_filter,
        )
    ]

    ranked_indices = sorted(
        filtered_indices,
        key=lambda index: scores[index],
        reverse=True,
    )[:top_k]

    return [
        {
            "score": float(scores[index]),
            "chunk": chunks[index],
        }
        for index in ranked_indices
    ]


def hybrid_search(query, top_k=50, metadata_filter=None):
    document_ids = sorted({
        chunk["document_id"]
        for chunk in chunks
        if chunk.get("document_id")
    })

    rankings = {}

    for document_id in document_ids:

        current_filter = {
            "document_id": document_id
        }

        if metadata_filter:
            current_filter.update(
                {
                    key: value
                    for key, value in metadata_filter.items()
                    if value is not None
                }
            )

        vector_results = semantic_search(
            query,
            top_k=10,
            metadata_filter=current_filter,
        )

        keyword_results = keyword_search(
            query,
            top_k=10,
            metadata_filter=current_filter,
        )

        for rank, result in enumerate(vector_results, start=1):
            chunk = result.payload
            chunk_id = chunk["chunk_id"]

            rankings.setdefault(
                chunk_id,
                {
                    "chunk": chunk,
                    "vector_rank": None,
                    "bm25_rank": None,
                },
            )

            rankings[chunk_id]["vector_rank"] = rank

        for rank, result in enumerate(keyword_results, start=1):
            chunk = result["chunk"]
            chunk_id = chunk["chunk_id"]

            rankings.setdefault(
                chunk_id,
                {
                    "chunk": chunk,
                    "vector_rank": None,
                    "bm25_rank": None,
                },
            )

            rankings[chunk_id]["bm25_rank"] = rank

    rrf_k = 60

    for result in rankings.values():

        vector_rank = result["vector_rank"]
        bm25_rank = result["bm25_rank"]

        vector_score = (
            1 / (rrf_k + vector_rank)
            if vector_rank
            else 0
        )

        bm25_score = (
            1 / (rrf_k + bm25_rank)
            if bm25_rank
            else 0
        )

        result["rrf_score"] = vector_score + bm25_score

    return sorted(
        rankings.values(),
        key=lambda result: result["rrf_score"],
        reverse=True,
    )[:top_k]

def rerank(
    query: str,
    results,
    top_k: int = 10,
):
    pairs = [
        (
            query,
            result["chunk"]["text"],
        )
        for result in results
    ]

    scores = reranker.predict(pairs)

    rerank_scores = [float(score) for score in scores]
    rrf_scores = [
        float(result["rrf_score"])
        for result in results
    ]

    # Min-max normalization
    def normalize(values):
        minimum = min(values)
        maximum = max(values)

        if maximum == minimum:
            return [1.0] * len(values)

        return [
            (value - minimum) / (maximum - minimum)
            for value in values
        ]

    normalized_rerank = normalize(
        rerank_scores
    )

    normalized_rrf = normalize(
        rrf_scores
    )

    reranked = []

    for result, rerank_score, norm_rerank, norm_rrf in zip(
        results,
        rerank_scores,
        normalized_rerank,
        normalized_rrf,
    ):

        combined_score = (
            0.7 * norm_rerank
            + 0.3 * norm_rrf
        )

        reranked.append(
            {
                "chunk": result["chunk"],
                "rrf_score": result["rrf_score"],
                "rerank_score": rerank_score,
                "combined_score": combined_score,
            }
        )

    return sorted(
        reranked,
        key=lambda result: result["combined_score"],
        reverse=True,
    )[:top_k]


def diversify_results(
    results,
    top_k: int = 5,
):
    selected = []
    seen_pages = set()

    for result in results:
        page_key = (
            result["chunk"]["document_id"],
            result["chunk"]["page"],
        )

        if page_key not in seen_pages:
            selected.append(result)
            seen_pages.add(page_key)

        if len(selected) == top_k:
            break

    return selected


def retrieve(query, top_k=5, metadata_filter=None):
    candidates = hybrid_search(
        query,
        top_k=50,
        metadata_filter=metadata_filter,
    )

    reranked = rerank(
        query,
        candidates,
        top_k=20,
    )

    return reranked[:top_k]

def graph_expand(results, top_k=10):
    expanded = []

    seen_entities = set()

    from app.graph.entity_extractor import extract_entities

    for result in results:
        chunk = result["chunk"]

        entities = extract_entities(
            chunk["text"]
        )

        for entity in entities:
            entity_name = entity["text"]

            if entity_name in seen_entities:
                continue

            seen_entities.add(entity_name)

            neighbors = get_entity_neighbors(
                entity_name,
                top_k=top_k,
            )

            for neighbor in neighbors:
                expanded.append(
                    {
                        "source_entity": entity_name,
                        "entity": neighbor["entity"],
                        "type": neighbor["type"],
                        "source_chunk_ids": neighbor[
                            "source_chunk_ids"
                        ],
                    }
                )

    return expanded

def graph_rag_retrieve(
    query: str,
    top_k: int = 5,
):
    retrieved = retrieve(
        query,
        top_k=top_k,
    )

    graph_results = graph_expand(
        retrieved,
        top_k=10,
    )

    return {
        "retrieved_chunks": retrieved,
        "graph_results": graph_results,
    }

def build_graph_context(result):
    context = []

    context.append("DIRECT EVIDENCE")

    retrieved_chunk_ids = set()

    for item in result["retrieved_chunks"][:3]:
        chunk = item["chunk"]

        retrieved_chunk_ids.add(
            chunk["chunk_id"]
        )

        context.append(
            f"[Document: {chunk['document_id']} | "
            f"Page: {chunk['page']} | "
            f"Chunk: {chunk['chunk_id']}]"
        )

        context.append(chunk["text"])
        context.append("")

    context.append("GRAPH EVIDENCE")

    seen_relationships = set()
    graph_count = 0

    for item in result["graph_results"]:
        source_chunks = set(
            item["source_chunk_ids"]
        )

        if not (
            source_chunks
            & retrieved_chunk_ids
        ):
            continue

        relationship = (
            item["source_entity"],
            item["entity"],
            item["type"],
        )

        if relationship in seen_relationships:
            continue

        if graph_count >= 5:
           break

        seen_relationships.add(relationship)

        matching_chunks = [
            chunk_id
            for chunk_id in item["source_chunk_ids"]
            if chunk_id in retrieved_chunk_ids
        ]

        context.append(
            f"{item['source_entity']} "
            f"-> {item['entity']} "
            f"({item['type']})"
        )

        context.append(
            "Source chunks: "
            + ", ".join(matching_chunks)
        )
        graph_count += 1

    return "\n".join(context)

if __name__ == "__main__":

    evaluation_queries = [
        {
            "query": "What are Siemens sustainability targets for employees?",
            "expected_page": None,
            "expected_document": "siemens_sustainability_2025",
        },
    ]

    for item in evaluation_queries:

        query = item["query"]

        expected_page = item["expected_page"]

        expected_document = item[
            "expected_document"
        ]

        results = retrieve(
            query,
            top_k=5,
        )

        print("\n" + "=" * 80)
        print(f"Query: {query}")
        print(
            f"Expected: "
            f"{expected_document}, "
            f"page {expected_page}"
        )
        print("=" * 80)

        for rank, result in enumerate(
            results,
            start=1,
        ):
            chunk = result["chunk"]

            print(
                f"\nRank {rank}"
            )

            print(
                f"Document: "
                f"{chunk['document_id']}"
            )

            print(
                f"Page: "
                f"{chunk['page']}"
            )

            print(
                f"Chunk ID: "
                f"{chunk['chunk_id']}"
            )

            print(
                f"RRF Score: "
                f"{result['rrf_score']:.4f}"
            )

            print(
                f"Rerank Score: "
                f"{result['rerank_score']:.4f}"
            )
            print(
                f"Combined Score: "
                f"{result['combined_score']:.4f}"
            )

            print(
                f"Text: "
                f"{chunk['text'][:500]}"
            )

    result = graph_rag_retrieve(
        "What sustainability targets does Siemens have for employees?",
        top_k=3,
    )

    print("\nGRAPH RESULTS")

    for item in result["graph_results"][:10]:
        print(item)

    print("\n" + "=" * 80)
    print("GRAPH-RAG CONTEXT")
    print("=" * 80)

    context = build_graph_context(result)

    print(context[:5000])