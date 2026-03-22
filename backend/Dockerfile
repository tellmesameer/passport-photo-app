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

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create cache directory for u2net models used by rembg
ENV U2NET_HOME=/app/.u2net
RUN mkdir -p /app/.u2net

# ── ONNX Runtime env vars (prevent cpuinfo / thread-pool crashes) ────
ENV ORT_DISABLE_CPUINFO=1
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV ORT_LOG_LEVEL=ERROR

COPY . .

EXPOSE 8080

# Use gunicorn.conf.py for production-safe ONNX Runtime initialization
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]

