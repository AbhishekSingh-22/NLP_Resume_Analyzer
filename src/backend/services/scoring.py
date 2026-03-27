from typing import Dict, Any
import numpy as np
from src.backend.services.embeddings import cosine_similarity

def calculate_fit_score(
    resume_emb: np.ndarray, 
    jd_emb: np.ndarray, 
    parsed_data: Dict[str, Any],
    llm_compatibility_score: float = 50.0
) -> float:
    """
    Computes a combined heuristic score for a resume against a job description.
    Weights: 
    - 60% Semantic Similarity (Cosine)
    - 10% Exact Keyword Skill Match (ATS-style)
    - 15% LLM-based Skill Compatibility (transferable skills)
    - 10% Contact Presence
    -  5% Name Quality
    """
    
    # 1. Base semantic similarity (0-1 mapped to 0-60)
    sim = cosine_similarity(resume_emb, jd_emb)
    sim = max(0.0, sim)
    score_similarity = sim * 60.0
    print(f"📊 Cosine Similarity: {sim:.4f} (contributes {score_similarity:.2f}/60 to score)")
    
    # 2. Exact JD Skills Match — ATS keyword matching (0-10)
    jd_match = parsed_data.get("jd_match", {})
    matched_skills = jd_match.get("matched", [])
    total_jd_skills = len(jd_match.get("jd_skills", []))
    
    if total_jd_skills > 0:
        match_ratio = len(matched_skills) / total_jd_skills
        score_skills = match_ratio * 10.0
    else:
        skills = parsed_data.get("skills", [])
        score_skills = min(len(skills) * 1.0, 10.0)
    
    # 3. LLM Skill Compatibility — transferable skill evaluation (0-15)
    # e.g., PostgreSQL ≈ MySQL (both RDBMS), React ≈ Vue (frontend frameworks)
    score_compatibility = (llm_compatibility_score / 100.0) * 15.0
    
    # 4. Contact Presence (0-10)
    contacts = parsed_data.get("contacts", {})
    has_contact = (
        contacts.get("email") is not None or 
        contacts.get("phone") is not None or 
        contacts.get("linkedin") is not None
    )
    score_contact = 10.0 if has_contact else 0.0
    
    # 5. Name Quality (0-5)
    name = parsed_data.get("name", "")
    score_name = 5.0 if (name and len(name) > 2) else 0.0
    
    # Text penalty — reject unreadable PDFs
    first_page = parsed_data.get("first_page_text", "")
    if len(first_page) < 100:
        return 0.0
        
    total_score = (
        score_similarity + 
        score_skills + 
        score_compatibility + 
        score_contact + 
        score_name
    )
    final = round(min(100.0, max(0.0, total_score)), 2)
    
    print("\n" + "="*60)
    print("🏆 SCORING BREAKDOWN")
    print("-"*60)
    print(f"  Cosine Similarity (60%):     {score_similarity:.2f} / 60")
    print(f"  Exact Skill Match (10%):     {score_skills:.2f} / 10  ({len(matched_skills)}/{total_jd_skills} JD skills)")
    print(f"  LLM Compatibility (15%):     {score_compatibility:.2f} / 15  (raw: {llm_compatibility_score:.0f}/100)")
    print(f"  Contact Presence  (10%):     {score_contact:.2f} / 10")
    print(f"  Name Quality       (5%):     {score_name:.2f} / 5")
    print("-"*60)
    print(f"  TOTAL FIT SCORE:             {final} / 100")
    print("="*60 + "\n")
    
    return final
