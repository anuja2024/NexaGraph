# NexaGraph — Enterprise GraphRAG Knowledge Intelligence Platform

Local-first GraphRAG system for querying enterprise documents using hybrid retrieval, knowledge graphs, reranking, and a local LLM.

## Project Overview

NexaGraph combines semantic search, keyword search, knowledge-graph retrieval, and cross-encoder reranking to provide grounded answers from enterprise documents.

```text
Enterprise PDFs
      |
      v
Document Processing & Chunking
      |
      +------------------+
      v                  v
   Qdrant             Neo4j
 Vector Search       Knowledge Graph
      |                  |
      +--------+---------+
               v
        Hybrid Retrieval
               |
               v
       Cross-Encoder Reranker
               |
               v
          Local LLM
               |
               v
      Grounded Answer + Sources
Features
PDF ingestion and section-aware chunking
Multilingual semantic embeddings
BM25 keyword retrieval
Qdrant vector search
Neo4j knowledge graph
Hybrid Reciprocal Rank Fusion (RRF)
Cross-encoder reranking
Local Qwen LLM
Source citations with document and page information
FastAPI backend
React/Vite frontend
Dataset

The current demonstration corpus contains five Siemens 2025 reports:

Management Report
Consolidated Financial Statements
Sustainability Report
Remuneration Report
Supervisory Board Report

Total:

5 documents
1,678 chunks
Example Questions
Wie hoch waren die Umsatzerlöse von Siemens im Geschäftsjahr 2025?

Wie viele Mitarbeiter hatte Siemens zum 30. September 2025?

Welche Nachhaltigkeitsbereiche werden im Bericht genannt?

Answers are generated only from retrieved document evidence.

Tech Stack
Python 3.12
FastAPI
React + Vite
Qdrant
Neo4j
FastEmbed
BM25
Sentence Transformers
Qwen 2.5
Docker
pytest
Project Structure
NexaGraph/
|
+-- app/
|   +-- ingestion/
|   +-- retrieval/
|   +-- graph/
|   +-- llm/
|   +-- evaluation/
|   +-- main.py
|
+-- frontend/
+-- data/
+-- docker/
+-- tests/
+-- requirements.txt
+-- README.md
Installation
git clone https://github.com/anuja2024/NexaGraph.git
cd NexaGraph

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Start Qdrant and Neo4j with Docker, configure .env, then run:

python -m app.ingestion.pipeline
python -m app.graph.neo4j_client
uvicorn app.main:app --reload

Frontend:

cd frontend
npm install
npm run dev
Evaluation

The retrieval pipeline is evaluated using document recall, page recall, and Mean Reciprocal Rank (MRR).

Current evaluation:

Document Recall@5    100%
Page Recall@5         20%
MRR                   0.125
Project Goal

NexaGraph demonstrates an end-to-end local GraphRAG architecture combining document processing, hybrid retrieval, graph-based context, reranking, and grounded generation without relying on paid LLM APIs.
