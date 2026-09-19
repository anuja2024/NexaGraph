# NexaGraph

### Enterprise GraphRAG Knowledge Intelligence Platform

NexaGraph is a local-first enterprise document intelligence platform that combines **hybrid retrieval, knowledge graphs, neural reranking, and a local LLM** to generate grounded answers from business documents.

The system combines traditional information retrieval, semantic search, graph-based context, and generative AI into an end-to-end **GraphRAG pipeline**.

---

## 🚀 Features

- 🔎 **Hybrid Retrieval**
  - Dense vector search with Qdrant
  - BM25 keyword retrieval
  - Reciprocal Rank Fusion (RRF)

- 🧠 **Neural Reranking**
  - Cross-encoder based relevance scoring

- 🕸️ **Knowledge Graph**
  - Entity extraction
  - Entity relationships
  - Neo4j graph storage

- 🤖 **Local LLM**
  - Qwen2.5-0.5B-Instruct
  - No paid LLM API dependency

- 📚 **Grounded Question Answering**
  - Evidence-based generation
  - Strict context-only prompting
  - Source references

- 🇩🇪 **Multilingual Retrieval**
  - Multilingual sentence embeddings
  - Designed for German enterprise documents

- ⚡ **FastAPI Backend**
  - REST API
  - Swagger/OpenAPI documentation

- 💻 **React Frontend**
  - React + Vite
  - Interactive enterprise-style interface

- 🧪 **Automated Testing**
  - pytest
  - FastAPI TestClient

---

## 🏗️ Architecture

