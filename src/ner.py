# src/ner.py
import re
import spacy
from spacy.matcher import PhraseMatcher
from typing import Dict, List, Any

# Lazy global NLP model
_NLP = None

def get_nlp(model_name: str = "en_core_web_sm"):
    """Lazy-load spaCy model once."""
    global _NLP
    if _NLP is None:
        _NLP = spacy.load(model_name, disable=["parser"])
    return _NLP


# -----------------------------
# REGEX EXTRACTORS
# -----------------------------

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"\+?\d[\d\-\s]{7,}\d"
LINKEDIN_REGEX = r"(https?://)?(www\.)?linkedin\.com/[A-Za-z0-9\-/]+"
GITHUB_REGEX = r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_]+"


def extract_regex_entities(text: str) -> Dict[str, List[str]]:
    """Extract email, phone, LinkedIn, GitHub using regex."""
    return {
        "email": re.findall(EMAIL_REGEX, text),
        "phone": re.findall(PHONE_REGEX, text),
        "linkedin": re.findall(LINKEDIN_REGEX, text),
        "github": re.findall(GITHUB_REGEX, text),
    }


# -----------------------------
# SKILL EXTRACTION
# -----------------------------

def build_skill_matcher(nlp, skills: List[str]) -> PhraseMatcher:
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in skills]
    matcher.add("SKILLS", patterns)
    return matcher


def extract_skills(text: str, skills_vocab: List[str]) -> List[str]:
    nlp = get_nlp()
    matcher = build_skill_matcher(nlp, skills_vocab)
    doc = nlp(text)

    found = set()
    for _, start, end in matcher(doc):
        found.add(doc[start:end].text.lower())

    return sorted(found)


# -----------------------------
# SPACY NER
# -----------------------------

def extract_spacy_entities(text: str) -> Dict[str, List[str]]:
    nlp = get_nlp()
    doc = nlp(text)

    ents: Dict[str, List[str]] = {}
    for ent in doc.ents:
        ents.setdefault(ent.label_, []).append(ent.text)
    return ents


# -----------------------------
# FULL ENTITY EXTRACTION PIPELINE
# -----------------------------

def extract_resume_entities(
    text: str,
    skills_vocab: List[str]
) -> Dict[str, Any]:
    """
    Full NER for a single resume.
    Combines: regex, spaCy NER, skill extraction.
    """

    return {
        "regex": extract_regex_entities(text),
        "spacy": extract_spacy_entities(text),
        "skills": extract_skills(text, skills_vocab),
    }
