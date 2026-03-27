from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from src.backend.services.extraction import extract_all_from_pdf
from src.backend.services.nlp_ner import process_resume_text
from src.backend.services.embeddings import generate_embedding
from src.backend.services.scoring import calculate_fit_score
from src.backend.services.llm_summary import get_candidate_feedback, summarize_for_embedding, evaluate_skill_compatibility
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        pdf_bytes = await resume.read()
        
        # Stage 1: Extract text + first page + hyperlinks from PDF
        extracted = extract_all_from_pdf(pdf_bytes)
        full_text = extracted["full_text"]
        first_page_text = extracted["first_page_text"]
        hyperlinks = extracted["hyperlinks"]
        
        if not full_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")
        
        # Stage 2: NER, skills, contacts (with hyperlinks and JD matching)
        parsed_data = process_resume_text(
            full_text=full_text,
            first_page_text=first_page_text,
            hyperlinks=hyperlinks,
            job_description=job_description
        )
        
        # Stage 3: Pre-embedding keyword summarization via Groq
        resume_input = (parsed_data.get("name") or "") + "\n" + first_page_text
        resume_summary = summarize_for_embedding(resume_input, text_type="resume")
        jd_summary = summarize_for_embedding(job_description, text_type="job_description")
        
        # ─── Debug: Print summaries to terminal for verification ───
        print("\n" + "="*80)
        print("📄 RESUME SUMMARY (sent to embedding model):")
        print("-"*80)
        print(resume_summary)
        print("\n" + "="*80)
        print("📋 JD SUMMARY (sent to embedding model):")
        print("-"*80)
        print(jd_summary)
        print("="*80 + "\n")
        
        # Stage 4: Embeddings on the summarized text (not raw)
        resume_emb = generate_embedding(resume_summary)
        jd_emb = generate_embedding(jd_summary)
        
        # Stage 5: LLM Skill Compatibility (transferable skills evaluation)
        jd_match = parsed_data.get("jd_match", {})
        llm_compat_score = evaluate_skill_compatibility(
            resume_skills=parsed_data.get("skills", []),
            jd_skills=jd_match.get("jd_skills", []),
            matched_skills=jd_match.get("matched", []),
            missing_skills=jd_match.get("missing", [])
        )
        
        # Stage 6: Scoring (with LLM compatibility)
        fit_score = calculate_fit_score(resume_emb, jd_emb, parsed_data, llm_compat_score)
        
        # Stage 5: LLM Feedback (JD-scoped)
        jd_match = parsed_data.get("jd_match", {})
        feedback = get_candidate_feedback(
            text=full_text,
            fit_score=fit_score,
            job_description=job_description,
            matched_skills=jd_match.get("matched", []),
            missing_skills=jd_match.get("missing", []),
            resume_skills=parsed_data.get("skills", [])
        )
        
        return {
            "candidate_name": parsed_data.get("name") or resume.filename,
            "fit_score": fit_score,
            "contacts": parsed_data.get("contacts"),
            "skills_found": parsed_data.get("skills", []),
            "jd_match": jd_match,
            "feedback": feedback
        }
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))
