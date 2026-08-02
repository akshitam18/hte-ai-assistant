"""
main.py
Main FastAPI application for the HTE AI Assistant.
Handles API routing, authentication, health checks, file downloads, feedback logging, and error boundaries.
"""
import os
import json
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# Hardcoded Credentials / Rules
ADMIN_EMAIL = "admin@vjti.ac.in"
ADMIN_PASSWORD = "adminpassword123"

# Request schema for login
class LoginRequest(BaseModel):
    email: str
    password: str

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

FEEDBACK_LOG = "user_feedback.json"


@app.get("/")
def home():
    return {
        "message": "Welcome to HTE AI Assistant API 🚀"
    }


# Primary health check
@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "running"
    }


# Frontend status badge endpoint (/api/health)
@app.get("/api/health")
def api_health_check():
    return {
        "status": "online",
        "message": "RAG Engine Active"
    }


# Login API Endpoint (/api/login)
@app.post("/api/login")
def login_api(data: LoginRequest):
    email = data.email.strip().lower()
    password = data.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required."
        )

    # 1. Domain Check: Only @vjti.ac.in emails allowed
    if not email.endswith("@vjti.ac.in"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized email domain. Please use your @vjti.ac.in address."
        )

    # 2. Admin Check: Must pass correct ADMIN_PASSWORD
    if email == ADMIN_EMAIL:
        if password == ADMIN_PASSWORD:
            return {
                "success": True, 
                "redirect": "/rag_dashboard.html"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password for Admin account."
            )

    # 3. Any other @vjti.ac.in Email -> Direct to Work In Progress
    return {
        "success": True, 
        "redirect": "/work_in_progress.html"
    }


# =========================================================
# GET /documents: FIXES THE FRONTEND 404 & EMPTY FILE LIST
# =========================================================
@app.get("/documents")
def list_documents():
    """
    Returns a list of all indexed PDF documents in DOCS_DIR.
    """
    if not os.path.exists(DOCS_DIR):
        return []

    files = [
        f for f in os.listdir(DOCS_DIR)
        if f.lower().endswith(".pdf")
    ]

    return [{"name": f} for f in files]


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):

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

    # Check file size safely
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the limit."
        )

    # Save file asynchronously
    filename = await save_uploaded_file(file)

    # Trigger chunking and ChromaDB vector insertion
    ingest_file()

    return {
        "message": "Upload successful",
        "filename": filename
    }


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    result = run_rag_pipeline(request.question)

    if isinstance(result, dict):
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