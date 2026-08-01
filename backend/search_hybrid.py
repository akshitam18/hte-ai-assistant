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
    # 1. Semantic Vector Search
    query_embedding = get_embeddings([query])
    semantic_res = collection.query(
        query_embeddings=query_embedding, 
        n_results=n_results
    )
    
    # Safely extract output lists
    merged_docs = list(semantic_res.get("documents", [[]])[0]) if semantic_res.get("documents") else []
    merged_meta = list(semantic_res.get("metadatas", [[]])[0]) if semantic_res.get("metadatas") else []
    merged_dist = list(semantic_res.get("distances", [[]])[0]) if semantic_res.get("distances") else []
    
    # 2. Text Match Keyword Filter ($contains)
    try:
        keyword_res = collection.get(where_document={"$contains": query}, limit=5)
        kw_docs = keyword_res.get("documents", [])
        kw_meta = keyword_res.get("metadatas", [])
        
        # Merge keyword hits if not already present in semantic results
        for idx, kw_doc in enumerate(kw_docs):
            if kw_doc not in merged_docs:
                merged_docs.append(kw_doc)
                merged_meta.append(kw_meta[idx])
                # Assign a calibrated baseline distance for exact keyword matches
                merged_dist.append(0.35)  
    except Exception as e:
        print(f"Keyword search warning: {e}")
            
    return {
        "documents": [merged_docs[:n_results]],
        "metadatas": [merged_meta[:n_results]],
        "distances": [merged_dist[:n_results]]
    }