import os
from backend.chroma_db import collection
from backend.search_hybrid import execute_hybrid_search, calculate_relevance
from backend.gemini import generate_answer, summarize_text

def run_rag_pipeline(query: str) -> dict:
    """Finds matching context from ChromaDB and gets an answer from Gemini."""
    if not query or not query.strip():
        return {
            "answer": "Please enter a question.",
            "source": "None",
            "page": 0,
            "relevance_score": "0.0"
        }

    results = execute_hybrid_search(query, n_results=3)

    docs = results.get("documents", []) or []
    metadatas = results.get("metadatas", []) or []

    if not docs:
        ans = generate_answer(query, retrieved_context="")
        return {
            "answer": ans,
            "source": "None",
            "page": 0,
            "relevance_score": "0.0"
        }

    context = "\n\n".join(docs)
    answer = generate_answer(query, context)

    top_source = "Unknown"
    top_page = 0
    if metadatas and len(metadatas) > 0:
        top_meta = metadatas[0]
        if isinstance(top_meta, dict):
            raw_source = top_meta.get("source", "Unknown")
            top_source = os.path.basename(raw_source) if raw_source else "Unknown"
            top_page = top_meta.get("page", 0)

    rel_score = "0.85"
    if "distances" in results and results["distances"]:
        dist = results["distances"][0]
        rel_score = f"{max(0.0, min(1.0, 1.0 - float(dist))):.2f}"

    # If the answer itself says info isn't available, don't show a misleading citation
    if "not available" in answer.lower() or "उपलब्ध नाही" in answer:
        top_source = "None"
        top_page = 0
        rel_score = "0.0"

    return {
        "answer": answer,
        "source": top_source,
        "page": top_page,
        "relevance_score": rel_score
    }


def generate_document_summary(filename: str) -> str:
    """Finds all chunks for a file and summarizes them."""
    if not filename:
        return "Filename not provided."

    clean_name = os.path.basename(filename)

    try:
        results = collection.get(where={"source": clean_name}, include=["documents"])
        chunks = results.get("documents", []) or []
    except Exception:
        chunks = []

    if not chunks:
        return f"No indexed content found for '{clean_name}'."

    full_text = "\n\n".join(chunks[:10])
    return summarize_text(full_text)