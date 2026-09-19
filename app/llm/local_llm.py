from transformers import pipeline
from app.retrieval.retriever import keyword_search

from app.retrieval.retriever import (
    graph_rag_retrieve,
    build_graph_context,
)


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


generator = pipeline(
    "text-generation",
    model=MODEL_NAME,
)

def generate_answer(context: str, question: str):
    system_prompt = """
You are a strict enterprise document question-answering system.

Use ONLY the evidence provided by the user.
Never use outside knowledge.
Never invent, infer, or substitute information.

IMPORTANT RULES:

1. First identify exactly what the question asks for.

2. If the question asks for a number, amount, percentage, date,
   target, metric, or other specific value:
   - Return ONLY a value explicitly supported by the evidence.
   - Do NOT substitute a related value.
   - Do NOT use a growth rate when the question asks for an
     absolute amount.
   - Do NOT use a segment value when the question asks for a total.
   - Do NOT use an order-entry value when the question asks for
     revenue.
   - Do NOT use a percentage when the question asks for an amount.

3. If the exact requested information is NOT present in the evidence,
   say exactly:

   "Die bereitgestellten Quellen enthalten nicht die angeforderte Information."

4. If the evidence contains a list:
   - Include ONLY items explicitly present in the evidence.
   - Never invent additional list items.
   - Never replace evidence items with similar-sounding concepts.

5. If the question asks "how many", return the exact number
   explicitly stated in the evidence.

6. If the question asks "how much", return the exact amount
   explicitly stated in the evidence.

7. Preserve units exactly when they are available in the evidence,
   such as €, Mio. €, Mrd. €, %, employees, or dates.

8. Do not confuse:
   - revenue with revenue growth
   - total revenue with segment revenue
   - revenue with order intake
   - profit with profit growth
   - employee count with employee growth
   - absolute values with percentages

9. Answer in the same language as the question.

10. Keep the answer concise and factual.

11. Do not create citations.
    Citations are handled separately by the application.

EXAMPLES:

Question:
"Wie hoch waren die Umsatzerlöse?"

Evidence:
"Umsatzerlöse 78.914 Mio. €"

Answer:
"Die Umsatzerlöse betrugen 78.914 Mio. €."

Question:
"Wie hoch waren die Umsatzerlöse?"

Evidence:
"Die Umsatzerlöse stiegen um 5 %."

Answer:
"Die bereitgestellten Quellen enthalten nicht die angeforderte Information."

Question:
"Wie viele Ausschüsse hatte der Aufsichtsrat?"

Evidence:
"Der Aufsichtsrat hatte sechs Ausschüsse."

Answer:
"Der Aufsichtsrat hatte sechs Ausschüsse."

Question:
"Welche Ausschüsse hatte der Aufsichtsrat?"

Evidence:
"Im Berichtsjahr hatte der Aufsichtsrat sechs Ausschüsse.
Das Präsidium, der Nominierungsausschuss und der Prüfungsausschuss..."

Answer:
"Der Aufsichtsrat hatte das Präsidium, den Nominierungsausschuss
und den Prüfungsausschuss."

Return ONLY the answer.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": f"EVIDENCE:\n{context}\n\nQUESTION:\n{question}",
        },
    ]

    result = generator(
        messages,
        max_new_tokens=120,
        do_sample=False,
    )

    generated = result[0]["generated_text"]

    if isinstance(generated, list):
        answer = generated[-1]["content"]
    else:
        answer = generated

    return answer.strip()

def validate_evidence(answer: str, retrieved_chunks):

    validated = []

    answer_words = {
        word.lower().strip(".,:;!?()")
        for word in answer.split()
        if len(word) > 3
    }

    for item in retrieved_chunks:

        chunk = item["chunk"]
        text = chunk["text"].lower()

        matching_words = sum(
            1
            for word in answer_words
            if word in text
        )

        coverage = (
            matching_words / len(answer_words)
            if answer_words
            else 0
        )

        validated.append(
    {
        "chunk": chunk,
        "rerank_score": item.get(
            "rerank_score",
            0.0,
        ),
        "combined_score": item.get(
            "combined_score",
            0.0,
        ),
        "coverage": coverage,
    }
)

    return sorted(
        validated,
        key=lambda item: (
            item["coverage"],
            item["rerank_score"],
        ),
        reverse=True,
    )

def answer_question(question: str):

    result = graph_rag_retrieve(
        question,
        top_k=5,
    )

    # Use only the strongest retrieved evidence
    # for the local LLM.
    top_evidence = result["retrieved_chunks"][:5]

    evidence_context = []

    for item in top_evidence:

        chunk = item["chunk"]

        evidence_context.append(
            f"[Document: {chunk['document_id']} | "
            f"Page: {chunk['page']} | "
            f"Chunk: {chunk['chunk_id']}]"
        )

        evidence_context.append(
            chunk["text"]
        )

        evidence_context.append("")

    context = "\n".join(evidence_context)

    

    answer = generate_answer(
        context,
        question,
    )

    validated = validate_evidence(
        answer,
        top_evidence,
    )

    citations = []

    seen = set()

    for item in validated:

        chunk = item["chunk"]

        if item["coverage"] < 0.10:
            continue

        citation_key = (
            chunk["document_id"],
            chunk["page"],
        )

        if citation_key in seen:
            continue

        seen.add(citation_key)

        citations.append(
            {
                "document": chunk["document_id"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
                "rerank_score": item["rerank_score"],
                "combined_score": item.get("combined_score", 0.0),
                "coverage": item["coverage"],
            }
        )

    return {
        "answer": answer,
        "citations": citations,
    }

if __name__ == "__main__":

    question = (
        "What sustainability targets does Siemens "
        "have for employees?"
    )

    result = answer_question(question)

    print("\n" + "=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result["answer"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    for citation in result["citations"]:
        print(
            f"- {citation['document']} | "
            f"Page {citation['page']} | "
            f"Rerank {citation['rerank_score']:.4f} | "
            f"Combined {citation.get('combined_score', 0.0):.4f} | "
            f"Coverage {citation['coverage']:.2f} | "
            f"{citation['chunk_id']}"
        )