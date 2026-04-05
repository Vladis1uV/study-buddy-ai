FROM python:3.11-slim AS builder

WORKDIR /app

COPY ../poetry.lock ../pyproject.toml ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# ---------- runtime ----------
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ ./backend/

# Copy pre-exported ONNX model
COPY backend/model/ ./backend/model/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
