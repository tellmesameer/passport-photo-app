# run.py
import os
import sys

# ── ONNX Runtime env vars — set BEFORE any onnxruntime import ────────
# These prevent cpuinfo parse failures and thread-pool crashes in
# containerized / restricted environments.
os.environ.setdefault("ORT_DISABLE_CPUINFO", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import uvicorn

if __name__ == "__main__":
    # Include backend directory in python path for uvicorn to find 'app.main:app'
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.insert(0, backend_dir)

    # FastAPI serves the frontend via StaticFiles (see backend/app/main.py).
    # Both the API and the UI are available on the same port — no separate
    # frontend process is needed.
    print("Starting server on http://localhost:8000 ...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[backend_dir])

