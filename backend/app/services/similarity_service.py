import numpy as np

from app.services.embedding_service import EmbeddingService


class SimilarityService:
    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service

    def cosine_similarity(self, left: str, right: str) -> float:
        left_vector = self.embedding_service.embed(left)
        right_vector = self.embedding_service.embed(right)
        denominator = np.linalg.norm(left_vector) * np.linalg.norm(right_vector)
        if denominator == 0:
            return 0.0
        return float(max(0.0, min(1.0, np.dot(left_vector, right_vector) / denominator)))
