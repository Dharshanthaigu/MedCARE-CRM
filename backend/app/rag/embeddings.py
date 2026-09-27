"""
STAGE ii — RETRIEVAL (embedding half)

Default: HashingEmbedder — pure Python + numpy, no downloads, works
immediately. Optional upgrade: SentenceTransformerEmbedder (real neural
embeddings, needs `pip install sentence-transformers`).
"""

import hashlib
import os
import re
from abc import ABC, abstractmethod
from typing import List

import numpy as np

from app.config import EMBEDDING_DIM

_WORD_RE = re.compile(r"[a-zA-Z0-9]+")


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        ...


class HashingEmbedder(Embedder):
    def __init__(self, dim: int = EMBEDDING_DIM):
        self.dim = dim

    def _embed_one(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        words = _WORD_RE.findall(text.lower())
        for word in words:
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h // self.dim) % 2 == 0 else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_one(t) for t in texts]


class SentenceTransformerEmbedder(Embedder):
    _model = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if SentenceTransformerEmbedder._model is None:
            from sentence_transformers import SentenceTransformer
            SentenceTransformerEmbedder._model = SentenceTransformer(model_name)
        self.model = SentenceTransformerEmbedder._model

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


_embedder_instance = None


def get_embedder() -> Embedder:
    global _embedder_instance
    if _embedder_instance is not None:
        return _embedder_instance

    provider = os.getenv("EMBEDDING_PROVIDER", "hashing").lower()
    if provider == "sentence_transformers":
        _embedder_instance = SentenceTransformerEmbedder()
    else:
        _embedder_instance = HashingEmbedder()
    return _embedder_instance