import os
import docker
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
docker_client = docker.from_env()

def test_container_network_isolation():
    # Attempting to fetch an external website inside Python container must fail
    code = """
import socket
try:
    s = socket.create_connection(("8.8.8.8", 53), timeout=2)
    print("NETWORK_CONNECTED")
except Exception as e:
    print("NETWORK_DISABLED")
"""
    payload = {
        "language": "python",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "NETWORK_DISABLED" in data["stdout"]
    assert "NETWORK_CONNECTED" not in data["stdout"]

def test_non_root_execution():
    # Verify process runs under UID 1000 (sandbox user), not root (UID 0)
    code = """
import os
print(f"UID:{os.getuid()}")
"""
    payload = {
        "language": "python",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "UID:1000" in data["stdout"]

def test_no_host_path_leakage_in_errors():
    # Generate compilation and runtime errors and ensure host paths are not exposed
    payload = {
        "language": "cpp",
        "code": "int main() { return error; }",
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPILATION_ERROR"
    # Ensure Windows user host path is NOT leaked
    assert "c:\\users" not in data["stderr"].lower()
    assert "c:/users" not in data["stderr"].lower()

def test_container_and_workspace_cleanup():
    # Capture initial container count
    initial_containers = len(docker_client.containers.list(all=True))

    payload = {
        "language": "python",
        "code": "print('Cleanup Test')",
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify no container was left orphaned after request completed
    final_containers = len(docker_client.containers.list(all=True))
    assert final_containers == initial_containers
