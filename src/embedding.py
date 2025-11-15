# src/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

_MODEL = None

def get_embedding_model(name: str = "all-MiniLM-L6-v2"):
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(name)
    return _MODEL

def embed_texts(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    model = get_embedding_model(model_name)
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = a / (np.linalg.norm(a) + 1e-12)
    b_norm = b / (np.linalg.norm(b) + 1e-12)
    return float(np.dot(a_norm, b_norm))
