from fastembed import TextEmbedding


MODEL_NAME = "BAAI/bge-small-en-v1.5"


model = TextEmbedding(
    model_name=MODEL_NAME
)


def generate_embedding(text: str):
    """
    Generate an embedding for a single text.
    """

    embedding = list(
        model.embed([text])
    )[0]

    return embedding.tolist()