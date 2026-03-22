import re
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# ─── Regex patterns ───
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"\+?\d[\d\-\s]{7,}\d"
LINKEDIN_REGEX = r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-/%]+"
GITHUB_REGEX = r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_]+"

# ─── Expanded Skills Vocabulary ───
SKILLS_VOCAB = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "dart", "perl",
    "lua", "haskell", "elixir", "clojure", "shell", "bash", "powershell",
    # Web Frameworks & Libraries
    "react", "react.js", "reactjs", "angular", "vue", "vue.js", "vuejs", "next.js",
    "nextjs", "nuxt.js", "svelte", "django", "flask", "fastapi", "express",
    "express.js", "spring", "spring boot", "asp.net", ".net", "rails", "ruby on rails",
    "laravel", "gin", "fiber", "nest.js", "nestjs", "remix", "gatsby",
    # Frontend Technologies
    "html", "css", "sass", "scss", "less", "tailwindcss", "tailwind", "bootstrap",
    "material ui", "chakra ui", "styled components", "webpack", "vite", "babel",
    "jquery", "redux", "zustand", "mobx", "graphql", "rest api", "restful",
    # Mobile Development
    "react native", "flutter", "android", "ios", "swiftui", "jetpack compose",
    "xamarin", "ionic", "cordova",
    # Databases
    "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "cassandra",
    "dynamodb", "firebase", "firestore", "sqlite", "oracle", "mariadb", "neo4j",
    "elasticsearch", "couchdb", "influxdb", "supabase",
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "heroku",
    "digitalocean", "vercel", "netlify", "cloudflare", "docker", "kubernetes",
    "k8s", "terraform", "ansible", "jenkins", "ci/cd", "github actions",
    "gitlab ci", "circleci", "nginx", "apache", "linux", "unix",
    # Data Science & ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "opencv",
    "spacy", "hugging face", "huggingface", "transformers", "bert", "gpt",
    "llm", "large language models", "generative ai", "gen ai", "langchain",
    "rag", "retrieval augmented generation", "xgboost", "lightgbm", "catboost",
    "random forest", "neural network", "cnn", "rnn", "lstm", "gan",
    "reinforcement learning", "feature engineering", "data wrangling",
    # Data Engineering & BI
    "spark", "apache spark", "pyspark", "hadoop", "hive", "kafka",
    "apache kafka", "airflow", "apache airflow", "dbt", "etl", "data pipeline",
    "data warehouse", "snowflake", "bigquery", "redshift", "databricks",
    "tableau", "power bi", "looker", "metabase",
    # AI & APIs
    "openai", "gemini", "anthropic", "claude", "groq", "ollama",
    "chatgpt", "prompt engineering", "fine-tuning", "embeddings",
    "vector database", "pinecone", "weaviate", "chromadb", "faiss", "milvus",
    # Tools & Practices
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "notion",
    "figma", "postman", "swagger", "agile", "scrum", "kanban",
    "test driven development", "tdd", "unit testing", "integration testing",
    "selenium", "cypress", "jest", "pytest", "mocha",
    # Networking & Security
    "networking", "tcp/ip", "http", "https", "websocket", "oauth",
    "jwt", "ssl", "tls", "encryption", "cybersecurity", "penetration testing",
    # Soft Skills (commonly looked for in JDs)
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "project management", "time management",
]

_NER_PIPELINE = None

def get_ner_pipeline():
    global _NER_PIPELINE
    if _NER_PIPELINE is None:
        model_name = "Davlan/xlm-roberta-base-ner-hrl"
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForTokenClassification.from_pretrained(model_name)
            _NER_PIPELINE = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
        except Exception as e:
            logger.error(f"Failed to load XLM-RoBERTa NER model: {e}")
    return _NER_PIPELINE


def extract_contact_info(text: str, hyperlinks: List[str] = None) -> Dict[str, Any]:
    """
    Extract contact info from both visible text AND embedded PDF hyperlinks.
    """
    all_text = text
    if hyperlinks:
        all_text += "\n" + "\n".join(hyperlinks)

    emails = re.findall(EMAIL_REGEX, all_text)
    phones = re.findall(PHONE_REGEX, text)  # phones only from text, not URLs

    # Search for LinkedIn/GitHub in both text and hyperlinks
    linkedin_matches = re.findall(LINKEDIN_REGEX, all_text)
    github_matches = re.findall(GITHUB_REGEX, all_text)

    # Also check raw hyperlinks for exact matches
    linkedin_url = None
    github_url = None
    if hyperlinks:
        for link in hyperlinks:
            if "linkedin.com" in link.lower() and not linkedin_url:
                linkedin_url = link
            if "github.com" in link.lower() and not github_url:
                github_url = link

    if not linkedin_url and linkedin_matches:
        linkedin_url = "".join(linkedin_matches[0]) if isinstance(linkedin_matches[0], tuple) else linkedin_matches[0]
    if not github_url and github_matches:
        github_url = "".join(github_matches[0]) if isinstance(github_matches[0], tuple) else github_matches[0]

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0].strip() if phones else None,
        "linkedin": linkedin_url,
        "github": github_url,
        "contact_status": "found" if (emails or phones or linkedin_url) else "missing"
    }


def extract_primary_name(first_page_text: str) -> str:
    """Use the full first page for NER to find the candidate's name."""
    ner_pipe = get_ner_pipeline()
    if not ner_pipe:
        return ""

    try:
        entities = ner_pipe(first_page_text[:3000])  # First page is usually < 3000 chars
        for ent in entities:
            if ent['entity_group'] == 'PER':
                name = ent['word'].strip()
                if len(name) > 2 and not re.search(r'\d', name):
                    return name
    except Exception as e:
        logger.error(f"NER extraction failed: {e}")
    return ""


def extract_skills(text: str, skills_vocab: List[str] = None) -> List[str]:
    """Match skills from the expanded vocabulary against the resume text."""
    if skills_vocab is None:
        skills_vocab = SKILLS_VOCAB

    text_lower = text.lower()
    found_skills = []
    for skill in skills_vocab:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return sorted(set(found_skills))


def match_jd_skills(jd_text: str, resume_skills: List[str]) -> Dict[str, List[str]]:
    """
    Extract skills from the JD, then compare against resume skills.
    Returns matched and missing skills relative to JD requirements.
    """
    jd_skills = extract_skills(jd_text)
    resume_skills_lower = {s.lower() for s in resume_skills}

    matched = [s for s in jd_skills if s.lower() in resume_skills_lower]
    missing = [s for s in jd_skills if s.lower() not in resume_skills_lower]

    return {
        "jd_skills": jd_skills,
        "matched": matched,
        "missing": missing
    }


def process_resume_text(
    full_text: str,
    first_page_text: str,
    hyperlinks: List[str] = None,
    job_description: str = None
) -> Dict[str, Any]:
    """
    Full NER pipeline. Uses:
    - first_page_text for name extraction (NER) and embedding input
    - full_text for skill extraction
    - hyperlinks for contact info (GitHub/LinkedIn from PDF metadata)
    """
    contacts = extract_contact_info(full_text, hyperlinks)
    name = extract_primary_name(first_page_text)
    skills = extract_skills(full_text)

    result = {
        "name": name,
        "contacts": contacts,
        "skills": skills,
        "first_page_text": first_page_text,
        "full_text_length": len(full_text),
    }

    if job_description:
        result["jd_match"] = match_jd_skills(job_description, skills)

    return result
