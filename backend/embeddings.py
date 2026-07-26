from sentence_transformers import SentenceTransformer

# Load Hugging Face embedding model globally
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(texts: list[str]):
    """Generates vector embeddings for a list of text strings."""
    return embedding_model.encode(texts).tolist()