import fitz  # PyMuPDF
import pdfplumber
import logging
from io import BytesIO
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def extract_text_pymupdf(pdf_bytes: bytes) -> str:
    """Extract full text from all pages."""
    text = ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        doc.close()
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {e}")
    return text.strip()

def extract_first_page_text(pdf_bytes: bytes) -> str:
    """Extract text from only the first page of the PDF."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) > 0:
            text = doc[0].get_text() or ""
            doc.close()
            return text.strip()
        doc.close()
    except Exception as e:
        logger.error(f"First page extraction failed: {e}")
    return ""

def extract_hyperlinks(pdf_bytes: bytes) -> List[str]:
    """Extract all hyperlinks embedded in the PDF (not just visible text)."""
    links = []
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            for link in page.get_links():
                uri = link.get("uri", "")
                if uri:
                    links.append(uri)
        doc.close()
    except Exception as e:
        logger.error(f"Hyperlink extraction failed: {e}")
    return links

def extract_text_pdfplumber(pdf_bytes: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"pdfplumber extraction failed: {e}")
    return text.strip()

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts text using PyMuPDF, falls back to pdfplumber if text is too short."""
    text = extract_text_pymupdf(pdf_bytes)
    if len(text.strip()) < 50:
        logger.info("PyMuPDF returned very little text, falling back to pdfplumber.")
        text = extract_text_pdfplumber(pdf_bytes)
    return text

def extract_all_from_pdf(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Master extraction function. Returns:
    - full_text: all pages combined
    - first_page_text: just the first page (for NER and embedding)
    - hyperlinks: all embedded URIs from the PDF
    """
    full_text = extract_text_from_pdf_bytes(pdf_bytes)
    first_page_text = extract_first_page_text(pdf_bytes)
    hyperlinks = extract_hyperlinks(pdf_bytes)
    return {
        "full_text": full_text,
        "first_page_text": first_page_text,
        "hyperlinks": hyperlinks
    }
