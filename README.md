# Study Buddy AI

A full-stack RAG (Retrieval-Augmented Generation) application that lets students upload lecture notes and get answers grounded in their own material — not generic LLM knowledge.

## Goals

- Build an end-to-end MLOps project covering the full lifecycle: data ingestion, vector search, LLM inference, and containerized deployment
- Keep the stack self-contained and reproducible — the embedding model is baked into the Docker image, no external model servers required
- Serve as a practical foundation for adding experiment tracking (MLflow) and pipeline orchestration (Airflow)

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Backend | Python, FastAPI |
| Embeddings | ONNX Runtime (all-MiniLM-L6-v2) |
| Vector search | FAISS |
| Document parsing | pdfplumber, python-docx |
| LLM inference | RunPod (serverless GPU) |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions, GHCR |

## Project Structure

```
├── src/                      # React frontend
│   ├── components/           # UI components
│   └── pages/                # Page components
├── backend/
│   ├── api/                  # FastAPI route handlers
│   ├── service/              # Business logic orchestration
│   ├── rag/
│   │   ├── chunker.py        # Text splitting
│   │   ├── embedder.py       # ONNX embedding inference
│   │   ├── retriever.py      # FAISS similarity search
│   │   └── generator.py      # RunPod LLM generation
│   ├── utils/                # File parsers (PDF, DOCX, TXT)
│   ├── tests/                # pytest test suite
│   └── main.py               # FastAPI entry point
├── .github/workflows/        # CI/CD pipeline
└── docker-compose.yaml
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (frontend only)
- A RunPod account with an API key (for LLM answers)

### Run with Docker

```bash
# Copy the env template and fill in your RunPod credentials
cp backend/.env.example backend/.env

# Start the backend (embedding model is downloaded automatically at build time)
docker compose up backend
```

The API will be available at `http://localhost:8000`.

### Run the frontend

```bash
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

### Run tests locally

```bash
poetry install --with dev
poetry run pytest
poetry run ruff check backend/
```

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/upload` | Upload a document (PDF, DOCX, TXT, MD) |
| POST | `/api/ask` | Ask a question about an uploaded document |

## How It Works

1. **Upload** — user uploads lecture notes via the web UI
2. **Parse** — backend extracts raw text from the file
3. **Chunk** — text is split into overlapping segments
4. **Embed** — each chunk is converted to a vector using a local ONNX model
5. **Index** — vectors are stored in a FAISS index
6. **Query** — question is embedded and matched against the index
7. **Generate** — top matching chunks are sent to the LLM on RunPod alongside the question
