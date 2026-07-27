"""
config.py

This file stores all the configuration values used across the backend.
Keeping them in one place makes the project easier to maintain.
"""

import os
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

DOCS_DIR = "docs"   # Folder where uploaded PDFs are stored
CHROMA_DB_FOLDER = "chroma_db"   # Folder where ChromaDB stores embeddings

os.makedirs(DOCS_DIR, exist_ok=True)   #creating folders if they do not exist
os.makedirs(CHROMA_DB_FOLDER, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")    # Read the Gemini API key from the .env file
GEMINI_MODEL = "gemini-2.5-flash"     # Gemini model to use
MAX_FILE_SIZE = 20 * 1024 * 1024     # Maximum allowed PDF upload size (20 MB)
ALLOWED_EXTENSIONS = {".pdf"}    # Allowed file extensions

# ==========================
# RAG SETTINGS
# ==========================


TOP_K_RESULTS = 3    #Number of search results to retrieve from ChromaDB
CHUNK_SIZE = 500     #Number of characters in one chunk
CHUNK_OVERLAP = 100     # Number of overlapping characters between chunks

# ==========================
# API SETTINGS
# ==========================

HOST = "127.0.0.1"
PORT = 8000
