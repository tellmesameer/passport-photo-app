FROM python:3.11-slim

WORKDIR /app

# Install runtime + build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy uv directly
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Install Python dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt && rm -rf /root/.cache/pip

# Copy app code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# ONNX cache
ENV U2NET_HOME=/tmp/.u2net
ENV ORT_DISABLE_CPUINFO=1
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV ORT_LOG_LEVEL=ERROR
ENV PYTHONPATH=/app/backend

EXPOSE 8000

CMD ["gunicorn", "backend.app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]