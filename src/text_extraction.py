# src/text_extraction.py
from pathlib import Path
from typing import List
import pdfplumber
import logging
from .config import DATA_DIR

logger = logging.getLogger(__name__)

def extract_text_from_pdf(path: str | Path) -> str:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    pages: List[str] = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            txt = p.extract_text()
            if txt:
                pages.append(txt)
    text = "\n".join(pages)
    return clean_text(text)

def clean_text(text: str) -> str:
    # minimal cleaning: strip empty lines and normalize whitespace
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)
