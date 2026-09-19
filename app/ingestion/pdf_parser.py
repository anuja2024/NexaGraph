import re
import pymupdf


def clean_text(text: str):
    """
    Clean common PDF text extraction problems.
    """

    # Replace multiple spaces/tabs with one space
    text = re.sub(r"[ \t]+", " ", text)

    # Fix common missing spaces between words.
    # Example:
    # Forschungund Entwicklung
    # -> Forschung und Entwicklung
    text = re.sub(
        r"([a-zäöüß])([A-ZÄÖÜ])",
        r"\1 \2",
        text
    )

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_text_from_pdf(pdf_path: str):
    """
    Extract and clean text from a PDF page by page.
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        text = clean_text(text)

        pages.append({
            "page": page_number,
            "text": text
        })

    document.close()

    return pages


if __name__ == "__main__":

    pdf_path = "data/raw/siemens_lagebericht.pdf"

    pages = extract_text_from_pdf(pdf_path)

    print(f"Number of pages: {len(pages)}")

    for page in pages[:5]:

        print("\n" + "=" * 60)
        print(f"PAGE {page['page']}")
        print("=" * 60)

        print(page["text"][:1500])