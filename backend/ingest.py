"""
backend/ingest.py
Handles loading PDF files, splitting text into chunks, and storing them into ChromaDB.
"""
import os
from backend.pdf_loader import load_pdf
from backend.chunking import chunk_text
from backend.chroma_db import store_chunks
from backend.config import DOCS_DIR


def process_single_file(filename: str) -> bool:
    """Processes and ingests a single PDF file into ChromaDB."""
    pdf_path = os.path.join(DOCS_DIR, filename)

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False

    try:
        print(f"⏳ Reading PDF: {filename}...")
        pages_data = load_pdf(pdf_path)

        # Check if any text was actually extracted
        if not pages_data:
            print(f"⚠️ Warning: Could not extract any text from '{filename}'. The file might be empty or scanned.")
            return False

        print(f"⏳ Splitting text into chunks for {filename}...")
        chunks = chunk_text(pages_data)

        print(f"⏳ Saving chunks to vector database...")
        store_chunks(chunks, source_filename=filename)

        print(f"✅ Successfully processed {filename} into ChromaDB!\n")
        return True

    except Exception as e:
        print(f"❌ Failed to process {filename}: {e}\n")
        return False


def ingest_file() -> None:
    """Batch ingests all PDF files in the DOCS_DIR directory."""
    if not os.path.exists(DOCS_DIR):
        print(f"Directory '{DOCS_DIR}' not found.")
        return

    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found to ingest.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process...\n")
    for filename in pdf_files:
        process_single_file(filename)


if __name__ == "__main__":
    ingest_file()