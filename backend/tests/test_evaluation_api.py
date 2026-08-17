import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENABLE_SENTENCE_TRANSFORMERS"] = "false"
os.environ["LLM_PROVIDER"] = "local"
os.environ["ALLOW_LOCAL_FALLBACK"] = "true"

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_evaluate_creates_result() -> None:
    response = client.post(
        "/evaluate",
        json={
            "question": "Explain binary search.",
            "reference_answer": "Binary search finds an item in a sorted array by repeatedly dividing the search interval in half. It runs in O(log n).",
            "student_answer": "Binary search works on sorted arrays and halves the search space, so it is efficient.",
            "subject": "Computer Science",
            "difficulty": "Medium",
            "rubric": "Balanced",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert 0 <= data["result"]["overall_score"] <= 100
    assert "semantic_similarity" in data["result"]


def test_history_and_delete() -> None:
    created = client.post(
        "/evaluate",
        json={
            "question": "What is photosynthesis?",
            "reference_answer": "Photosynthesis converts light energy into chemical energy in plants using carbon dioxide and water to produce glucose and oxygen.",
            "student_answer": "Plants use light to make food and oxygen.",
        },
    ).json()

    history = client.get("/history")
    assert history.status_code == 200
    assert len(history.json()) == 1

    deleted = client.delete(f"/history/{created['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/evaluation/{created['id']}").status_code == 404


def test_validation_rejects_short_question() -> None:
    response = client.post(
        "/evaluate",
        json={
            "question": "Why?",
            "reference_answer": "A valid reference answer with enough detail.",
            "student_answer": "A valid student answer.",
        },
    )

    assert response.status_code == 422


def test_get_evaluation_returns_full_saved_payload() -> None:
    created = client.post(
        "/evaluate",
        json={
            "question": "Explain the role of mitochondria in a cell.",
            "reference_answer": "Mitochondria generate ATP through cellular respiration and provide usable energy for cellular processes.",
            "student_answer": "Mitochondria make ATP energy for the cell through respiration.",
            "subject": "Biology",
            "difficulty": "Easy",
            "rubric": "Strict",
        },
    ).json()

    response = client.get(f"/evaluation/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Biology"
    assert data["difficulty"] == "Easy"
    assert data["rubric"] == "Strict"
    assert data["result"]["overall_score"] == created["result"]["overall_score"]


def test_empty_student_answer_is_rejected() -> None:
    response = client.post(
        "/evaluate",
        json={
            "question": "Explain photosynthesis.",
            "reference_answer": "Photosynthesis uses sunlight, carbon dioxide, and water to produce glucose and oxygen.",
            "student_answer": "",
        },
    )

    assert response.status_code == 422
