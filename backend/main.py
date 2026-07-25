"""
main.py

Main FastAPI application for the HTE AI Assistant.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import HOST, PORT
from schemas import (
    AskRequest,
    AskResponse,
    UploadResponse,
    HealthResponse,
)
from utils import (
    allowed_file,
    save_uploaded_file,
)

# Member 1 will provide this later
# from rag import ask_ai

app = FastAPI(
    title="HTE AI Assistant",
    version="1.0.0",
    description="AI-powered assistant for HTE documents"
)

# ==========================
# CORS
# ==========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # For prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# HOME
# ==========================

@app.get("/")
def home():
    return {
        "message": "Welcome to HTE AI Assistant API 🚀"
    }


# ==========================
# HEALTH CHECK
# ==========================

@app.get(
    "/health",
    response_model=HealthResponse
)
def health_check():

    return {
        "status": "running"
    }


# ==========================
# UPLOAD PDF
# ==========================

@app.post(
    "/upload",
    response_model=UploadResponse
)
def upload_pdf(
    file: UploadFile = File(...)
):

    if not allowed_file(file.filename):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    filename = save_uploaded_file(file)

    # Member 1
    # ingest_document(filename)

    return {
        "message": "Upload successful",
        "filename": filename
    }


# ==========================
# ASK QUESTION
# ==========================

@app.post(
    "/ask",
    response_model=AskResponse
)
def ask_question(
    request: AskRequest
):

    # Replace this block with:
    # result = ask_ai(request.question)

    result = {
        "answer": "This is a placeholder response until the RAG pipeline is integrated.",
        "source": "Scholarship.pdf",
        "page": 1
    }

    return result


# ==========================
# RUN SERVER
# ==========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True
    )