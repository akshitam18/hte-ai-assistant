"""
schemas.py

Defines the request and response models
used by the FastAPI backend.
"""

from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1, max_length=500,
        description="Question asked by the user"
    )

class AskResponse(BaseModel):
    answer: str
    source: str
    page: int

class UploadResponse(BaseModel):
    message: str
    filename: str

class HealthResponse(BaseModel):
    status: str