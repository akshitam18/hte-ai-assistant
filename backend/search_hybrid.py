"""
backend/search_hybrid.py
Hybrid search implementation combining ChromaDB vector distance search
with exact string-match filtering ($contains).
"""
from backend.chroma_db import collection
from backend.embeddings import get_embeddings

def calculate_relevance(distance: float) -> str:
    """Converts Chroma distance metrics to a readable match percentage confidence string."""
    similarity = max(0.0, 1.0 - (distance / 2.0))
    return f"{int(similarity * 100)}%"

def execute_hybrid_search(query: str, n_results=3) -> dict:
    """
    Combines string-match processing with vector embedding verification.
    Ensures exact administrative dates, GR numbers, and keywords aren't lost in vector space.
    """
    from backend.chroma_db import collection
    from backend.embeddings import get_embeddings

    # 1. Semantic Vector Search
    query_embedding = get_embeddings([query])
    semantic_res = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    # Safely extract output lists handling potential None values
    raw_docs = semantic_res.get("documents") or [[]]
    raw_meta = semantic_res.get("metadatas") or [[]]
    raw_dist = semantic_res.get("distances") or [[]]

    merged_docs: list = list(raw_docs[0]) if raw_docs and raw_docs[0] else []
    merged_meta: list = list(raw_meta[0]) if raw_meta and raw_meta[0] else []
    merged_dist: list = list(raw_dist[0]) if raw_dist and raw_dist[0] else []

    # 2. Text Match Keyword Filter ($contains)
    try:
        keyword_res = collection.get(where_document={"$contains": query}, limit=5)
        kw_docs = keyword_res.get("documents") or []
        kw_meta = keyword_res.get("metadatas") or []

        # Merge keyword hits if not already present in semantic results
        for idx, kw_doc in enumerate(kw_docs):
            if kw_doc and kw_doc not in merged_docs:
                merged_docs.append(kw_doc)
                if kw_meta and idx < len(kw_meta):
                    merged_meta.append(kw_meta[idx])
                else:
                    merged_meta.append({})
                # Assign a calibrated baseline distance for exact keyword matches
                merged_dist.append(0.35)
    except Exception as e:
        print(f"Keyword search warning: {e}")

    return {
        "documents": merged_docs,
        "metadatas": merged_meta,
        "distances": merged_dist
    }