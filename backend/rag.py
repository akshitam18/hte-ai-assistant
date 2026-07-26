from chroma_db import query_chroma
from gemini import generate_answer

def run_rag_pipeline(query: str):
    retrieval_results = query_chroma(query, n_results=3)
    
    docs = retrieval_results.get("documents", [[]])[0]
    metadatas = retrieval_results.get("metadatas", [[]])[0]
    
    if not docs:
        return {
            "answer": "No relevant context found in the database.",
            "source": "None",
            "page": 0
        }
    
    combined_context = "\n\n".join(docs)
    answer = generate_answer(query, combined_context)
    
    top_source = metadatas[0]["source"]
    top_page = metadatas[0]["page"]
    
    return {
        "answer": answer,
        "source": top_source,
        "page": top_page
    }