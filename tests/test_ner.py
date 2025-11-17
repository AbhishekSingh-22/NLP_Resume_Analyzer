import sys
sys.path.append("..")

from src.ner import extract_resume_entities

skills = ["python","machine learning","docker","react", "sql"]

result = extract_resume_entities(text, skills)
result
