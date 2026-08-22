# 🚀 Setup & Execution Guide for Friends & Collaborators

This guide provides step-by-step instructions for setting up and running the **Standardized Browser-Based Coding Environment** on a fresh laptop/machine.

---

## 📋 Prerequisites Checklist

Before starting, ensure the following software is installed on your machine:

1. **Git**: [Download Git](https://git-scm.com/)
2. **Docker Desktop**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   > ⚠️ **IMPORTANT**: Docker Desktop MUST be running in the background before starting the backend!
3. **Python (3.10 or higher)**: [Download Python](https://www.python.org/downloads/)
4. **Node.js (v18 or higher) & npm**: [Download Node.js](https://nodejs.org/)

---

## 📤 Part 1: Pushing the Code to GitHub (For You)

If you haven't pushed your code to GitHub yet, run these commands in your project terminal:

```bash
git init
git add .
git commit -m "Initial commit - Code Execution Engine IDE"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

---

## 📥 Part 2: Running on Your Friend's Laptop

Follow these exact steps on your friend's machine:

### Step 1: Clone the Repository
Open a terminal (PowerShell / Command Prompt / Terminal) and run:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd "YOUR_REPOSITORY"
```

---

### Step 2: Ensure Docker Desktop is Running
1. Open the **Docker Desktop** app on your computer.
2. Wait until the whale icon status in the bottom corner shows **Docker Desktop is running**.

---

### Step 3: Build the Required Docker Sandbox Images
From the project root directory, run these 3 build commands to generate the isolated sandbox environments:

```bash
docker build -t college-code-python:3.11 -f docker/python/Dockerfile docker/python
docker build -t college-code-java:17 -f docker/java/Dockerfile docker/java
docker build -t college-code-cpp:gcc -f docker/cpp/Dockerfile docker/cpp
```

*Note: This only needs to be done once during initial setup.*

---

### Step 4: Configure & Start the Backend (FastAPI)

1. Open a terminal in the **project root**.
2. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
3. Create and activate a Python virtual environment:
   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   * **macOS / Linux (Bash/Zsh):**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
4. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. *(Optional)* Configure custom environment variables:
   If you want to customize memory or CPU limits, copy `.env.example` to `.env`:
   * **Windows (PowerShell):** `copy .env.example .env`
   * **macOS / Linux:** `cp .env.example .env`
6. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *Backend is now running at:* `http://127.0.0.1:8000`  
   *API documentation (Swagger UI) available at:* `http://127.0.0.1:8000/docs`

---

### Step 5: Configure & Start the Frontend (React + Vite)

1. Open a **NEW terminal window/tab** in the **project root**.
2. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
3. Install frontend dependencies:
   ```bash
   npm install
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *Frontend is now running at:* `http://localhost:3000`

---

### Step 6: Open the IDE in Your Browser
1. Open your browser and navigate to: **`http://localhost:3000`**
2. Write Python, Java, or C++ code and click **Run Code**!

---

## 🛠️ Troubleshooting & Tips

* **Docker Ping Failed / Connection Error**:
  * Ensure Docker Desktop application is open and running.
* **Port 8000 or 3000 already in use**:
  * Close any other servers running on those ports, or change the port in `uvicorn` / `vite.config.ts`.
* **Execution Timeout or Out of Memory**:
  * Default limits: 5 seconds max execution, 256MB RAM. You can increase these in `backend/.env`.
