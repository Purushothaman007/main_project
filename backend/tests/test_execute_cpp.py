import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cpp_success():
    code = """
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!";
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
    assert data["success"] is True
    assert data["status"] == "COMPLETED"
    assert data["exit_code"] == 0
    assert "Hello, World!" in data["stdout"]
    assert data["stderr"] == ""

def test_cpp_stdin():
    code = """
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << n * n;
    return 0;
}
"""
    payload = {
        "language": "cpp",
        "code": code,
        "stdin": "9\n"
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "COMPLETED"
    assert data["exit_code"] == 0
    assert "81" in data["stdout"]

def test_cpp_compilation_error():
    code = """
#include <iostream>
using namespace std;

int main() {
    cout << "Missing semicolon"
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
    assert data["status"] == "COMPILATION_ERROR"
    assert data["exit_code"] != 0
    assert "error:" in data["stderr"]

def test_cpp_runtime_error():
    code = """
#include <iostream>
using namespace std;

int main() {
    int* ptr = nullptr;
    *ptr = 42; // Segmentation fault
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
    assert data["status"] == "RUNTIME_ERROR"
    assert data["exit_code"] != 0

def test_cpp_timeout():
    code = """
#include <iostream>
using namespace std;

int main() {
    while (true) {
        // Infinite loop
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
    assert data["status"] == "TIME_LIMIT_EXCEEDED"
