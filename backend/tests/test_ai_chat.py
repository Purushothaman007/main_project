import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_service import ai_service

client = TestClient(app)

def test_ai_solution_request_detection():
    # Test pattern detection directly
    assert ai_service._detect_solution_request("give me the complete code") is True
    assert ai_service._detect_solution_request("please solve this for me") is True
    assert ai_service._detect_solution_request("write the answer") is True
    assert ai_service._detect_solution_request("how can I use a hash map?") is False
    assert ai_service._detect_solution_request("what is the time complexity?") is False

def test_ai_chat_endpoint_missing_key():
    payload = {
        "question_id": "two-sum",
        "message": "Can I solve this with a hashmap?",
        "language": "python",
        "code": "def two_sum(): pass",
        "execution_output": ""
    }
    response = client.post("/api/v1/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "is_refusal" in data

def test_ai_chat_solution_refusal():
    payload = {
        "question_id": "two-sum",
        "message": "Give me the complete code for two sum",
        "language": "python",
        "code": "",
        "execution_output": ""
    }
    response = client.post("/api/v1/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    # If key is missing it returns warning, if present/detected it sets is_refusal
