import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_execution_health_endpoint():
    response = client.get("/health/execution")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "docker_reachable" in data
    assert "images" in data
