import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def load_pdf(pdf_path: str) -> list[dict]:
    """
    Reads a PDF file page by page. 
    Attempts standard text extraction, and falls back to Tesseract OCR 
    if no text (or noise) is detected.
    """
    pages_data = []

    try:
        with fitz.open(pdf_path) as doc:
            for page_index, page in enumerate(doc):
                # Always calculate page_num directly from page_index (1-indexed)
                page_num = page_index + 1

                # 1. Try standard text extraction
                raw_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES)
                text = raw_text.strip() if isinstance(raw_text, str) else ""

                # 2. OCR Fallback if text is empty or contains garbage noise (< 20 chars)
                if len(text) < 20:
                    try:
                        pix = page.get_pixmap(dpi=300)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        
                        # Extract Marathi, Hindi, and English text via Tesseract
                        ocr_text = pytesseract.image_to_string(img, lang="mar+hin+eng").strip()
                        img.close()  # Free memory
                        
                        if ocr_text:
                            text = ocr_text
                    except Exception as ocr_err:
                        print(f"⚠️ OCR failed on Page {page_num}: {ocr_err}")

                # 3. Append valid text along with accurate page metadata
                if text:
                    pages_data.append({
                        "page": page_num,
                        "text": text
                    })

    except Exception as e:
        print(f"❌ Error reading PDF '{pdf_path}': {e}")

    return pages_data