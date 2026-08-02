import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Model name (use gemini-2.5-flash or gemini-1.5-flash)
MODEL_NAME = 'gemini-3.5-flash'

def generate_answer(query: str, retrieved_context: str) -> str:
    """Generates an answer in English, Marathi, or Hindi based on the question."""
    prompt = f"""
You are an AI assistant for Higher and Technical Education documents.

Rules:
1. Detect the language of the Question (English, Marathi, or Hindi) and answer in that SAME language.
2. Keep official terms unchanged (e.g., "शासन निर्णय", "GR Number", "परिपत्रक", "MahaDBT").
3. Answer ONLY using the Context below. If context is empty, say information is not available.
4. Output ONLY the direct answer. Do NOT add meta-introductions or preambles.

Context:
{retrieved_context}

Question: {query}
Answer:
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        response_text = response.text or ""
        return response_text.strip()
    except Exception as e:
        return f"Error: {e}"


def summarize_text(document_text: str) -> str:
    """Creates a short summary under 250 words."""
    prompt = f"""
Summarize the following document clearly and concisely using Markdown formatting.

Strict Rules:
1. Do NOT include introductory phrases like "Here is the summary...", "Summary for HTE Department:", or conversational preambles.
2. Start DIRECTLY with the content or section headings (e.g., "**Document Overview**").
3. Keep the total length under 250 words.
4. Preserve official terms like "शासन निर्णय" or "GR Number".
5. Write in the same language as the document text.

Document Text:
{document_text}

Summary:
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        response_text = response.text or ""
        return response_text.strip()
    except Exception as e:
        return f"Error: {e}"