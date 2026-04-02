# 📚 Study Assistant

A full-stack, end-to-end MLOps project that lets students upload lecture notes and ask questions answered by a RAG (Retrieval-Augmented Generation) pipeline powered by a self-hosted LLM.

## Tech Stack

| Layer            | Technology                                            |
| ---------------- | ----------------------------------------------------- |
| Frontend         | React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui   |
| Backend          | Python, FastAPI, Uvicorn                              |
| RAG              | sentence-transformers, FAISS, pdfplumber, python-docx |
| LLM Hosting      | RunPod (serverless GPU inference)                     |
| Containerization | Docker, Docker Compose                                |
| MLOps (planned)  | MLflow, Apache Airflow                                |

## Project Structure

```
├── src/                    # React frontend
│   ├── components/         # UI components (FileUpload, Chat, etc.)
│   └── pages/              # Page components
├── backend/
│   ├── api/                # FastAPI route handlers
│   ├── service/            # Business logic orchestration
│   ├── rag/                # RAG pipeline modules
│   │   ├── chunker.py      # Document chunking
│   │   ├── embedder.py     # Text → vector embeddings
│   │   ├── retriever.py    # FAISS similarity search
│   │   └── generator.py    # LLM answer generation (RunPod)
│   ├── models/             # Pydantic schemas
│   ├── utils/              # File parsers (PDF, DOCX, TXT, MD)
│   └── main.py             # FastAPI entry point
├── docker-compose.yaml
└── backend/Dockerfile
```

## Getting Started

### Prerequisites

- Python 3.10–3.11
- Node.js 18+
- Docker & Docker Compose
- RunPod account with API credits

### Backend

```bash
# Copy env file and add your RunPod credentials
cp backend/.env.example backend/.env

# Run with Docker
docker compose up backend
```

### Frontend

```bash
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and expects the backend at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint      | Description                               |
| ------ | ------------- | ----------------------------------------- |
| POST   | `/api/upload` | Upload a document (PDF, TXT, MD, DOCX)    |
| POST   | `/api/ask`    | Ask a question about an uploaded document |

## How It Works

1. **Upload** — User uploads lecture notes via the web UI
2. **Parse** — Backend extracts text from the file (PDF, DOCX, TXT, MD)
3. **Chunk** — Text is split into overlapping segments
4. **Embed** — Each chunk is converted to a vector using sentence-transformers
5. **Index** — Vectors are stored in a FAISS index for fast retrieval
6. **Query** — User asks a question → question is embedded → top-k similar chunks retrieved
7. **Generate** — Retrieved chunks + question are sent to the LLM on RunPod → answer returned

## Roadmap

- [x] React frontend with file upload and chat UI
- [x] FastAPI backend with layered architecture
- [x] RAG pipeline (chunk → embed → retrieve → generate)
- [x] RunPod LLM integration
- [x] Docker containerization
- [ ] MLflow experiment tracking
- [ ] Airflow pipeline orchestration
- [ ] Multi-document support
- [ ] Evaluation metrics (RAGAS, faithfulness, relevance)

## License

MIT
