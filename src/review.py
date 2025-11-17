# src/review.py
from typing import Dict, Any, List
import re

def generate_review_from_summary(summary_obj: Dict[str,Any], parsed: Dict[str,Any]) -> Dict[str,Any]:
    """
    Use the rule-based feedback generator you already built.
    Returns a dict with strengths, gaps, suggestions and short_review.
    """
    # minimal wrapper: reuse some heuristics from your notebook
    skills = parsed.get("skills", [])
    contact_present = bool(parsed.get("emails") or parsed.get("phones"))
    strengths = []
    gaps = []
    suggestions = []
    if skills:
        strengths.append(f"Detected skills: {', '.join(skills[:6])}.")
    if not contact_present:
        gaps.append("Missing contact info (email/phone).")
        suggestions.append("Add a professional email in the header and ensure it's selectable text.")
    if len(skills) < 4:
        gaps.append(f"Few skills detected ({len(skills)}).")
        suggestions.append("List 5-12 relevant skills in a clear 'Skills' section.")
    short_review = (" ".join(strengths + gaps + suggestions))[:600]
    return {
        "resume_id": summary_obj.get("resume_id"),
        "name": summary_obj.get("name"),
        "fit_score": float(summary_obj.get("fit_score", 0.0)),
        "strengths": strengths,
        "gaps": gaps,
        "suggestions": suggestions,
        "short_review": short_review
    }
