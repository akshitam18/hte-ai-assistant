import fitz  # PyMuPDF

def load_pdf(pdf_path: str):
    """
    Extracts text page-by-page from a given PDF file.
    Retains page numbers for source reference.
    """
    doc = fitz.open(pdf_path)
    pages_data = []
    
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            pages_data.append({
                "page": page_num,
                "text": text
            })
    
    return pages_data