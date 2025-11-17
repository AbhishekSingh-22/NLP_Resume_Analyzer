# src/extract.py
from typing import Optional
from io import BytesIO
import pdfplumber

def extract_text_from_pdf_bytes(pdf_bytes: bytes, pages=None, repair: bool = False) -> str:
    """
    Extract text from a text-based PDF (not scanned).
    - pdf_bytes: raw bytes of a PDF
    - pages: optional sequence of page indices to extract
    - repair: pass to pdfplumber (False default)
    Returns combined text (page order).
    """
    text_pages = []
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            page_iter = pages if pages is not None else range(len(pdf.pages))
            for i in page_iter:
                page = pdf.pages[i]
                page_text = page.extract_text() or ""
                text_pages.append(page_text)
    except Exception as e:
        # If pdfplumber fails, return empty string and let caller handle
        raise
    return "\n\n".join(text_pages)


def sniff_is_text_pdf(pdf_bytes: bytes) -> bool:
    """Simple heuristic: look for %PDF and for presence of text-like sequences."""
    try:
        head = pdf_bytes[:200].lower()
        if not head.startswith(b"%pdf"):
            return False
        # quick heuristic: ASCII percentage of bytes
        printable = sum(1 for b in pdf_bytes[:2000] if 32 <= b <= 126)
        return printable / min(len(pdf_bytes[:2000]), 2000) > 0.3
    except Exception:
        return False
