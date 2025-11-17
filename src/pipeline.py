# src/pipeline.py
from typing import Dict, Any
from .extract import extract_text_from_pdf_bytes, sniff_is_text_pdf
from .parse import parse_basic_fields
from .score import enriched_score
from .summarize import summarize_with_model
from .review import generate_review_from_summary

def process_pdf_bytes(pdf_bytes: bytes, resume_id: str = None, model_fn=None) -> Dict[str,Any]:
    """
    High-level pipeline:
      - sniff if PDF likely text
      - extract text
      - parse fields
      - score
      - summarize (rule or model)
      - review
    Returns a dict with parsed, score, summary, review
    """
    if not sniff_is_text_pdf(pdf_bytes):
        # caller can decide to OCR or reject
        raise ValueError("PDF does not appear to be text-based. Use OCR pipeline for scanned PDFs.")
    text = extract_text_from_pdf_bytes(pdf_bytes)
    parsed = parse_basic_fields(text)
    if resume_id:
        parsed["resume_id"] = resume_id
    score_record = enriched_score(parsed)
    summary = summarize_with_model(parsed, score_record, model_fn=model_fn)
    review = generate_review_from_summary(summary, parsed)
    return {"parsed": parsed, "score": score_record, "summary": summary, "review": review}
