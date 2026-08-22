# Standardized Browser-Based Coding Environment (Module 1)

Module 1 of a college programming laboratory and examination platform: a browser-based IDE that executes student code inside isolated, resource-limited Docker containers.

---

## Technical Architecture & Stack

* **Frontend:** React + Vite + TypeScript, Monaco Editor (`@monaco-editor/react`), Axios, Glassmorphism Dark UI Design Tokens (Vanilla CSS).
* **Backend:** Python + FastAPI + Pydantic v2 + Uvicorn, Docker SDK for Python (`docker` package).
* **Execution Sandboxing:** Docker Engine, one image per language, strict resource limits (1 CPU core, 256MB RAM, 64 PIDs, network disabled, capability drop `ALL`, non-root `sandbox` UID 1000).
* **Supported Languages (v1):** Python 3.11, Java 17, C++ (GCC).

---

## Project Structure

```
project-root/
├── frontend/                  # React + Vite + TypeScript Frontend
│   ├── src/
│   │   ├── components/        # Header, CodeEditor, StdinPanel, OutputPanel
│   │   ├── api/               # Axios API client
│   │   ├── types/             # Shared TS types mirroring backend schemas
│   │   ├── utils/             # Default code snippets
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                   # FastAPI Code Execution Engine
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint & router registry
│   │   ├── api/v1/            # API route handlers (/execute, /health)
│   │   ├── services/          # ExecutionService & DockerService
│   │   ├── models/            # Language configuration definitions
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── core/              # Config settings & structured logging
│   │   └── utils/             # Workspace & ID utilities
│   ├── tests/                 # Comprehensive test suite (29 tests)
│   └── requirements.txt
│
├── docker/                    # Language Sandbox Dockerfiles
│   ├── python/Dockerfile      # college-code-python:3.11
│   ├── java/Dockerfile        # college-code-java:17
│   └── cpp/Dockerfile         # college-code-cpp:gcc
│
├── docs/                      # Architectural & Security Documentation
│   ├── architecture.md
│   ├── execution-flow.md
│   ├── security.md
│   └── troubleshooting.md
│
├── docker-compose.yml
└── README.md
```

---

## Quickstart Guide

### 1. Build Required Docker Sandbox Images
From the project root directory, run:

```bash
docker build -t college-code-python:3.11 -f docker/python/Dockerfile docker/python
docker build -t college-code-java:17 -f docker/java/Dockerfile docker/java
docker build -t college-code-cpp:gcc -f docker/cpp/Dockerfile docker/cpp
```

### 2. Start the Backend API Server
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger UI will be accessible at: `http://127.0.0.1:8000/docs`

### 3. Start the Frontend IDE
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## API Documentation

### `POST /api/v1/execute`
Submits code for containerized execution.

**Request Body:**
```json
{
  "language": "python",
  "code": "n = int(input())\nprint(n * n)",
  "stdin": "5"
}
```

**Response (Success):**
```json
{
  "success": true,
  "language": "python",
  "stdout": "25\n",
  "stderr": "",
  "exit_code": 0,
  "execution_time_ms": 35,
  "status": "COMPLETED",
  "execution_id": "exec_8f92a1c4"
}
```

**Status Enum Values:**
`COMPLETED`, `COMPILATION_ERROR`, `RUNTIME_ERROR`, `TIME_LIMIT_EXCEEDED`, `MEMORY_LIMIT_EXCEEDED`, `OUTPUT_LIMIT_EXCEEDED`, `SYSTEM_ERROR`.

---

## Running the Automated Test Suite

Run all 29 unit, integration, limit, and security tests:
```bash
cd backend
.\.venv\Scripts\pytest
```

---

## Documentation Links

* [Architecture Overview](docs/architecture.md)
* [Execution Flow Trace](docs/execution-flow.md)
* [Security & Threat Model Audit](docs/security.md)
* [Troubleshooting & Diagnostics](docs/troubleshooting.md)
