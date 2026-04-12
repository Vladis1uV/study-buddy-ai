"""
Study Assistant Backend - Entry Point
Run: uvicorn main:app --reload --port 8000
"""

import logging

logging.basicConfig(level=logging.INFO, force=True, format="%(asctime)s - %(levelname)s - %(message)s")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router

app = FastAPI(
    title="Study Assistant API",
    description="RAG-powered lecture Q&A backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
