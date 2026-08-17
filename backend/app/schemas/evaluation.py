from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EvaluationRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=5000)
    reference_answer: str = Field(..., min_length=5, max_length=10000)
    student_answer: str = Field(..., min_length=1, max_length=10000)
    subject: str = Field(default="General", max_length=80)
    difficulty: str = Field(default="Medium", max_length=40)
    rubric: str = Field(default="Balanced", max_length=80)

    @field_validator("question", "reference_answer", "student_answer", "subject", "difficulty", "rubric")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class CategoryScores(BaseModel):
    correctness: int = Field(..., ge=0, le=100)
    completeness: int = Field(..., ge=0, le=100)
    relevance: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    grammar: int = Field(..., ge=0, le=100)


class EvaluationResult(CategoryScores):
    overall_score: int = Field(..., ge=0, le=100)
    confidence_score: int = Field(..., ge=0, le=100)
    semantic_similarity: float = Field(..., ge=0, le=1)
    correct_concepts: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    incorrect_concepts: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    grammar_feedback: str
    feedback: str
    suggestions: list[str] = Field(default_factory=list)
    model_explanation: str


class EvaluationResponse(BaseModel):
    id: int
    question: str
    reference_answer: str
    student_answer: str
    subject: str
    difficulty: str
    rubric: str
    result: EvaluationResult
    created_at: datetime


class EvaluationSummary(BaseModel):
    id: int
    question: str
    subject: str
    difficulty: str
    rubric: str
    overall_score: int
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str | dict[str, Any]
