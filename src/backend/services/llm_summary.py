import json
import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from src.backend.core.config import settings

logger = logging.getLogger(__name__)

def get_candidate_feedback(
    text: str,
    fit_score: float = None,
    job_description: str = "",
    matched_skills: List[str] = None,
    missing_skills: List[str] = None,
    resume_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Sends resume text + JD context to Groq for JD-specific analysis.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        logger.warning("GROQ_API_KEY not set. Returning mock summary.")
        return _get_mock_summary()

    matched_str = ", ".join(matched_skills) if matched_skills else "None identified"
    missing_str = ", ".join(missing_skills) if missing_skills else "None identified"
    resume_skills_str = ", ".join(resume_skills) if resume_skills else "None identified"

    try:
        client = Groq(api_key=api_key)
        prompt = f"""
You are an expert HR analyst. Analyze the following resume against the provided Job Description.

## Job Description:
{job_description[:2000]}

## Resume Text:
{text[:4000]}

## Pre-computed Data:
- Resume Fit Score: {fit_score}/100
- Skills found in resume: {resume_skills_str}
- Skills matching the JD: {matched_str}
- Skills required by JD but missing from resume: {missing_str}

## Instructions:
1. "name": Extract the candidate's full name.
2. "roles": Suggest 2-3 roles the candidate is best suited for, based on the JD.
3. "key_skills": List the candidate's most relevant skills FOR THIS SPECIFIC JD.
4. "matched_skills": List the skills that appear in BOTH the resume and JD.
5. "missing_skills": List the skills the JD requires but the resume lacks.
6. "summary": Write a detailed 4-6 sentence profile summary highlighting how the candidate aligns with THIS specific JD. Mention their strongest qualifications, relevant experience, and overall fit.
7. "strengths": List 3-5 specific strengths RELEVANT TO THE JD (not generic). Reference actual experience or skills from the resume that relate to the JD requirements.
8. "gaps": List 2-4 specific gaps or weaknesses RELATIVE TO THE JD (not generic). Only mention gaps that matter for this particular role.
9. "suggestions": List 3-5 actionable, specific suggestions to improve the resume FOR THIS JD. Each suggestion should reference a specific JD requirement.

You MUST return ONLY valid JSON matching this exact structure:
{{
    "name": "string",
    "roles": ["string"],
    "key_skills": ["string"],
    "matched_skills": ["string"],
    "missing_skills": ["string"],
    "summary": "string",
    "strengths": ["string"],
    "gaps": ["string"],
    "suggestions": ["string"]
}}
"""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional HR analyst that outputs strict JSON. All feedback must be specific to the given Job Description."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            temperature=0.1
        )

        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        return _get_mock_summary(error=str(e))

def _get_mock_summary(error: str = None) -> Dict[str, Any]:
    return {
        "name": "Unknown Candidate",
        "roles": ["Software Engineer"],
        "key_skills": ["Python"],
        "matched_skills": [],
        "missing_skills": [],
        "summary": "Could not generate summary from LLM." + (f" Error: {error}" if error else ""),
        "strengths": ["Basic text analyzed"],
        "gaps": ["LLM API failure"],
        "suggestions": ["Check API Key or rate limits."]
    }
