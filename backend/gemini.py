import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_answer(query: str, retrieved_context: str) -> str:
    """Generates an answer in English, Marathi, or Hindi based on the question."""
    prompt = f"""
You are an AI assistant for the Higher and Technical Education (HTE) Department.

Rules:
1. Detect the language of the Question (English, Marathi, or Hindi) and answer in that SAME language.
2. Keep official terms unchanged (e.g., "शासन निर्णय", "GR Number", "परिपत्रक", "MahaDBT").
3. Answer ONLY using the Context below. If context is empty, say information is not available.

Context:
{retrieved_context}

Question: {query}
Answer:
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        response_text = response.text or ""
        return response_text.strip()
    except Exception as e:
        return f"Error: {e}"


def summarize_text(document_text: str) -> str:
    """Creates a short summary under 250 words."""
    prompt = f"""
Summarize the following document for the HTE Department.

Rules:
1. Keep it under 250 words.
2. Keep official terms like "शासन निर्णय" or "GR Number".
3. Write in the same language as the document text.

Document:
{document_text}

Summary:
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        response_text = response.text or ""
        return response_text.strip()
    except Exception as e:
        return f"Error: {e}"