```text
                         Enterprise Documents
                                  │
                                  ▼
                           PDF Ingestion
                                  │
                                  ▼
                     Text Extraction & Chunking
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
              Vector Search                 BM25 Search
                 Qdrant                    Keyword Retrieval
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                         Hybrid Retrieval
                                  │
                                  ▼
                         RRF Result Fusion
                                  │
                                  ▼
                       Cross-Encoder Reranking
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
               Neo4j Graph                 Retrieved Evidence
                 Context                         │
                    │                            │
                    └─────────────┬──────────────┘
                                  ▼
                             Local LLM
                         Qwen2.5-0.5B-Instruct
                                  │
                                  ▼
                         Grounded Answer
                                  │
                                  ▼
                         Sources & Citations
🛠️ Tech Stack
Layer	Technologies
Language	Python 3.12
Backend	FastAPI, Pydantic, Uvicorn
Vector Database	Qdrant
Embeddings	FastEmbed, Sentence Transformers
Keyword Search	BM25
Retrieval	Hybrid Search, RRF
Reranking	Cross-Encoder
Knowledge Graph	Neo4j, Cypher
LLM	Qwen2.5-0.5B-Instruct
LLM Framework	Hugging Face Transformers
Frontend	React, Vite, JavaScript
Infrastructure	Docker
Testing	pytest
Version Control	Git, GitHub
📊 Dataset

The current NexaGraph corpus consists of five official Siemens 2025 reports:

Siemens 2025 Management Report
Siemens 2025 Consolidated Financial Statements
Siemens 2025 Sustainability Report
Siemens 2025 Compensation Report
Siemens 2025 Supervisory Board Report
Corpus Statistics
Metric	Value
Documents	5
Text chunks	1,678
Vector Database	Qdrant
Knowledge Graph	Neo4j

The source PDFs are intentionally kept outside the public Git repository.

🔍 Retrieval Pipeline
1. Document Ingestion

PDF documents are parsed, processed, chunked, and enriched with metadata.

2. Vector Retrieval

Chunks are converted into multilingual embeddings using:

sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

Embeddings are indexed in Qdrant.

3. BM25 Retrieval

BM25 provides lexical retrieval for:

Exact terminology
Names
Dates
Financial values
German business terminology
4. Hybrid Fusion

Vector and BM25 results are combined using Reciprocal Rank Fusion (RRF).

5. Cross-Encoder Reranking

Candidate chunks are reranked using:

cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
6. Knowledge Graph

Extracted entities and relationships are stored in Neo4j and used as graph-based context.

7. Local Generation

The final evidence is passed to:

Qwen/Qwen2.5-0.5B-Instruct

The model generates the answer using the retrieved evidence.

🎯 Grounded Generation

NexaGraph uses strict evidence-based prompting.

The generation layer is instructed to:

Use only retrieved evidence
Avoid outside knowledge
Avoid inventing information
Preserve numerical values and units
Distinguish absolute values from percentages
Distinguish total values from segment values
Avoid substituting related metrics
Explicitly state when the requested information is not available in the evidence

This is particularly important when working with financial and operational documents.

💬 Example Queries
Wie viele Mitarbeiter hatte Siemens zum 30. September 2025?
Wie hoch waren die Umsatzerlöse von Siemens im Geschäftsjahr 2025?
Wie viele Ausschüsse hatte der Aufsichtsrat im Geschäftsjahr 2025?
Wie hoch war der Gewinn nach Steuern?
Wie viele Sitzungen hielt der Aufsichtsrat im Geschäftsjahr 2025 ab?

Example response:

Question:
Wie viele Mitarbeiter hatte Siemens zum 30. September 2025?

Answer:
318.000

Source:
siemens_lagebericht_2025
Page 5
🖥️ Application
Backend

FastAPI provides the REST API.

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
Frontend

The React/Vite interface allows users to:

Ask natural-language questions
View grounded answers
Inspect retrieved sources
View citation information
Use example queries
📁 Project Structure
knowledgegraph-ai/
│
├── app/
│   ├── config.py
│   ├── main.py
│   │
│   ├── evaluation/
│   │   ├── evaluation_dataset.py
│   │   └── evaluate_retrieval.py
│   │
│   ├── graph/
│   │   ├── entity_extractor.py
│   │   └── neo4j_client.py
│   │
│   ├── ingestion/
│   │   ├── chunker.py
│   │   ├── document_processor.py
│   │   ├── pdf_parser.py
│   │   ├── pipeline.py
│   │   └── section_detector.py
│   │
│   ├── llm/
│   │   └── local_llm.py
│   │
│   └── retrieval/
│       ├── bm25_search.py
│       ├── embedding_pipeline.py
│       ├── embeddings.py
│       ├── index_documents.py
│       ├── retriever.py
│       ├── vector_search.py
│       └── vector_store.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docker/
│   └── docker-compose.yml
│
├── frontend/
│   ├── public/
│   └── src/
│
├── tests/
│   └── test_api.py
│
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
⚙️ Installation
Clone
git clone https://github.com/anuja2024/NexaGraph.git
cd NexaGraph
Create Virtual Environment
python -m venv .venv

Activate:

.venv\Scripts\Activate.ps1
Install Dependencies
pip install -r requirements.txt
🐳 Infrastructure

NexaGraph uses Docker for:

Qdrant
Neo4j

Start the services:

docker compose -f docker/docker-compose.yml up -d

Check running containers:

docker ps
📥 Document Ingestion

Place the supported documents inside:

data/raw/

Run the ingestion pipeline:

python -m app.ingestion.pipeline

Build the Neo4j knowledge graph:

python -m app.graph.neo4j_client
🚀 Run the Backend
uvicorn app.main:app --reload

API:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
🎨 Run the Frontend

Open another terminal:

cd frontend
npm install
npm run dev

Open the Vite development URL displayed in the terminal.

🧪 Testing

Run:

pytest -q

Current API tests cover:

Home endpoint
Health endpoint
Query validation
📈 Retrieval Evaluation

NexaGraph includes a retrieval evaluation framework using metrics such as:

Document Recall@5
Page Recall@5
Mean Reciprocal Rank (MRR)

The evaluation framework provides a basis for measuring retrieval quality systematically.

🔐 Local-First Architecture

NexaGraph is designed to keep the core AI pipeline local.

Documents
    ↓
Local Processing
    ↓
Qdrant + Neo4j
    ↓
Hybrid Retrieval
    ↓
Local Reranker
    ↓
Local LLM
    ↓
Grounded Answer

The core question-answering pipeline does not require a paid external LLM API.

🚧 Future Improvements
Advanced answer-quality evaluation
Citation faithfulness evaluation
Entity normalization and deduplication
Improved graph traversal
PostgreSQL integration
Agentic retrieval workflows
Document-level authorization
Authentication and role-based access control
Audit logging
Production deployment
Observability and tracing
Larger local language models
📌 Project Status
Implemented
 PDF ingestion
 Text extraction and chunking
 Metadata processing
 Vector indexing
 BM25 retrieval
 Hybrid retrieval
 Reciprocal Rank Fusion
 Cross-encoder reranking
 Neo4j knowledge graph
 Entity extraction
 Local LLM generation
 Evidence-grounded prompting
 FastAPI backend
 React frontend
 API tests
 Retrieval evaluation framework
Planned
 Advanced graph reasoning
 PostgreSQL
 Agentic workflows
 Enterprise authentication
 Fine-grained authorization
 Production deployment
 Advanced observability
🧠 What NexaGraph Demonstrates

NexaGraph brings together:

Data Engineering
       +
Information Retrieval
       +
Machine Learning
       +
Knowledge Graphs
       +
Generative AI
       +
Backend Engineering
       +
Frontend Engineering

The project demonstrates an end-to-end approach to building a local enterprise GraphRAG system capable of retrieving, reranking, grounding, and presenting information from complex business documents.

📄 License

This project is intended for educational, portfolio, and demonstration purposes.


### After replacing `README.md`

Since you've **already pushed the previous README**, run:

```powershell
git add README.md
git commit -m "Improve GitHub README"
git push
