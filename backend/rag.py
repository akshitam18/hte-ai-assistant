import os
from backend.chroma_db import collection, query_chroma
from backend.gemini import generate_answer, summarize_text

def run_rag_pipeline(query: str) -> dict:
    """Finds matching context from ChromaDB and gets an answer from Gemini."""
    if not query or not query.strip():
        return {"answer": "Please enter a question.", "source": "None", "page": 0}

    # 1. Search ChromaDB for relevant document chunks
    results = query_chroma(query, n_results=3)
    
    docs = results.get("documents", [[]])[0] if results.get("documents") else []
    metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

    # 2. If no matching docs found, return fallback
    if not docs:
        ans = generate_answer(query, retrieved_context="")
        return {"answer": ans, "source": "None", "page": 0}

    # 3. Combine context and generate answer
    context = "\n\n".join(docs)
    answer = generate_answer(query, context)

    # 4. Get source name and page number
    top_source = os.path.basename(metadatas[0].get("source", "Unknown")) if metadatas else "Unknown"
    top_page = metadatas[0].get("page", 0) if metadatas else 0

    return {
        "answer": answer,
        "source": top_source,
        "page": top_page
    }


def generate_document_summary(filename: str) -> str:
    """Finds all chunks for a file and summarizes them."""
    if not filename:
        return "Filename not provided."

    clean_name = os.path.basename(filename)

    # 1. Get document chunks from ChromaDB
    try:
        results = collection.get(where={"source": clean_name}, include=["documents"])
        chunks = results.get("documents", [])
    except Exception:
        chunks = []

    if not chunks:
        return f"No indexed content found for '{clean_name}'."

    # 2. Combine top chunks and get summary
    full_text = "\n\n".join(chunks[:10])
    return summarize_text(full_text)