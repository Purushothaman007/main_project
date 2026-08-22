import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_oversized_source_code():
    big_code = "x = 1\n" + ("# comment\n" * 15000)  # Exceeds 100KB
    payload = {
        "language": "python",
        "code": big_code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "SYSTEM_ERROR"
    assert "exceeds limit" in data["stderr"]

def test_oversized_stdin():
    big_stdin = "a" * (settings.MAX_STDIN_SIZE_BYTES + 100)
    payload = {
        "language": "python",
        "code": "print('hi')",
        "stdin": big_stdin
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "SYSTEM_ERROR"
    assert "exceeds limit" in data["stderr"]

def test_output_limit_exceeded():
    code = """
import sys
for _ in range(200000):
    sys.stdout.write("A" * 100 + "\\n")
"""
    payload = {
        "language": "python",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] in ["OUTPUT_LIMIT_EXCEEDED", "TIME_LIMIT_EXCEEDED"]

def test_python_memory_limit():
    # Attempt to allocate 500MB bytearray (Memory limit is 256MB)
    code = "x = bytearray(500 * 1024 * 1024)"
    payload = {
        "language": "python",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] in ["MEMORY_LIMIT_EXCEEDED", "RUNTIME_ERROR"]

def test_cpp_memory_limit():
    # Attempt to allocate and write to 500MB array (Memory limit is 256MB)
    # Using volatile prevents GCC -O2 from optimizing away the loop
    code = """
#include <iostream>
int main() {
    long long size = 500LL * 1024 * 1024;
    volatile char* p = new char[size];
    for (long long i = 0; i < size; i += 4096) {
        p[i] = 1;
    }
    return 0;
}
"""
    payload = {
        "language": "cpp",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] in ["MEMORY_LIMIT_EXCEEDED", "RUNTIME_ERROR"]

def test_cpp_timeout_limit():
    code = "int main() { while(true); return 0; }"
    payload = {
        "language": "cpp",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "TIME_LIMIT_EXCEEDED"
