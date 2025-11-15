# src/ingest.py
import fitz # PyMuPDF
import pdfplumber
from docx import Document
import re


def extract_text_pymupdf(path):
    doc = fitz.open(path)
    pages = []
    for page in doc:
        text = page.get_text("text")
        pages.append(text)
    raw = "\n\n".join(pages)
    return _clean_text(raw)


def extract_text_pdfplumber(path):
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
    return _clean_text("\n\n".join(texts))


def extract_text_docx(path):
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return _clean_text("\n\n".join(paragraphs))


# shared cleaning helper
def _clean_text(text):
    # Basic normalization — expand this later
    text = text.replace("\r", "\n")
    # collapse many spaces
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # strip leading/trailing whitespace on lines
    text = "\n".join([ln.strip() for ln in text.splitlines()])
    return text.strip()