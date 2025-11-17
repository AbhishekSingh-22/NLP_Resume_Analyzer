# scripts/run_pipeline.py
import argparse
from pathlib import Path
from src.text_extraction import extract_text_from_pdf
from src.ner import extract_entities, extract_skills
from src.embeddings import embed_texts, cosine_similarity
from src.config import ensure_dirs, DATA_DIR

ensure_dirs()

def run_resume_pipeline(pdf_path: str, skills_list: list[str], job_text: str | None = None):
    pdf_path = Path(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    entities = extract_entities(text)
    found_skills = extract_skills(text, skills_list)
    emb_score = 0.0
    if job_text:
        emb = embed_texts([text])[0]
        job_emb = embed_texts([job_text])[0]
        emb_score = cosine_similarity(emb, job_emb)
    return {
        "entities": entities,
        "found_skills": found_skills,
        "emb_score": emb_score
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to resume PDF")
    parser.add_argument("--skills", nargs="+", default=["python", "docker", "react"])
    parser.add_argument("--job", help="Optional job description text file")
    args = parser.parse_args()
    job_text = None
    if args.job:
        job_text = Path(args.job).read_text()
    out = run_resume_pipeline(args.pdf, args.skills, job_text)
    import json
    print(json.dumps(out, indent=2))
