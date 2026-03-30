"""
Pydantic models / schemas for the application.
"""

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    chunk_count: int


class QuestionRequest(BaseModel):
    document_id: str
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str] = []
    model_info: dict = {}
