"""
config.py

This file stores all the configuration values used across the backend.
Keeping them in one place makes the project easier to maintain.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Folder where uploaded PDFs are stored
DOCUMENTS_FOLDER = "documents"

# Folder where ChromaDB stores embeddings
CHROMA_DB_FOLDER = "chroma_db"

# Read the Gemini API key from the .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini model to use
GEMINI_MODEL = "gemini-2.5-flash"

# Maximum allowed PDF upload size (20 MB)
MAX_FILE_SIZE = 20 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf"}

# ==========================
# RAG SETTINGS
# ==========================

# Number of search results to retrieve from ChromaDB
TOP_K_RESULTS = 3

# Number of characters in one chunk
CHUNK_SIZE = 500

# Number of overlapping characters between chunks
CHUNK_OVERLAP = 100

# ==========================
# API SETTINGS
# ==========================

HOST = "127.0.0.1"
PORT = 8000