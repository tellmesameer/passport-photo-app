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

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
