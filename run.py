# run.py
import os
import sys
import subprocess
import threading

# ── ONNX Runtime env vars — set BEFORE any onnxruntime import ────────
# These prevent cpuinfo parse failures and thread-pool crashes in
# containerized / restricted environments.
os.environ.setdefault("ORT_DISABLE_CPUINFO", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import uvicorn

def start_frontend():
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    print("Starting frontend server on port 3000...")
    subprocess.run([sys.executable, "-m", "http.server", "3000"], cwd=frontend_dir)

if __name__ == "__main__":
    # Start frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()

    # Include backend directory in python path for uvicorn to find 'app.main:app'
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.insert(0, backend_dir)

    print("Starting FastAPI backend server on port 8000...")
    # Add reload_dirs so changes in the backend directory still trigger hot reloads
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[backend_dir])

