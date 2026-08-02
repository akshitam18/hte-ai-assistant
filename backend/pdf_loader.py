import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
                page_num = page_index + 1

                # 1. Try standard text extraction
                raw_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES)
                text = raw_text.strip() if isinstance(raw_text, str) else ""

                # 2. OCR Fallback if text is empty or contains garbage noise (< 20 chars)
                if len(text) < 20:
                    try:
                        pix = page.get_pixmap(dpi=300)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        
                        # Try multi-language first, fallback to english if language packs are missing
                        try:
                            ocr_text = pytesseract.image_to_string(img, lang="mar+hin+eng").strip()
                        except Exception:
                            ocr_text = pytesseract.image_to_string(img, lang="eng").strip()

                        img.close()  # Free memory
                        
                        if ocr_text:
                            text = ocr_text
                    except Exception as ocr_err:
                        print(f"⚠️ OCR failed on Page {page_num} of {pdf_path}: {ocr_err}")

                # 3. Append valid text along with accurate page metadata
                if text:
                    pages_data.append({
                        "page": page_num,
                        "text": text
                    })

    except Exception as e:
        print(f"❌ Error reading PDF '{pdf_path}': {e}")

    return pages_data