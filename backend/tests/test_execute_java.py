import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_java_success():
    code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""
    payload = {
        "language": "java",
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

def test_java_stdin():
    code = """
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(n * n);
    }
}
"""
    payload = {
        "language": "java",
        "code": code,
        "stdin": "7\n"
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "COMPLETED"
    assert data["exit_code"] == 0
    assert "49" in data["stdout"]

def test_java_compilation_error():
    code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Missing semicolon")
    }
}
"""
    payload = {
        "language": "java",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "COMPILATION_ERROR"
    assert data["exit_code"] != 0
    assert "error:" in data["stderr"] or "';' expected" in data["stderr"]

def test_java_runtime_error():
    code = """
public class Main {
    public static void main(String[] args) {
        int x = 10 / 0;
    }
}
"""
    payload = {
        "language": "java",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "RUNTIME_ERROR"
    assert data["exit_code"] != 0
    assert "ArithmeticException" in data["stderr"]

def test_java_timeout():
    code = """
public class Main {
    public static void main(String[] args) {
        while (true) {
            // Infinite loop
        }
    }
}
"""
    payload = {
        "language": "java",
        "code": code,
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "TIME_LIMIT_EXCEEDED"
