from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_returns_answer():
    fake_result = {
        "question": "Which property has the highest cap rate?",
        "answer": "The Nashville Short-Term Rental Portfolio has the highest cap rate at 9.4%.",
        "sources_used": 3,
    }

    # Patch where the name is looked up (main.ask_property_question), not where
    # it's defined (rag.ask_property_question) — main.py already bound its own
    # reference to the function at import time via `from rag import ...`.
    with patch("main.ask_property_question", return_value=fake_result) as mock_ask:
        response = client.post("/ask", json={"question": fake_result["question"]})

    assert response.status_code == 200
    assert response.json() == fake_result
    mock_ask.assert_called_once_with(fake_result["question"])


def test_ask_rejects_empty_question():
    with patch("main.ask_property_question", side_effect=ValueError("Question cannot be empty")):
        response = client.post("/ask", json={"question": ""})

    assert response.status_code == 400


def test_ask_missing_question_field_returns_422():
    # No mock needed here — Pydantic rejects the request before the route
    # body even runs, since "question" is a required field on QuestionRequest.
    response = client.post("/ask", json={})
    assert response.status_code == 422


@pytest.mark.integration
def test_ask_end_to_end_against_real_services():
    response = client.post(
        "/ask", json={"question": "Which property has the highest cap rate?"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "Nashville" in body["answer"]
    assert body["sources_used"] > 0
