from pathlib import Path

from app.ingestion.chunker import chunk_text
from app.ingestion.pdf_parser import extract_text_from_pdf
from app.ingestion.section_detector import detect_section


def process_document(pdf_path: str, document_id: str):
    pages = extract_text_from_pdf(pdf_path)

    all_chunks = []
    current_section = "Unknown"

    for page in pages:
        page_number = page["page"]
        text = page["text"]

        detected_section = detect_section(text)

        if detected_section:
            current_section = detected_section

        chunks = chunk_text(
            text,
            chunk_size=900,
            overlap=150,
        )

        for chunk_number, chunk in enumerate(chunks, start=1):
            chunk_data = {
                "document_id": document_id,
                "page": page_number,
                "chunk_id": (
                    f"{document_id}_page_"
                    f"{page_number}_chunk_{chunk_number}"
                ),
                "section": current_section,
                "text": chunk,
            }

            all_chunks.append(chunk_data)

    return all_chunks


if __name__ == "__main__":
    pdf_path = Path("data/raw/siemens_lagebericht.pdf")

    chunks = process_document(
        str(pdf_path),
        "siemens_lagebericht_2025",
    )

    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks[:10]:
        print("\n" + "=" * 70)
        print(f"Document : {chunk['document_id']}")
        print(f"Page     : {chunk['page']}")
        print(f"Chunk ID : {chunk['chunk_id']}")
        print(f"Section  : {chunk['section']}")
        print("=" * 70)
        print(chunk["text"])