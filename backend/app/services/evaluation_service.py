import json
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.models.evaluation import Evaluation
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse, EvaluationResult, EvaluationSummary
from app.services.embedding_service import get_embedding_service
from app.services.gemini_service import GeminiService
from app.services.groq_service import GroqService
from app.services.similarity_service import SimilarityService
from app.utils.text import extract_concepts, grammar_signal, tokenize


class EvaluationService:
    def __init__(self) -> None:
        self.settings = get_settings()
        embeddings = get_embedding_service()
        self.similarity_service = SimilarityService(embeddings)
        self.groq_service = GroqService()
        self.gemini_service = GeminiService()

    def evaluate_and_store(self, db: Session, payload: EvaluationRequest) -> EvaluationResponse:
        semantic_similarity = self.similarity_service.cosine_similarity(
            payload.reference_answer,
            payload.student_answer,
        )
        result = self._evaluate_with_configured_provider(payload, semantic_similarity)
        if result is None and self.settings.allow_local_fallback:
            result = self._deterministic_evaluation(payload, semantic_similarity)
        if result is None:
            raise RuntimeError(
                f"{self.settings.normalized_provider.upper()} evaluation is not configured or failed. "
                "Set a valid API key or enable ALLOW_LOCAL_FALLBACK=true."
            )

        record = Evaluation(
            question=payload.question,
            reference_answer=payload.reference_answer,
            student_answer=payload.student_answer,
            subject=payload.subject,
            difficulty=payload.difficulty,
            rubric=payload.rubric,
            result_json=result.model_dump_json(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return self._to_response(record)

    def _evaluate_with_configured_provider(
        self,
        payload: EvaluationRequest,
        semantic_similarity: float,
    ) -> EvaluationResult | None:
        provider = self.settings.normalized_provider
        if provider == "groq":
            if not self.groq_service.is_enabled():
                return None
            return self.groq_service.evaluate(payload, semantic_similarity)
        if provider == "gemini":
            if not self.gemini_service.is_enabled():
                return None
            result = self.gemini_service.evaluate(payload, semantic_similarity)
            return result
        if provider == "local":
            return self._deterministic_evaluation(payload, semantic_similarity)
        raise RuntimeError(f"Unsupported LLM_PROVIDER '{self.settings.llm_provider}'. Use groq, gemini, or local.")

    def list_history(self, db: Session) -> list[EvaluationSummary]:
        records = db.query(Evaluation).order_by(Evaluation.created_at.desc()).all()
        summaries = []
        for record in records:
            result = EvaluationResult(**json.loads(record.result_json))
            summaries.append(
                EvaluationSummary(
                    id=record.id,
                    question=record.question,
                    subject=record.subject,
                    difficulty=record.difficulty,
                    rubric=record.rubric,
                    overall_score=result.overall_score,
                    created_at=record.created_at,
                )
            )
        return summaries

    def get_evaluation(self, db: Session, evaluation_id: int) -> EvaluationResponse | None:
        record = db.get(Evaluation, evaluation_id)
        return self._to_response(record) if record else None

    def delete_evaluation(self, db: Session, evaluation_id: int) -> bool:
        record = db.get(Evaluation, evaluation_id)
        if record is None:
            return False
        db.delete(record)
        db.commit()
        return True

    def _deterministic_evaluation(self, payload: EvaluationRequest, semantic_similarity: float) -> EvaluationResult:
        reference_concepts = extract_concepts(payload.reference_answer, limit=14)
        student_tokens = set(tokenize(payload.student_answer))

        correct = [
            concept for concept in reference_concepts
            if any(part.lower() in student_tokens for part in concept.split())
        ]
        missing = [concept for concept in reference_concepts if concept not in correct]
        student_concepts = extract_concepts(payload.student_answer, limit=10)
        reference_tokens = set(tokenize(payload.reference_answer))
        incorrect = [
            concept for concept in student_concepts
            if all(part.lower() not in reference_tokens for part in concept.split())
        ][:5]

        coverage = len(correct) / max(len(reference_concepts), 1)
        grammar = grammar_signal(payload.student_answer)
        correctness = round((semantic_similarity * 70) + (coverage * 30))
        completeness = round((coverage * 75) + (semantic_similarity * 25))
        relevance = round(semantic_similarity * 100)
        clarity = round((grammar * 0.55) + (min(len(tokenize(payload.student_answer)) / 60, 1) * 45))
        overall = round(
            correctness * 0.34
            + completeness * 0.24
            + relevance * 0.18
            + clarity * 0.12
            + grammar * 0.12
        )

        strengths = []
        if correct:
            strengths.append(f"Addresses key concepts such as {', '.join(correct[:3])}.")
        if semantic_similarity >= 0.7:
            strengths.append("Maintains strong semantic alignment with the reference answer.")
        if grammar >= 80:
            strengths.append("Communicates the response clearly.")
        if not strengths:
            strengths.append("The answer attempts to respond to the question.")

        weaknesses = []
        if missing:
            weaknesses.append(f"Omits important concepts including {', '.join(missing[:3])}.")
        if incorrect:
            weaknesses.append(f"Includes unsupported or potentially incorrect ideas such as {', '.join(incorrect[:2])}.")
        if grammar < 75:
            weaknesses.append("The wording can be made clearer and more polished.")

        suggestions = [f"Add a clear explanation of {concept}." for concept in missing[:3]]
        if incorrect:
            suggestions.append("Remove or correct claims that are not supported by the reference answer.")
        suggestions.append("Use a concise final sentence that directly answers the question.")

        feedback = (
            "The answer is strong and mostly complete."
            if overall >= 80
            else "The answer shows partial understanding but needs more complete coverage of the reference concepts."
            if overall >= 55
            else "The answer needs significant improvement to match the expected response."
        )

        return EvaluationResult(
            overall_score=max(0, min(100, overall)),
            correctness=max(0, min(100, correctness)),
            completeness=max(0, min(100, completeness)),
            relevance=max(0, min(100, relevance)),
            clarity=max(0, min(100, clarity)),
            grammar=max(0, min(100, grammar)),
            confidence_score=max(40, min(96, round((semantic_similarity * 65) + (coverage * 25) + 10))),
            semantic_similarity=round(semantic_similarity, 3),
            correct_concepts=correct,
            missing_concepts=missing,
            incorrect_concepts=incorrect,
            strengths=strengths,
            weaknesses=weaknesses,
            grammar_feedback="Grammar and clarity are acceptable." if grammar >= 80 else "Improve sentence structure, punctuation, and precision.",
            feedback=feedback,
            suggestions=suggestions,
            model_explanation="Scores combine embedding similarity, reference concept coverage, clarity, and grammar signals. Gemini was not used for this response.",
        )

    @staticmethod
    def _to_response(record: Evaluation) -> EvaluationResponse:
        return EvaluationResponse(
            id=record.id,
            question=record.question,
            reference_answer=record.reference_answer,
            student_answer=record.student_answer,
            subject=record.subject,
            difficulty=record.difficulty,
            rubric=record.rubric,
            result=EvaluationResult(**json.loads(record.result_json)),
            created_at=record.created_at,
        )
