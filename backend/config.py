"""
config.py

This file stores all the configuration values used across the backend.
Keeping them in one place makes the project easier to maintain.
"""

import os
from dotenv import load_dotenv

load_dotenv()  

DOCS_DIR = "docs"   
CHROMA_DB_FOLDER = "chroma_db"   

os.makedirs(DOCS_DIR, exist_ok=True)   
os.makedirs(CHROMA_DB_FOLDER, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")    
GEMINI_MODEL = "gemini-2.5-flash"     
MAX_FILE_SIZE = 20 * 1024 * 1024    
ALLOWED_EXTENSIONS = {".pdf"}    


TOP_K_RESULTS = 3    
CHUNK_SIZE = 500    
CHUNK_OVERLAP = 100     


HOST = "127.0.0.1"
PORT = 8000
