# Resume NLP Analyzer

An AI-powered application that evaluates and scores candidates' resumes against job descriptions. It uses a combination of modern Natural Language Processing (NLP), Named Entity Recognition (NER), Language Model extraction, and semantic embeddings to generate highly accurate compatibility scores and feedback.

The application serves two primary user bases:
- **Candidate Portal**: Allows individuals to upload a single resume, provide a job description, and receive instant feedback on their fit score, skill matching, and missing requirements.
- **HR Dashboard**: Enables recruiters to upload a ZIP file containing multiple resumes to bulk analyze candidates against a target Job Description and instantly generate a ranked leaderboard.

## Project Architecture

The architecture relies on a **FastAPI** backend that acts as a pipeline to sequentially process and evaluate documents via multiple AI-assisted stages, and a **React (Vite)** frontend that connects with these APIs to provide interactive dashboards.

### ML Processing Pipeline (Backend)
1. **Extraction (`services/extraction.py`)**: Parses uploaded PDF resumes to extract clean text, hyperlinks, and first-page summaries.
2. **NLP & NER Processing (`services/nlp_ner.py`)**: Identifies the candidate's name, contact information, and exact keyword overlap using specialized NER capabilities.
3. **LLM Summarization (`services/llm_summary.py`)**: Cleans and condenses both the resume and the Job Description into pure professional contexts using Groq LLM to remove unstructured noise.
4. **Embeddings (`services/embeddings.py`)**: Uses a BERT-based model to evaluate deep contextual and semantic similarity between the condensed resume and the Job Description.
5. **Skill Compatibility & Feedback (`services/llm_summary.py`)**: Employs an LLM to reason about "transferable skills" and construct specific, human-readable feedback.
6. **Scoring (`services/scoring.py`)**: Computes an empirically tuned final "Fit Score" that blends semantic vector matching, keyword overlaps, and LLM logical compatibility.

## Prerequisites
- **Python 3.8+**
- **Node.js 18+**

## Installation and Setup

### 1. Backend (FastAPI)
Navigate to the root directory `resume-nlp` and set up the Python environment:

```bash
# Create and activate a virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

Environment Setup:
- Ensure you have configured any required API keys (e.g., your Groq API key) within the `.env` file at the root. You can refer to `.env.sample`.

### 2. Frontend (React + Vite)
Open a new terminal, navigate to the frontend directory, and install npm packages:

```bash
cd src/frontend
npm install
```

## Running the Application

To run the application, you will need two separate terminal windows.

### Start the Backend
From the root directory with your virtual environment activated:
```bash
uvicorn src.backend.main:app --reload
```
*The backend API will run at `http://localhost:8000`. You can test endpoints dynamically at `http://localhost:8000/docs`.*

### Start the Frontend
From the `src/frontend` directory:
```bash
npm run dev
```
*The frontend interface will run locally at `http://localhost:5173`.*
