from fastapi import APIRouter

from app.controllers.evaluation_controller import (
    create_evaluation,
    delete_evaluation,
    get_evaluation,
    list_history,
)
from app.schemas.evaluation import EvaluationResponse, EvaluationSummary

router = APIRouter(tags=["Evaluations"])

router.add_api_route("/evaluate", create_evaluation, methods=["POST"], response_model=EvaluationResponse)
router.add_api_route("/history", list_history, methods=["GET"], response_model=list[EvaluationSummary])
router.add_api_route("/evaluation/{evaluation_id}", get_evaluation, methods=["GET"], response_model=EvaluationResponse)
router.add_api_route("/history/{evaluation_id}", delete_evaluation, methods=["DELETE"], status_code=204)
