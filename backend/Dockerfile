FROM python:3.11-slim

WORKDIR /app

COPY ../poetry.lock ../pyproject.toml ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

COPY backend/ ./backend/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
