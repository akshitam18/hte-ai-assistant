"""
main.py
Main FastAPI application for the HTE AI Assistant.
Handles API routing, file downloads, feedback logging, and error boundaries.
"""
import os
import json
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import DOCS_DIR, HOST, PORT, MAX_FILE_SIZE
from backend.schemas import (
    AskRequest,
    AskResponse,
    UploadResponse,
    HealthResponse,
    FeedbackRequest,
    SummaryResponse,
)
from backend.utils import (
    allowed_file,
    save_uploaded_file,
)

from backend.ingest import ingest_file
from backend.rag import run_rag_pipeline, generate_document_summary

app = FastAPI(
    title="HTE AI Assistant",
    version="1.0.0",
    description="AI-powered assistant for HTE documents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

FEEDBACK_LOG = "user_feedback.json"

@app.get("/")
def home():
    return {
        "message": "Welcome to HTE AI Assistant API 🚀"
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "running"
    }

@app.post("/upload", response_model=UploadResponse)
def upload_pdf(file: UploadFile = File(...)):

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

    ingest_file() 

    return {
        "message": "Upload successful",
        "filename": filename
    }


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    result = run_rag_pipeline(request.question)
    
    if isinstance(result, dict):
        # Convert float to str, or set default string if missing
        if "relevance_score" in result:
            result["relevance_score"] = str(result["relevance_score"])
        else:
            result["relevance_score"] = "0.0"
            
    return result

@app.get("/docs/{filename}")
def download_document(filename: str):
    
    target_path = os.path.join(DOCS_DIR, filename)
    if not os.path.exists(target_path):
        raise HTTPException(
            status_code=404,
            detail="Requested document file not found on server."
        )
    return FileResponse(
        path=target_path,
        media_type="application/pdf",
        filename=filename
    )

@app.post("/feedback")
def record_feedback(entry: FeedbackRequest):

    record = {
        "timestamp": datetime.now().isoformat(),
        "question": entry.question,
        "answer": entry.answer,
        "rating": entry.rating
    }

    history = []
    if os.path.exists(FEEDBACK_LOG):
        try:
            with open(FEEDBACK_LOG, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append(record)
    with open(FEEDBACK_LOG, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return {"status": "Feedback logged successfully."}

@app.get("/summarize/{filename}", response_model=SummaryResponse)
def summarize_document(filename: str):
    
    summary_text = generate_document_summary(filename)
    return {
        "filename": filename,
        "summary": summary_text
    }

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )