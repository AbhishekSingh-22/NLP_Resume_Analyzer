from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)

_MODEL = None

def get_embedding_model(model_name: str = "all-mpnet-base-v2"):
    global _MODEL
    if _MODEL is None:
        try:
            _MODEL = SentenceTransformer(model_name)
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {e}")
    return _MODEL

def generate_embedding(text: str) -> np.ndarray:
    model = get_embedding_model()
    if not model or not text.strip():
        # Return empty embedding if model fails or empty text
        return np.zeros(768)
    return model.encode([text], convert_to_numpy=True, show_progress_bar=False)[0]

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    a_norm = a / np.linalg.norm(a)
    b_norm = b / np.linalg.norm(b)
    return float(np.dot(a_norm, b_norm))
