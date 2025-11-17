# src/config.py
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
load_dotenv()  # safe: only reads .env in dev


# Project-level directories
ROOT = Path(__file__).resolve().parents[1]  # repo root
DATA_DIR = Path(os.getenv("RESUME_DATA_DIR", ROOT / "data"))
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", ROOT / "artifacts"))

# Hugging Face token (expects you exported it already)
HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN")  # already in your environment per your comment

def require_hf_token():
    if not HF_TOKEN:
        raise EnvironmentError(
            "HUGGING_FACE_TOKEN not set. Export it in your shell or set it in a .env file for local dev."
        )

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
