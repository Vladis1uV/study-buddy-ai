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
│   ├── pages/                # Page components
│   └── test/setup.ts         # Vitest setup
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
│   ├── main.py               # FastAPI entry point
│   └── Dockerfile            # Backend image (python + ONNX model baked in)
├── frontend.Dockerfile       # Frontend image (Vite build → nginx)
├── .github/workflows/        # CI/CD pipeline
└── docker-compose.yaml
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (frontend only)
- A RunPod account with an API key (for LLM answers)

### Run with Docker (full stack, one terminal)

```bash
# Copy the env template and fill in your RunPod credentials
cp backend/.env.example backend/.env

# Build and start both services (backend + frontend)
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Stop with `Ctrl+C`, or run detached with `docker compose up -d` and stop via `docker compose down`.

On first run, the backend image downloads the ONNX embedding model from HuggingFace
(baked into the image, no runtime download) and the frontend image builds the Vite
bundle and serves it via nginx.

### Run locally for development (two terminals)

Use this when you want hot-reload on frontend and/or backend.

Terminal 1 — backend with auto-reload:

```bash
poetry install
poetry run uvicorn backend.main:app --reload --port 8000
```

Terminal 2 — frontend dev server (Vite HMR):

```bash
npm install
npm run dev
```

The Vite dev server runs at `http://localhost:8080` (see `vite.config.ts`).
Both `:5173` and `:8080` are pre-allowed by the backend's CORS config, so either works.

A hybrid option: run the backend in Docker and the frontend locally — useful when you
only care about frontend iteration speed.

```bash
docker compose up backend -d     # backend container in background
npm run dev                      # foreground Vite with HMR
```

### Run tests locally

Backend (pytest + ruff):

```bash
poetry install --with dev
poetry run pytest
poetry run ruff check backend/
```

Frontend (vitest + React Testing Library, jsdom environment):

```bash
npm install            # one-time
npm test               # single run (vitest run)
npm run test:watch     # watch mode
npm run lint           # eslint
npm run build          # type-check + production build
```

Test files live next to components as `*.test.tsx` and are picked up by
`vitest.config.ts` (`src/**/*.{test,spec}.{ts,tsx}`). Shared setup —
`@testing-library/jest-dom` matchers, etc. — lives in `src/test/setup.ts`.

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
