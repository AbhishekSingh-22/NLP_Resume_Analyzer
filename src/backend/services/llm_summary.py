import json
import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from src.backend.core.config import settings

logger = logging.getLogger(__name__)


def evaluate_skill_compatibility(
    resume_skills: List[str],
    jd_skills: List[str],
    matched_skills: List[str],
    missing_skills: List[str]
) -> float:
    """
    Uses Groq LLM to evaluate transferable skill compatibility.
    e.g., PostgreSQL on resume + MySQL in JD → candidate knows RDBMS → high compatibility.
    
    Returns a score from 0-100.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return 50.0  # neutral fallback

    if not missing_skills:
        return 100.0  # all JD skills are matched exactly

    resume_str = ", ".join(resume_skills) if resume_skills else "None"
    jd_str = ", ".join(jd_skills) if jd_skills else "None"
    matched_str = ", ".join(matched_skills) if matched_skills else "None"
    missing_str = ", ".join(missing_skills) if missing_skills else "None"

    try:
        client = Groq(api_key=api_key)
        prompt = f"""You are an expert technical recruiter evaluating skill transferability.

A candidate has the following skills on their resume:
{resume_str}

The job description requires these skills:
{jd_str}

Already exactly matched: {matched_str}
Skills listed as "missing" (not exact keyword match): {missing_str}

For each "missing" skill, evaluate whether the candidate has a RELATED or TRANSFERABLE skill from their resume. For example:
- PostgreSQL (resume) covers MySQL (JD) → both are RDBMS, high transferability
- React (resume) covers Vue.js (JD) → both are frontend JS frameworks, moderate transferability  
- Python (resume) does NOT cover Java (JD) → different languages, low transferability
- AWS (resume) partially covers GCP (JD) → both are cloud platforms, moderate transferability

Rate the overall skill compatibility from 0-100 where:
- 100 = All "missing" skills have strong equivalents on the resume
- 75 = Most missing skills have related technologies on the resume
- 50 = Some missing skills have loosely related alternatives  
- 25 = Few missing skills have any related coverage
- 0 = No transferable skills exist for any of the missing requirements

Return ONLY a JSON object: {{"compatibility_score": <number>, "reasoning": "<one sentence>"}}"""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a technical skill evaluator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=150
        )
        
        result = json.loads(response.choices[0].message.content)
        score = float(result.get("compatibility_score", 50))
        logger.info(f"LLM skill compatibility: {score}/100 — {result.get('reasoning', '')}")
        return max(0.0, min(100.0, score))
    except Exception as e:
        logger.error(f"Skill compatibility evaluation failed: {e}")
        return 50.0  # neutral fallback


def summarize_for_embedding(text: str, text_type: str = "resume") -> str:
    """
    Uses Groq LLM to produce a keyword-rich, compact summary of the input text
    optimized for semantic embedding. Preserves all critical terms (skills, tools,
    job titles, certifications, technologies) while removing noise.
    
    Args:
        text: The raw text to summarize (resume first page or job description)
        text_type: Either "resume" or "job_description"
    
    Returns:
        A condensed, keyword-dense summary. Falls back to raw text on failure.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        logger.warning("GROQ_API_KEY not set, returning raw text for embedding.")
        return text[:2000]

    if text_type == "resume":
        system_prompt = "You are a resume keyword extraction expert."
        user_prompt = f"""Summarize the following resume text into a dense, keyword-rich paragraph optimized for semantic similarity matching.

CRITICAL RULES:
- PRESERVE every single: skill name, programming language, framework, tool, technology, certification, job title, company name, degree, and measurable achievement
- REMOVE filler words, generic phrases like "team player" or "hard worker", formatting artifacts, and repeated information
- KEEP the candidate's name at the very beginning
- Compress descriptions into concise keyword-dense phrases
- The output should be roughly 150-250 words — compact but retaining ALL matchable keywords
- Output ONLY the summary text, nothing else

Resume text:
{text[:3000]}"""
    else:
        system_prompt = "You are a job description keyword extraction expert."
        user_prompt = f"""Summarize the following job description into a dense, keyword-rich paragraph optimized for semantic similarity matching against resumes.

CRITICAL RULES:
- PRESERVE every single: required skill, technology, framework, tool, certification, qualification, experience level, and responsibility
- REMOVE company boilerplate, benefits, equal opportunity statements, and generic phrases
- Compress requirements into concise keyword-dense phrases
- The output should be roughly 100-200 words — compact but retaining ALL matchable requirements
- Output ONLY the summary text, nothing else

Job Description:
{text[:3000]}"""

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.05,
            max_tokens=400
        )
        summary = response.choices[0].message.content.strip()
        logger.info(f"Pre-embedding {text_type} summary: {len(text)} chars → {len(summary)} chars")
        return summary
    except Exception as e:
        logger.error(f"Pre-embedding summarization failed for {text_type}: {e}")
        return text[:2000]

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
