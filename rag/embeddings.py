"""Embedding pipeline using sentence-transformers."""

import numpy as np

from .config import EMBEDDING_MODEL, EMBEDDING_DEVICE

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL, device=EMBEDDING_DEVICE)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    model = get_model()
    emb = model.encode(text, normalize_embeddings=True)
    return emb.tolist()
