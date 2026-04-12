FROM python:3.11-slim AS builder

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# ---------- model download ----------
# huggingface_hub is pulled in by transformers, so huggingface-cli is already available
RUN huggingface-cli download onnx-models/all-MiniLM-L6-v2-onnx \
    --local-dir /model \
    --include "*.onnx" "*.json" "vocab.txt"

# ---------- runtime ----------
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy model (baked into image, no runtime download needed)
COPY --from=builder /model ./backend/model/all-MiniLM-L6-v2-onnx

# Copy application code (backend/model/ is excluded via .dockerignore)
COPY backend/ ./backend/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
