import json
import os

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EMBEDDINGS_PATH = os.path.join(DATA_DIR, "embeddings.npy")
NAMES_PATH = os.path.join(DATA_DIR, "names.json")

# Cosine similarity threshold — scores below this are treated as "unknown"
MATCH_THRESHOLD = 0.35


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def load_database():
    """
    Load precomputed embeddings and names from disk.
    Returns (embeddings: ndarray shape (N,512), names: list[str]).
    Call once at startup and keep the result in memory.
    """
    if not os.path.exists(EMBEDDINGS_PATH) or not os.path.exists(NAMES_PATH):
        raise FileNotFoundError(
            "Embedding database not found. Run src/embed_database.py first."
        )
    embeddings = np.load(EMBEDDINGS_PATH)          # (N, 512) float32
    with open(NAMES_PATH) as f:
        names = json.load(f)
    return embeddings, names


def find_match(live_embedding, db_embeddings, db_names):
    """
    Compare a single live face embedding against the full database.

    Returns (name: str, score: float).
    name is "Unknown" when the best score is below MATCH_THRESHOLD.
    """
    # Normalise both sides then do a single matrix multiply — fast even for 100s of entries
    live_norm = live_embedding / (np.linalg.norm(live_embedding) + 1e-10)
    db_norms = db_embeddings / (np.linalg.norm(db_embeddings, axis=1, keepdims=True) + 1e-10)

    scores = db_norms @ live_norm          # (N,) cosine similarities
    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])

    if best_score < MATCH_THRESHOLD:
        return "Unknown", best_score

    return db_names[best_idx], best_score
