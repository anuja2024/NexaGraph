from app.evaluation.evaluation_dataset import EVALUATION_DATASET
from app.retrieval.retriever import retrieve


def evaluate_query(item, top_k=5):
    results = retrieve(
        item["query"],
        top_k=top_k,
    )

    expected_document = item["expected_document"]
    expected_page = item["expected_page"]

    documents = [
        result["chunk"]["document_id"]
        for result in results
    ]

    pages = [
        result["chunk"]["page"]
        for result in results
    ]

    document_hit = expected_document in documents

    page_hit = any(
        result["chunk"]["document_id"] == expected_document
        and (
            expected_page is None
            or result["chunk"]["page"] == expected_page
        )
        for result in results
 )

    reciprocal_rank = 0.0

    for rank, result in enumerate(results, start=1):
        chunk = result["chunk"]

        if (
            chunk["document_id"] == expected_document
            and (
                expected_page is None
                or chunk["page"] == expected_page
            )
        ):
            reciprocal_rank = 1 / rank
            break

    return {
        "id": item["id"],
        "document_hit": document_hit,
        "page_hit": page_hit,
        "reciprocal_rank": reciprocal_rank,
        "results": results,
    }


def main():
    evaluations = [
        evaluate_query(item)
        for item in EVALUATION_DATASET
    ]

    document_recall = sum(
        result["document_hit"]
        for result in evaluations
    ) / len(evaluations)

    page_recall = sum(
        result["page_hit"]
        for result in evaluations
    ) / len(evaluations)

    mrr = sum(
        result["reciprocal_rank"]
        for result in evaluations
    ) / len(evaluations)

    print("\n" + "=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)

    print(
        f"Queries          : {len(evaluations)}"
    )

    print(
        f"Document Recall@5: {document_recall:.2%}"
    )

    print(
        f"Page Recall@5    : {page_recall:.2%}"
    )

    print(
        f"MRR              : {mrr:.3f}"
    )

    print("\nQUERY RESULTS")
    print("-" * 70)

    for result in evaluations:
        print(
            f"{result['id']} | "
            f"Document: "
            f"{'PASS' if result['document_hit'] else 'FAIL'} | "
            f"Page: "
            f"{'PASS' if result['page_hit'] else 'FAIL'} | "
            f"RR: {result['reciprocal_rank']:.3f}"
        )


if __name__ == "__main__":
    main()