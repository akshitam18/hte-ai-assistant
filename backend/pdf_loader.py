import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def load_pdf(pdf_path: str):
    pages_data = []

    try:
        doc = fitz.open(pdf_path)

        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            page_num = page_index + 1

            # 1. Try standard text extraction
            raw_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES)
            text = raw_text.strip() if isinstance(raw_text, str) else ""

            # 2. OCR Fallback for scanned Marathi text
            if not text:
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                # Requires tesseract-ocr-mar installed on system
                text = pytesseract.image_to_string(img, lang="mar+hin+eng").strip()

            # Only append if text was successfully found or extracted via OCR
            if text:
                pages_data.append({
                    "page": page_num,
                    "text": text
                })

        doc.close()

    except Exception as e:
        print(f"Error reading PDF '{pdf_path}': {e}")

    return pages_data