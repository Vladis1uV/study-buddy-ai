"""
API Routes - handles HTTP requests and delegates to services.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from service.document_service import DocumentService
from service.qa_service import QAService

router = APIRouter()

document_service = DocumentService()
qa_service = QAService()


class AskRequest(BaseModel):
    document_id: str
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str] = []


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for RAG processing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    document_id = document_service.process_document(file.filename, content)

    return {"document_id": document_id, "filename": file.filename}


@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    """Ask a question about a previously uploaded document."""
    answer, sources = qa_service.ask(req.document_id, req.question)
    return AskResponse(answer=answer, sources=sources)
