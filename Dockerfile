FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and other C-extensions
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (requirements.txt is at repo root)
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── ONNX Runtime env vars (prevent cpuinfo / thread-pool crashes) ────
ENV ORT_DISABLE_CPUINFO=1
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV ORT_LOG_LEVEL=ERROR

# ── Serverless: use /tmp for writable files (model cache, etc.) ──────
# Leapcell serverless containers have read-only filesystems except /tmp
ENV U2NET_HOME=/tmp/.u2net

# Copy backend application code
COPY backend/app ./app
COPY backend/gunicorn.conf.py ./gunicorn.conf.py

# Copy frontend so FastAPI can serve it as static files
COPY frontend ./frontend

EXPOSE 3000

# Use gunicorn.conf.py for production-safe ONNX Runtime initialization
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
