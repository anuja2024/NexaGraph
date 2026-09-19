import os

from dotenv import load_dotenv


load_dotenv()


APP_NAME = os.getenv(
    "APP_NAME",
    "KnowledgeGraph AI",
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)

QDRANT_HOST = os.getenv(
    "QDRANT_HOST",
    "localhost",
)

QDRANT_PORT = int(
    os.getenv(
        "QDRANT_PORT",
        "6333",
    )
)

NEO4J_URI = os.getenv(
    "NEO4J_URI",
    "bolt://localhost:7687",
)

NEO4J_USERNAME = os.getenv(
    "NEO4J_USERNAME",
    "neo4j",
)

NEO4J_PASSWORD = os.getenv(
    "NEO4J_PASSWORD",
    "knowledgegraph123",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL",
    "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "Qwen/Qwen2.5-0.5B-Instruct",
)