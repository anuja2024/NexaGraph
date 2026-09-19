# NexaGraph — Enterprise GraphRAG Knowledge Intelligence Platform

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-312/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A local-first **GraphRAG (Graph Retrieval-Augmented Generation)** platform for querying enterprise documents using hybrid information retrieval, vector databases, knowledge graphs, cross-encoder reranking, and a local Large Language Model (LLM).

The project demonstrates an end-to-end pipeline from document ingestion to grounded question answering with source-level citations.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Dataset](#dataset)
- [Evaluation](#evaluation)
- [Key Concepts](#key-concepts-demonstrated)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Project Status](#project-status)
- [Author](#author)

---

## 🎯 Overview

Enterprise documents often contain information distributed across multiple reports, sections, tables, and pages. A simple keyword search or vector search may retrieve relevant text but can miss relationships between entities and documents.

**NexaGraph** combines multiple retrieval strategies to deliver grounded, source-cited answers:

- **Semantic vector search** → Qdrant
- **BM25 keyword search** → Lexical retrieval
- **Knowledge-graph retrieval** → Neo4j relationships
- **Reciprocal Rank Fusion** → Hybrid combination
- **Cross-encoder reranking** → Relevance optimization
- **Local LLM generation** → Grounded answers

---

## 🏗️ Architecture

### Information Retrieval Pipeline

```
                    Enterprise Documents
                            |
                            v
                 PDF Parsing & Processing
                            |
                            v
                   Section Detection
                            |
                            v
                       Chunking
                            |
              +-------------+-------------+
              |                           |
              v                           v
       Vector Embeddings             Entity Extraction
              |                           |
              v                           v
           Qdrant                      Neo4j
       Vector Database             Knowledge Graph
              |                           |
              +-------------+-------------+
                            |
                            v
                    Hybrid Retrieval
                            |
                            v
                  Reciprocal Rank Fusion
                            |
                            v
                   Cross-Encoder
                     Reranking
                            |
                            v
                      Top Evidence
                            |
                            v
                     Local Qwen LLM
                            |
                            v
                 Grounded Final Answer
                            |
                            v
                 Answer + Source Citations
```

### Document Ingestion Pipeline

```
PDF
 |
 v
Text Extraction
 |
 v
Section Detection
 |
 v
Chunking
 |
 v
Metadata Creation
 |
 +----------------------+
 |                      |
 v                      v
Vector Index         Graph Index
```

### Question-Answering Process

```
User Question
      |
      v
Query Processing
      |
      +------------------+
      |                  |
      v                  v
   BM25              Vector Search
      |                  |
      +--------+---------+
               |
               v
        Hybrid Retrieval
               |
               v
       Graph-based Context
               |
               v
        RRF Combination
               |
               v
        Cross-Encoder
          Reranking
               |
               v
        Top Evidence
               |
               v
          Local LLM
               |
               v
      Grounded Answer
               |
               v
       Source Citations
```

---

## ✨ Key Features

### Document Processing
- PDF text extraction and parsing
- Automatic section detection
- Intelligent chunking (1,678 chunks from 5 documents)
- Metadata preservation (document ID, page number, section)

### Semantic Search
- Multilingual embeddings: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Vector database: Qdrant (384-dimensional embeddings)
- Handles semantic similarity beyond keyword matching

### Keyword Retrieval
- BM25Okapi for lexical retrieval
- Preserves exact terminology, names, and numbers
- Complements semantic search

### Knowledge Graph
- Entity extraction and relationship mapping
- Neo4j graph database
- Captures relationships between concepts

### Hybrid Retrieval
- **Reciprocal Rank Fusion** combines BM25, vector, and graph results
- Higher-ranked candidates across methods receive boost
- Formula: `RRF(d) = Σ 1 / (k + rank(d))`

### Reranking
- Cross-encoder: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
- Reranks candidates for relevance
- Reduces impact of initially retrieved but less relevant chunks

### Grounded Generation
- Local LLM: `Qwen/Qwen2.5-0.5B-Instruct`
- Uses only retrieved evidence
- Avoids hallucinations
- Preserves exact numbers and units
- Returns source-level citations

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.12 |
| **Backend** | FastAPI |
| **Frontend** | React + Vite |
| **Vector Database** | Qdrant |
| **Knowledge Graph** | Neo4j |
| **Embeddings** | FastEmbed / Sentence Transformers |
| **Keyword Retrieval** | BM25Okapi |
| **Reranking** | Cross-Encoder |
| **LLM** | Qwen 2.5 |
| **Containerization** | Docker |
| **Testing** | pytest |
| **Version Control** | Git / GitHub |

---

## 📁 Project Structure

```
NexaGraph/
|
+-- app/
|   |
|   +-- evaluation/
|   |   +-- evaluate_retrieval.py
|   |   +-- evaluation_dataset.py
|   |
|   +-- graph/
|   |   +-- entity_extractor.py
|   |   +-- neo4j_client.py
|   |
|   +-- ingestion/
|   |   +-- chunker.py
|   |   +-- document_processor.py
|   |   +-- pdf_parser.py
|   |   +-- pipeline.py
|   |   +-- section_detector.py
|   |
|   +-- llm/
|   |   +-- local_llm.py
|   |
|   +-- retrieval/
|   |   +-- bm25_search.py
|   |   +-- embedding_pipeline.py
|   |   +-- embeddings.py
|   |   +-- index_documents.py
|   |   +-- retriever.py
|   |   +-- vector_search.py
|   |   +-- vector_store.py
|   |
|   +-- config.py
|   +-- main.py
|
+-- data/
|   +-- raw/
|   +-- processed/
|
+-- docker/
|   +-- docker-compose.yml
|
+-- frontend/
|   +-- src/
|   +-- public/
|   +-- package.json
|
+-- tests/
|   +-- test_api.py
|
+-- requirements.txt
+-- pytest.ini
+-- .gitignore
+-- README.md
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.12+**
- **Docker & Docker Compose** (for database services)
- **Node.js & npm** (for frontend)

### Clone Repository

```bash
git clone https://github.com/anuja2024/NexaGraph.git
cd NexaGraph
```

### Create Virtual Environment

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate     # Linux/macOS
```

### Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application
APP_NAME=NexaGraph
APP_VERSION=1.0.0

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Neo4j Knowledge Graph
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Models
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
RERANKER_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
LLM_MODEL=Qwen/Qwen2.5-0.5B-Instruct
```

⚠️ **Never commit credentials or `.env` files to GitHub.**

### Docker Services

Start the database services:

```bash
docker-compose -f docker/docker-compose.yml up -d
```

**Services:**

| Service | Port | Purpose |
|---------|------|---------|
| Qdrant | 6333 | Vector storage and similarity search |
| Neo4j | 7474 | Graph database UI |
| Neo4j Bolt | 7687 | Application connection |

---

## 📖 Usage

### 1. Document Ingestion

Place source PDFs in `data/raw/` and run:

```bash
python -m app.ingestion.pipeline
```

The pipeline will:
- Extract text from PDFs
- Detect sections
- Create chunks
- Generate embeddings
- Index in Qdrant

### 2. Build Knowledge Graph

```bash
python -m app.graph.neo4j_client
```

This indexes document chunks and extracted entities in Neo4j.

### 3. Run Backend Server

```bash
uvicorn app.main:app --reload
```

Backend runs on: `http://127.0.0.1:8000`

API docs: `http://127.0.0.1:8000/docs`

### 4. Run Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs through Vite development server.

---

## 🔌 API Documentation

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### Query Endpoint

```bash
POST /query
```

**Request:**
```json
{
  "question": "Wie viele Mitarbeiter hatte Siemens zum 30. September 2025?"
}
```

**Response:**
```json
{
  "question": "Wie viele Mitarbeiter hatte Siemens zum 30. September 2025?",
  "answer": {
    "answer": "318.000",
    "citations": [
      {
        "document": "siemens_lagebericht_2025",
        "page": 5
      }
    ]
  }
}
```

**Interactive API Docs:** `http://127.0.0.1:8000/docs`

---

## 📊 Dataset

The demonstration corpus consists of **5 Siemens 2025 reports**:

- `siemens_lagebericht_2025.pdf`
- `siemens_konzernabschluss_2025.pdf`
- `siemens_nachhaltigkeitsbericht_2025.pdf`
- `siemens_verguetungsbericht_2025.pdf`
- `siemens_aufsichtsrat_2025.pdf`

### Corpus Statistics

| Metric | Value |
|--------|-------|
| Documents | 5 |
| Total Chunks | 1,678 |
| Embedding Dimension | 384 |

### Example Questions

**German:**
- Wie hoch waren die Umsatzerlöse von Siemens im Geschäftsjahr 2025?
- Wie viele Mitarbeiter hatte Siemens zum 30. September 2025?
- Welche Nachhaltigkeitsbereiche werden im Bericht genannt?

**English:**
- What was Siemens' revenue in fiscal year 2025?
- What ROCE target is mentioned in the report?

---

## 📈 Evaluation

Retrieval quality is evaluated using a benchmark dataset in `app/evaluation/`.

### Metrics

| Metric | Result |
|--------|--------|
| Document Recall@5 | 100% |
| Page Recall@5 | 20% |
| Mean Reciprocal Rank (MRR) | 0.125 |

### Running Evaluation

```bash
pytest -q
```

**Test Status:** 3 passed

### Notes

The evaluation highlighted an important metadata consideration: reports contain both **physical PDF page numbers** and **printed report page numbers**. The current system uses physical PDF page metadata.

---

## 🎓 Key Concepts Demonstrated

This project demonstrates practical experience with:

- **Retrieval-Augmented Generation (RAG)**
- **GraphRAG Architecture**
- **Hybrid Information Retrieval**
- **Semantic Search & Vector Similarity**
- **BM25 Keyword Retrieval**
- **Vector Databases (Qdrant)**
- **Knowledge Graphs (Neo4j)**
- **Entity Extraction**
- **Reciprocal Rank Fusion (RRF)**
- **Cross-Encoder Reranking**
- **Local LLM Inference**
- **PDF Processing & Document Understanding**
- **Metadata Management**
- **FastAPI REST APIs**
- **React Frontend Development**
- **Docker Containerization**
- **Automated Testing (pytest)**
- **Retrieval Evaluation & Benchmarking**

---

## ⚠️ Limitations

- Entity extraction can produce noisy entities
- Knowledge graph is based on automatically extracted entities
- Evaluation dataset is relatively small
- Page evaluation uses physical PDF pages (not printed report pages)
- Local LLM is intentionally lightweight
- Optimized for local development, not large-scale production
- No authentication or enterprise access control
- No conversation memory

---

## 🔮 Future Improvements

- [ ] Improved entity normalization
- [ ] Better relationship extraction
- [ ] Separate physical and printed page metadata
- [ ] Larger retrieval evaluation benchmark
- [ ] Advanced graph traversal strategies
- [ ] Query classification
- [ ] Conversation memory
- [ ] Document-level access control
- [ ] Enterprise authentication
- [ ] Production deployment guidelines
- [ ] Monitoring and retrieval analytics
- [ ] Larger local LLMs
- [ ] Multilingual query expansion

---

## ✅ Project Status

| Component | Status |
|-----------|--------|
| Document ingestion | ✓ |
| PDF processing | ✓ |
| Chunking | ✓ |
| Vector indexing | ✓ |
| BM25 retrieval | ✓ |
| Neo4j graph | ✓ |
| Hybrid retrieval | ✓ |
| RRF ranking | ✓ |
| Cross-encoder reranking | ✓ |
| Local LLM generation | ✓ |
| FastAPI backend | ✓ |
| React frontend | ✓ |
| Source citations | ✓ |
| Retrieval evaluation | ✓ |
| Automated tests | ✓ |

---

## 👤 Author

**Anuja Patade**

GitHub: [@anuja2024](https://github.com/anuja2024/NexaGraph)

---

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## 🙌 Acknowledgments

Special thanks to the open-source communities behind:
- FastAPI
- React
- Qdrant
- Neo4j
- Sentence Transformers
- Cross-Encoder
- Qwen LLM

-
