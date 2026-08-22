import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_empty_code_submission():
    payload = {
        "language": "python",
        "code": "",
        "stdin": ""
    }
    response = client.post("/api/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "COMPLETED"
    assert data["stdout"] == ""

def test_concurrent_executions_isolated():
    # Submit 4 distinct code execution requests simultaneously to verify container isolation
    requests_data = [
        {"language": "python", "code": "print('TASK_1')", "expected": "TASK_1"},
        {"language": "java", "code": "public class Main { public static void main(String[] a) { System.out.println(\"TASK_2\"); } }", "expected": "TASK_2"},
        {"language": "cpp", "code": "#include <iostream>\nint main() { std::cout << \"TASK_3\"; return 0; }", "expected": "TASK_3"},
        {"language": "python", "code": "print('TASK_4')", "expected": "TASK_4"},
    ]

    def make_request(req):
        payload = {"language": req["language"], "code": req["code"], "stdin": ""}
        res = client.post("/api/v1/execute", json=payload)
        return req["expected"], res.json()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(make_request, req) for req in requests_data]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    execution_ids = set()
    for expected_str, resp in results:
        assert resp["success"] is True
        assert resp["status"] == "COMPLETED"
        assert expected_str in resp["stdout"]
        execution_ids.add(resp["execution_id"])

    # Ensure every concurrent execution generated a unique execution_id
    assert len(execution_ids) == 4
