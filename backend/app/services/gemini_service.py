import json
import logging

from app.config.settings import get_settings
from app.schemas.evaluation import EvaluationRequest, EvaluationResult
from app.services.prompt_builder import build_evaluation_prompt

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_enabled(self) -> bool:
        return bool(self.settings.gemini_api_key)

    def evaluate(self, payload: EvaluationRequest, semantic_similarity: float) -> EvaluationResult | None:
        if not self.is_enabled():
            return None
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.settings.gemini_api_key)
            model = genai.GenerativeModel(
                self.settings.gemini_model,
                generation_config={"temperature": 0, "response_mime_type": "application/json"},
            )
            response = model.generate_content(build_evaluation_prompt(payload, semantic_similarity))
            data = json.loads(response.text)
            data["semantic_similarity"] = semantic_similarity
            return EvaluationResult(**data)
        except Exception as exc:
            logger.exception("Gemini evaluation failed; using deterministic evaluator: %s", exc)
            return None
