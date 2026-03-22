# Gunicorn configuration for production / containerized environments
# -------------------------------------------------------------------
# Usage:
#   gunicorn -c gunicorn.conf.py app.main:app
# -------------------------------------------------------------------

import os

# ── Worker settings ──────────────────────────────────────────────────
bind = f":{os.environ.get('PORT', '10000')}"
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 600

# CRITICAL: Do NOT set preload_app = True.
# preload_app loads the application in the master process *before* forking.
# ONNX Runtime initializes internal loggers and thread pools during import,
# and these are left in an invalid state after fork(), causing:
#   "Attempt to use DefaultLogger but none has been registered" → SIGABRT
#
# With preload_app = False (default), each worker loads the app independently
# *after* fork, so the ONNX session created in the lifespan hook is always
# in a valid state.
preload_app = False

# ── Environment variables for ONNX Runtime ───────────────────────────
# Set these early so they take effect before onnxruntime is imported.
os.environ.setdefault("ORT_DISABLE_CPUINFO", "1")       # skip /sys/devices/system/cpu parsing
os.environ.setdefault("OMP_NUM_THREADS", "1")            # single OpenMP thread (fork-safe)
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")       # single OpenBLAS thread (fork-safe)

# ── Logging ──────────────────────────────────────────────────────────
accesslog = "-"
errorlog = "-"
loglevel = "info"
