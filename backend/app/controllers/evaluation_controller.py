from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse, EvaluationSummary
from app.services.evaluation_service import EvaluationService


def get_evaluation_service() -> EvaluationService:
    return EvaluationService()


def create_evaluation(
    payload: EvaluationRequest,
    db: Session = Depends(get_db),
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationResponse:
    try:
        return service.evaluate_and_store(db, payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


def list_history(
    db: Session = Depends(get_db),
    service: EvaluationService = Depends(get_evaluation_service),
) -> list[EvaluationSummary]:
    return service.list_history(db)


def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationResponse:
    result = service.get_evaluation(db, evaluation_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
    return result


def delete_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    service: EvaluationService = Depends(get_evaluation_service),
) -> Response:
    deleted = service.delete_evaluation(db, evaluation_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
