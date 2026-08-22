# Troubleshooting & Diagnostics Guide

## 1. Health Diagnostics Endpoints

### Basic Liveness Check
```bash
curl http://localhost:8000/health
```
**Expected Output:**
```json
{"status": "healthy"}
```

### Docker Daemon & Image Readiness Check
```bash
curl http://localhost:8000/health/execution
```
**Expected Output:**
```json
{
  "status": "healthy",
  "docker_reachable": true,
  "images": {
    "python": true,
    "java": true,
    "cpp": true
  }
}
```

---

## 2. Common Issues & Resolution Steps

### Issue 1: `docker_reachable: false` or `DockerException`
* **Symptom:** API returns `SYSTEM_ERROR` or `/health/execution` shows `docker_reachable: false`.
* **Cause:** Docker Desktop is not running or the Docker daemon socket is unreachable.
* **Fix:**
  1. Open Docker Desktop on Windows.
  2. Verify Docker is running via shell: `docker ps`.
  3. Ensure user account has permission to access Docker daemon.

### Issue 2: `images: {"python": false, "java": false, "cpp": false}`
* **Symptom:** Docker is reachable, but execution fails due to missing container images.
* **Cause:** Docker images have not been built locally yet.
* **Fix:** Run the build commands from the root directory:
  ```bash
  docker build -t college-code-python:3.11 -f docker/python/Dockerfile docker/python
  docker build -t college-code-java:17 -f docker/java/Dockerfile docker/java
  docker build -t college-code-cpp:gcc -f docker/cpp/Dockerfile docker/cpp
  ```

### Issue 3: Frontend API Call Fails with `ECONNREFUSED`
* **Symptom:** Browser shows network error or terminal logs `http proxy error: /api/v1/execute`.
* **Cause:** FastAPI backend server is not running on `http://127.0.0.1:8000`.
* **Fix:** Start the backend server in a separate terminal:
  ```bash
  cd backend
  .\.venv\Scripts\uvicorn app.main:app --reload --port 8000
  ```

### Issue 4: Orphaned Containers or Temp Folders
* **Symptom:** Disk space growing or container listing shows dead containers.
* **Fix:**
  - Remove stopped execution containers: `docker container prune -f`
  - Run the automated test suite cleanup check: `pytest backend/tests/test_security_hardening.py`
