from sentence_transformers import SentenceTransformer

# Load a high-performing multilingual model (supports Marathi, Hindi, English, etc.)
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_embeddings(texts: list[str]):
    """Generates vector embeddings for a list of text strings."""
    return embedding_model.encode(texts).tolist()