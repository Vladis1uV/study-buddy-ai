"""
API Routes - handles HTTP requests and delegates to services.
"""

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.exceptions import FileTooLargeError
from backend.service.document_service import DocumentService
from backend.service.qa_service import QAService

router = APIRouter()

document_service = DocumentService()
qa_service = QAService()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


class AskRequest(BaseModel):
    document_id: str = Field(min_length=1)
    question: str = Field(min_length=1)


class AskResponse(BaseModel):
    answer: str
    sources: list[str] = []


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for RAG processing."""
    if not file.filename:
        logging.warning("Attempting to upload file without a name.")
        raise HTTPException(status_code=400, detail="No filename provided")

    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        raise FileTooLargeError(f"{file.filename} is {file.size} bytes (max {MAX_UPLOAD_BYTES})")

    content = await file.read()
    document_id = document_service.process_document(file.filename, content)

    return {"document_id": document_id, "filename": file.filename}


@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    """Ask a question about a previously uploaded document."""

    answer, sources = qa_service.ask(req.document_id, req.question)

    logging.info(f"Question asked: {req.question} | Answer: {answer} | Sources: {sources}")
    return AskResponse(answer=answer, sources=sources)
