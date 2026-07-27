import os
from backend.pdf_loader import load_pdf
from backend.chunking import chunk_text
from backend.chroma_db import store_chunks

from backend.config import DOCS_DIR

def ingest_file():
    if not os.path.exists(DOCS_DIR):
        print(f"Directory {DOCS_DIR} not found. Create it and add PDFs.")
        return

    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(DOCS_DIR, filename)
            print(f"Processing: {filename}...")
            
            pages_data = load_pdf(pdf_path)
            chunks = chunk_text(pages_data)
            store_chunks(chunks, source_filename=filename)
            
            print(f"Successfully processed {filename} into ChromaDB!")

if __name__ == "__main__":
    ingest_file()