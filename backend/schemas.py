"""
schemas.py

Defines the request and response models
used by the FastAPI backend.
"""

from typing import Dict, Any, Optional
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
    relevance_score: str 
    detected_metadata: Optional[Dict[str, Any]] = None

class UploadResponse(BaseModel):
    message: str
    filename: str

class HealthResponse(BaseModel):
    status: str

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str = Field(..., description="'thumb_up' or 'thumb_down'")
    
class SummaryResponse(BaseModel):
    filename: str
    summary: str