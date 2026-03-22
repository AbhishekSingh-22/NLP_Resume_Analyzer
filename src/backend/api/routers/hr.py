from fastapi import APIRouter, File, UploadFile, Form, HTTPException
import zipfile
import io
import logging
from src.backend.services.extraction import extract_all_from_pdf
from src.backend.services.nlp_ner import process_resume_text
from src.backend.services.embeddings import generate_embedding
from src.backend.services.scoring import calculate_fit_score
from src.backend.services.llm_summary import get_candidate_feedback

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/bulk-analyze")
async def bulk_analyze_resumes(
    zip_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not zip_file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Must upload a ZIP file containing PDFs.")
    
    try:
        jd_emb = generate_embedding(job_description)
        zip_bytes = await zip_file.read()
        
        results = []
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for file_name in z.namelist():
                if file_name.lower().endswith(".pdf") and not file_name.startswith("__MACOSX"):
                    pdf_bytes = z.read(file_name)
                    
                    extracted = extract_all_from_pdf(pdf_bytes)
                    if not extracted["full_text"]:
                        continue
                    
                    parsed_data = process_resume_text(
                        full_text=extracted["full_text"],
                        first_page_text=extracted["first_page_text"],
                        hyperlinks=extracted["hyperlinks"],
                        job_description=job_description
                    )
                    
                    emb_text = (parsed_data.get("name") or "") + "\n" + extracted["first_page_text"]
                    resume_emb = generate_embedding(emb_text)
                    fit_score = calculate_fit_score(resume_emb, jd_emb, parsed_data)
                    
                    jd_match = parsed_data.get("jd_match", {})
                    feedback = get_candidate_feedback(
                        text=extracted["full_text"],
                        fit_score=fit_score,
                        job_description=job_description,
                        matched_skills=jd_match.get("matched", []),
                        missing_skills=jd_match.get("missing", []),
                        resume_skills=parsed_data.get("skills", [])
                    )
                    
                    results.append({
                        "filename": file_name,
                        "candidate_name": parsed_data.get("name") or file_name,
                        "fit_score": fit_score,
                        "contacts": parsed_data.get("contacts"),
                        "jd_match": jd_match,
                        "feedback": feedback
                    })
        
        results.sort(key=lambda x: x["fit_score"], reverse=True)
        return {"leaderboard": results}
        
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file.")
    except Exception as e:
        logger.error(f"Error processing bulk batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))
