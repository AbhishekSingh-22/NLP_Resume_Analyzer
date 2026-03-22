from typing import Dict, Any
import numpy as np
from src.backend.services.embeddings import cosine_similarity

def calculate_fit_score(
    resume_emb: np.ndarray, 
    jd_emb: np.ndarray, 
    parsed_data: Dict[str, Any]
) -> float:
    """
    Computes a combined heuristic score for a resume against a job description.
    Weights: 
    - 60% Semantic Similarity (Cosine)
    - 20% Skills match
    - 10% Contact presence
    - 10% Valid Name Quality and Length Checks
    """
    
    # 1. Base semantic similarity (0-1 mapped to 0-60)
    sim = cosine_similarity(resume_emb, jd_emb)
    # Cosine might be lightly negative in some embeddings, clip it
    sim = max(0.0, sim)
    score_similarity = sim * 60.0
    
    # 2. JD Skills Match (0-20) — prioritize JD-matched skills over raw count
    jd_match = parsed_data.get("jd_match", {})
    matched_skills = jd_match.get("matched", [])
    total_jd_skills = len(jd_match.get("jd_skills", []))
    
    if total_jd_skills > 0:
        match_ratio = len(matched_skills) / total_jd_skills
        score_skills = match_ratio * 20.0
    else:
        # Fallback to raw skills count if no JD provided
        skills = parsed_data.get("skills", [])
        score_skills = min(len(skills) * 2.0, 20.0)
    
    # 3. Contact Presence (0-10)
    contacts = parsed_data.get("contacts", {})
    has_contact = (
        contacts.get("email") is not None or 
        contacts.get("phone") is not None or 
        contacts.get("linkedin") is not None
    )
    score_contact = 10.0 if has_contact else 0.0
    
    # 4. Name Quality (0-10)
    name = parsed_data.get("name", "")
    score_name = 10.0 if (name and len(name) > 2) else 0.0
    
    # Text penalty — using first_page_text length
    first_page = parsed_data.get("first_page_text", "")
    if len(first_page) < 100:
        return 0.0
        
    total_score = score_similarity + score_skills + score_contact + score_name
    return round(min(100.0, max(0.0, total_score)), 2)
