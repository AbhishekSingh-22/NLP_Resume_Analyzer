# src/summarize.py
from typing import Dict, Any, Optional

def rule_based_summary(parsed: Dict[str, Any], score_record: Dict[str,Any]) -> Dict[str,Any]:
    """
    Fast deterministic summary used as fallback:
      - name, years_experience (if parsed), top_skills, short summary text, fit_score
    """
    name = parsed.get("primary_name")
    skills = parsed.get("skills", [])[:12]
    preview = parsed.get("preview","")
    # naive years extraction (optional)
    years = None
    # short summary
    summary_text = f"{name or 'Candidate'} — {len(skills)} skills detected: {', '.join(skills[:6])}."
    return {
        "resume_id": parsed.get("resume_id"),
        "name": name,
        "top_skills": skills,
        "summary": summary_text,
        "years_experience": years,
        "fit_score": float(score_record.get("score", 0.0))
    }

# If you want a wrapper that can call an LLM, place it here and gate by config flag.
def summarize_with_model(parsed: Dict[str,Any], score_record: Dict[str,Any], model_fn: Optional[callable]=None) -> Dict[str,Any]:
    """
    If model_fn provided, call it with text prompt to produce a JSON-like dictionary.
    Fallback to rule_based_summary otherwise.
    model_fn should accept 'text' and return dict or string JSON.
    """
    if model_fn is None:
        return rule_based_summary(parsed, score_record)
    try:
        return model_fn(parsed, score_record)
    except Exception:
        return rule_based_summary(parsed, score_record)
