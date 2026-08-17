import logging
from functools import lru_cache

import numpy as np

from app.config.settings import get_settings
from app.utils.text import tokenize

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        if self.settings.enable_sentence_transformers:
            self._load_model()

    def _load_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.settings.embedding_model)
        except Exception as exc:
            logger.warning("SentenceTransformer unavailable, falling back to lexical vectors: %s", exc)
            self._model = None

    def embed(self, text: str) -> np.ndarray:
        if self._model is not None:
            return np.array(self._model.encode(text), dtype=float)
        return self._lexical_vector(text)

    @staticmethod
    def _lexical_vector(text: str, dimensions: int = 384) -> np.ndarray:
        vector = np.zeros(dimensions, dtype=float)
        for token in tokenize(text):
            vector[hash(token) % dimensions] += 1.0
        norm = np.linalg.norm(vector)
        return vector / norm if norm else vector


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
