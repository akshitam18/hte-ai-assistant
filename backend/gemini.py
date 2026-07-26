import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_answer(query: str, retrieved_context: str):
    """Generates grounded answers strictly using context."""
    prompt = f"""
    You are an administrative AI assistant for the Higher and Technical Education (HTE) Department.
    Answer the user's question accurately using ONLY the official context provided below.
    If the answer is not contained in the context, state clearly that the information is not available in the official documents.

    Context:
    {retrieved_context}

    Question: {query}
    Answer:
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text