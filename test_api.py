import requests
import json
import glob
import os

pdf_files = glob.glob("data/**/*.pdf", recursive=True)
if not pdf_files:
    # Also try resumes_raw_pdf since notebook referenced it
    pdf_files = glob.glob("../data/**/*.pdf", recursive=True)
    if not pdf_files:
        print("No PDFs found to test with.")
        exit(1)

test_pdf = pdf_files[0]
print(f"Testing with: {test_pdf}")

url = "http://127.0.0.1:8081/api/user/analyze"
job_description = "We are looking for a Software Engineer with Python and Machine Learning skills to work on GenAI projects."

with open(test_pdf, "rb") as f:
    files = {"resume": (os.path.basename(test_pdf), f, "application/pdf")}
    data = {"job_description": job_description}
    print("Sending POST request to /api/user/analyze...")
    response = requests.post(url, files=files, data=data)

print(f"Status Code: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)
