import fitz  # PyMuPDF

def load_pdf(pdf_path: str):
    """
    Extracts text page-by-page from a given PDF file.
    Retains page numbers for source reference.
    """
    doc = fitz.open(pdf_path)
    pages_data = []
    
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        page_num = page_index + 1
        raw_text = page.get_text("text")
        if not isinstance(raw_text, str):
            continue
        text = raw_text.strip()
        if text:
            pages_data.append({
                "page": page_num,
                "text": text
            })
    
    return pages_data