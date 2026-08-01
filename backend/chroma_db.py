"""
backend/chroma_db.py
ChromaDB database configuration, chunk storage, and low-level querying.
"""
from typing import Any

import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="hte_docs")

def store_chunks(chunks: list[dict], source_filename: str, extra_metadata: dict | None = None):
    """
    Stores text chunks, vector embeddings, and rich metadata into ChromaDB.
    Supports extra structural metadata extracted by Developer 3.
    """
    # Guard against empty chunks to avoid crashing ChromaDB with empty embeddings []
    if not chunks:
        print(f"Warning: No valid text chunks found in {source_filename}. Skipping ChromaDB insertion.")
        return

    from backend.embeddings import get_embeddings
    
    texts = [c["text"] for c in chunks]
    embeddings = get_embeddings(texts)
    
    if not embeddings:
        print(f"Warning: Failed to generate embeddings for {source_filename}. Skipping ChromaDB insertion.")
        return
    
    ids = [f"{source_filename}_p{c['page']}_{i}" for i, c in enumerate(chunks)]
    
    # Base metadata with fallback support for extended Dev 3 fields
    metadatas = []
    for c in chunks:
        meta = {
            "source": source_filename, 
            "page": c["page"]
        }
        if extra_metadata is not None:
            meta.update(extra_metadata)
        metadatas.append(meta)
    
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

def query_chroma(query_text: str, n_results=3) -> Any:
    """Performs semantic search to retrieve matching document chunks with distances."""
    from backend.embeddings import get_embeddings
    
    query_embedding = get_embeddings([query_text])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results