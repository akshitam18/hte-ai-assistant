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

    # 1. Search ChromaDB for relevant document chunks
    results = execute_hybrid_search(query, n_results=3)

    # execute_hybrid_search already returns 1D lists: list[str] and list[dict]
    docs = results.get("documents", []) or []
    metadatas = results.get("metadatas", []) or []

    # 2. If no matching docs found, return fallback
    if not docs:
        ans = generate_answer(query, retrieved_context="")
        return {
            "answer": ans, 
            "source": "None", 
            "page": 0,
            "relevance_score": "0.0"
        }

    # 3. Combine context and generate answer
    context = "\n\n".join(docs)
    answer = generate_answer(query, context)

    # 4. Safely extract top source name and page number
    top_source = "Unknown"
    top_page = 0

    if metadatas and len(metadatas) > 0:
        top_meta = metadatas[0]
        if isinstance(top_meta, dict):
            raw_source = top_meta.get("source", "Unknown")
            top_source = os.path.basename(raw_source) if raw_source else "Unknown"
            top_page = top_meta.get("page", 0)

    # 5. Calculate or set relevance score as a String for AskResponse validation
    rel_score = "0.85"
    if "distances" in results and results["distances"]:
        # ChromaDB distance to relevance conversion
        dist = results["distances"][0]
        rel_score = f"{max(0.0, min(1.0, 1.0 - float(dist))):.2f}"

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

    # 1. Get document chunks from ChromaDB for this specific file
    try:
        results = collection.get(where={"source": clean_name}, include=["documents"])
        chunks = results.get("documents", []) or []
    except Exception:
        chunks = []

    if not chunks:
        return f"No indexed content found for '{clean_name}'."

    # 2. Combine top chunks and get summary
    full_text = "\n\n".join(chunks[:10])
    return summarize_text(full_text)