from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.llm.local_llm import answer_question


app = FastAPI(
    title="NexaGraph",
    description="Enterprise GraphRAG Knowledge Intelligence Platform",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "NexaGraph is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/query")
def query(request: QueryRequest):
    result = answer_question(request.question)

    return {
        "question": request.question,
        "answer": result,
    }