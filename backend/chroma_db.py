import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="hte_docs")

def store_chunks(chunks: list[dict], source_filename: str):
    """Stores text chunks and vector embeddings into ChromaDB."""
    from .embeddings import get_embeddings
    
    texts = [c["text"] for c in chunks]
    embeddings = get_embeddings(texts)
    
    ids = [f"{source_filename}_p{c['page']}_{i}" for i, c in enumerate(chunks)]
    metadatas = [{"source": source_filename, "page": c["page"]} for c in chunks]
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

def query_chroma(query_text: str, n_results=3):
    """Performs semantic search to retrieve matching document chunks."""
    from embeddings import get_embeddings
    
    query_embedding = get_embeddings([query_text])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results