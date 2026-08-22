import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_python_success():
    payload = {
        "language": "python",
        "code": "print('Hello, World!')",
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "COMPLETED"
    assert data["exit_code"] == 0
    assert "Hello, World!" in data["stdout"]
    assert data["stderr"] == ""
    assert data["execution_id"].startswith("exec_")

def test_python_stdin():
    payload = {
        "language": "python",
        "code": "n = int(input())\nprint(n * n)",
        "stdin": "5\n"
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "COMPLETED"
    assert data["exit_code"] == 0
    assert "25" in data["stdout"]

def test_python_runtime_error():
    payload = {
        "language": "python",
        "code": "x = 1 / 0",
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "RUNTIME_ERROR"
    assert data["exit_code"] != 0
    assert "ZeroDivisionError" in data["stderr"]

def test_python_timeout():
    payload = {
        "language": "python",
        "code": "import time\ntime.sleep(10)",
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "TIME_LIMIT_EXCEEDED"

def test_unsupported_language():
    payload = {
        "language": "brainfuck",
        "code": "++++",
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "SYSTEM_ERROR"
