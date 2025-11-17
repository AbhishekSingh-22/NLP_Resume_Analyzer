# src/parse.py
from typing import Dict, Any, List
import re

# stub NER — replace with spaCy or your NER of choice
def parse_basic_fields(text: str) -> Dict[str, Any]:
    """
    Return parsed fields:
      - primary_name, emails, phones, skills(list), orgs(list), preview (short text), education(list)
    This is a rule-based fallback parser. Plug your spaCy/HF NER here later.
    """
    out = {
        "primary_name": None,
        "emails": [],
        "phones": [],
        "skills": [],
        "orgs": [],
        "preview": text[:1200],
        "education": [],
    }
    # email
    out["emails"] = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    # phone (naive)
    out["phones"] = re.findall(r'\+?\d[\d\s\-\(\)]{6,}\d', text)
    # name heuristic: first non-empty line under 5 words
    for line in text.splitlines():
        s=line.strip()
        if s and len(s.split())<=5 and any(ch.isalpha() for ch in s):
            out["primary_name"]=s
            break
    # placeholder skills extraction - you can replace with keyword matching
    skill_candidates = ["python","java","c++","sql","docker","aws","azure","git","pytorch","tensorflow"]
    lower = text.lower()
    out["skills"] = [s for s in skill_candidates if s in lower]
    # orgs: simple heuristics (look for 'Company' words)
    out["orgs"] = re.findall(r'\b[A-Z][A-Za-z0-9&\.\- ]{2,40}(?:Inc|LLC|Ltd|Company|Corporation|Corp|University|College)\b', text)
    return out
