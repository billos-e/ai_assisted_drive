from __future__ import annotations

from io import BytesIO

import fitz
import pytesseract
from PIL import Image


def extract_pdf_bytes(content: bytes, languages: tuple[str, str]) -> str:
    document = fitz.open(stream=content, filetype="pdf")
    pages: list[str] = []
    ocr_language = "+".join(languages)
    for page in document:
        text = page.get_text("text").strip()
        if len(text) >= 40:
            pages.append(text)
            continue

        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        try:
            ocr_text = pytesseract.image_to_string(image, lang=ocr_language)
        except Exception:
            ocr_text = pytesseract.image_to_string(image)
        if ocr_text.strip():
            pages.append(ocr_text.strip())
    return "\n\n".join(pages)
