"""
main.py

Main FastAPI application for the HTE AI Assistant.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import HOST, PORT, MAX_FILE_SIZE
from backend.schemas import (
    AskRequest,
    AskResponse,
    UploadResponse,
    HealthResponse,
)
from backend.utils import (
    allowed_file,
    save_uploaded_file,
)

from backend.ingest import run_ingestion
from backend.rag import run_rag_pipeline

app = FastAPI(
    title="HTE AI Assistant",
    version="1.0.0",
    description="AI-powered assistant for HTE documents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Welcome to HTE AI Assistant API 🚀"
    }


@app.get(
    "/health",
    response_model=HealthResponse
)
def health_check():

    return {
        "status": "running"
    }

@app.post(
    "/upload",
    response_model=UploadResponse
)
def upload_pdf(
    file: UploadFile = File(...)
):

    if file.filename is None:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 20 MB limit."
        )

    filename = save_uploaded_file(file)

    # ==========================
    # Run ingestion pipeline
    # ==========================

    run_ingestion()

    return {
        "message": "Upload successful",
        "filename": filename
    }


@app.post(
    "/ask",
    response_model=AskResponse
)
def ask_question(
    request: AskRequest
):

    result = run_rag_pipeline(
        request.question
    )

    return result


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )
