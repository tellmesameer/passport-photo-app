# run.py
import os
import sys

# Add backend to path early so we can import settings before uvicorn.run
_backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.config import settings

# ── ONNX Runtime env vars — set BEFORE any onnxruntime import ────────
# These prevent cpuinfo parse failures and thread-pool crashes in
# containerized / restricted environments.
os.environ.setdefault("ORT_DISABLE_CPUINFO", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import uvicorn

if __name__ == "__main__":
    # backend_dir is already in sys.path (added above).
    backend_dir = _backend_dir

    # FastAPI serves the frontend via StaticFiles (see backend/app/main.py).
    # Both the API and the UI are available on the same port — no separate
    # frontend process is needed.
    print(f"Starting server on http://localhost:{settings.PORT} ...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True, reload_dirs=[backend_dir])

