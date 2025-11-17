
from typing import Dict, Any

def baseline_score(parsed: Dict[str, Any]) -> float:
    """
    Simple baseline score combining:
      - presence of contact
      - number of skills (capped)
      - character count (proxy for content)
    Returns score in 0-100 (not calibrated).
    """
    score = 0.0
    has_contact = bool(parsed.get("emails") or parsed.get("phones"))
    score += 30.0 if has_contact else 0.0
    n_skills = len(parsed.get("skills", []))
    score += min(n_skills, 10) * 5.0   # up to 50 points
    chars = len(parsed.get("preview",""))
    if chars > 4000:
        score += 20.0
    elif chars > 2000:
        score += 10.0
    elif chars > 800:
        score += 5.0
    return round(min(100.0, score), 3)

def enriched_score(parsed: Dict[str, Any], summary: Dict[str, Any]=None) -> Dict[str, Any]:
    """
    Compute base score and return a dict with details.
    The `summary` argument is optional to support callers that pass it or not.
    """
    base = baseline_score(parsed)
    return {"score": base, "reasons": {"has_contact": bool(parsed.get("emails") or parsed.get("phones")), "n_skills": len(parsed.get("skills",[]))}}
