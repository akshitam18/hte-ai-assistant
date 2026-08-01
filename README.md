# 🎓 HTE AI Assistant

An AI-powered Retrieval-Augmented Generation (RAG) chatbot developed for the Higher & Technical Education (HTE) Department. The assistant enables users to ask questions in natural language and receive accurate answers from official HTE documents, along with the document source and page number.

---

## 📌 Project Overview

Students often struggle to find information from lengthy government PDFs related to scholarships, admissions, AICTE guidelines, and other educational policies.

HTE AI Assistant solves this problem by:

- 📄 Reading official PDF documents
- 🔍 Retrieving the most relevant information
- 🤖 Generating accurate answers using Google Gemini
- 📚 Displaying the source document and page number for transparency

---

## 🚀 Features

- Chat with official HTE documents
- PDF-based Question Answering
- Retrieval-Augmented Generation (RAG)
- Source citation with page numbers
- FastAPI backend
- Responsive frontend
- ChromaDB vector database
- Google Gemini integration

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- ChromaDB
- PyMuPDF
- Sentence Transformers
- Google Gemini API

### Frontend
- HTML
- CSS
- JavaScript

### Database
- ChromaDB (Vector Database)

---
## 📂 Project Structure

```
HTE-AI-Assistant/
│
├── backend/
│   ├── documents/
│   ├── chroma_db/
│   ├── config.py
│   ├── schemas.py
│   ├── utils.py
│   ├── pdf_loader.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── chroma_db.py
│   ├── gemini.py
│   ├── rag.py
│   ├── search_hybrid.py
│   ├── ingest.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── index.html
│   └── script.js
│
├── .gitignore
├── README.md
└── presentation/
```

## 📖 How It Works

1. Official HTE PDFs are loaded into the system.
2. PDF text is split into smaller chunks.
3. Chunks are converted into vector embeddings.
4. Embeddings are stored in ChromaDB.
5. User asks a question.
6. The most relevant document chunks are retrieved.
7. Gemini generates an answer using only the retrieved context.
8. The answer is returned with the source document and page number.

---

## 👥 Team Members

| Member | Responsibility |
|----------|----------------|
| Member 1 | PDF Processing, Chunking, Embeddings, ChromaDB |
| Member 2 | FastAPI Backend, API Integration, RAG Pipeline |
| Member 3 | Frontend UI & User Experience |
| Member 4 | Testing, Documentation, Presentation |

---

## 📌 Future Enhancements

- Voice Input
- Marathi Language Support
- OCR for Scanned PDFs
- Multi-document Search
- Conversation History
- Authentication & User Profiles
- Cloud Deployment

---

## 📄 License

This project has been developed as part of a hackathon prototype for educational purposes.

---

⭐ If you like this project, feel free to star the repository.
