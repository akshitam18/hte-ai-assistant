import fitz  # PyMuPDF

def load_pdf(pdf_path: str):
    """
    Extracts text page-by-page from a given PDF file.
    Retains page numbers for source reference and handles Devanagari (Marathi) text properly.
    """
    pages_data = []

    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)

        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            page_num = page_index + 1

            # Use TEXT_PRESERVE_LIGATURES flag to prevent Devanagari combined characters from breaking
            raw_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES)

            if not isinstance(raw_text, str):
                continue

            text = raw_text.strip()

            # Only append pages that contain actual text
            if text:
                pages_data.append({
                    "page": page_num,
                    "text": text
                })

        doc.close()

    except Exception as e:
        print(f"Error reading PDF '{pdf_path}': {e}")

    return pages_data