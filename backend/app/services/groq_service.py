import json
import logging
import re

import httpx

from app.config.settings import get_settings
from app.schemas.evaluation import EvaluationRequest, EvaluationResult
from app.services.prompt_builder import SYSTEM_PROMPT, build_evaluation_prompt

logger = logging.getLogger(__name__)

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_enabled(self) -> bool:
        return bool(self.settings.groq_api_key)

    def evaluate(self, payload: EvaluationRequest, semantic_similarity: float) -> EvaluationResult | None:
        if not self.is_enabled():
            return None

        try:
            response = httpx.post(
                GROQ_CHAT_COMPLETIONS_URL,
                headers={
                    "Authorization": f"Bearer {self.settings.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.settings.groq_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": build_evaluation_prompt(payload, semantic_similarity)},
                    ],
                    "temperature": 0,
                    "top_p": 1,
                    "max_completion_tokens": 2048,
                    "response_format": {"type": "json_object"},
                },
                timeout=45,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            data = json.loads(_extract_json(content))
            data["semantic_similarity"] = semantic_similarity
            data["model_explanation"] = (
                f"{data.get('model_explanation', '').strip()} "
                f"Evaluated with Groq model {self.settings.groq_model}."
            ).strip()
            return EvaluationResult(**data)
        except Exception as exc:
            logger.exception("Groq evaluation failed: %s", exc)
            return None


def _extract_json(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned
