"""
Study Assistant Backend - Entry Point
Run: uvicorn main:app --reload --port 8000
"""

import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(level=logging.INFO, force=True, format="%(asctime)s - %(levelname)s - %(message)s")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import router as api_router
from backend.exceptions import StudyBuddyError

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Study Assistant API",
    description="RAG-powered lecture Q&A backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(StudyBuddyError)
async def handle_app_error(request: Request, exc: StudyBuddyError) -> JSONResponse:
    logger.error("%s: %s", exc.__class__.__name__, exc, exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.public_message, "error_type": exc.__class__.__name__},
    )


app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
