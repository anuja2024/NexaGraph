
import re


def normalize_text(text: str):
    """
    Normalize spaces while preserving paragraph boundaries.
    """

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return " ".join(lines)


def split_long_text(text, chunk_size):
    """
    Split long text without breaking words.
    """

    words = text.split()

    chunks = []

    current = ""

    for word in words:

        if len(current) + len(word) + 1 <= chunk_size:

            if current:
                current += " "

            current += word

        else:

            if current:
                chunks.append(current)

            current = word

    if current:
        chunks.append(current)

    return chunks


def get_overlap(chunk, overlap):
    """
    Return the last words up to approximately
    overlap characters.
    """

    words = chunk.split()

    result = []

    length = 0

    for word in reversed(words):

        length += len(word) + 1

        if length > overlap:
            break

        result.insert(0, word)

    return " ".join(result)


def chunk_text(text, chunk_size=900, overlap=150):
    """
    Production-style word-safe chunking.
    """

    text = normalize_text(text)

    if len(text) <= chunk_size:
        return [text]

    base_chunks = split_long_text(text, chunk_size)

    final_chunks = []

    previous = None

    for chunk in base_chunks:

        if previous is None:
            final_chunks.append(chunk)

        else:

            overlap_text = get_overlap(previous, overlap)

            combined = overlap_text + " " + chunk

            final_chunks.append(combined.strip())

        previous = chunk

    return final_chunks