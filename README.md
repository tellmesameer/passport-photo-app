# Passport Photo Pro

A production-ready full-stack web application for generating passport-size photos arranged on an A4 page for printing. Features automatic background removal, image enhancement, and a premium responsive UI.

## Features
- Upload JPEG/PNG images
- Optional AI background removal (Powered by U-2-Net / rembg)
- Automatic image enhancement (Brightness, Contrast, Sharpness)
- Configurable number of copies arranged automatically on an A4 grid
- Download as PNG or Print directly from the browser

## Tech Stack
- **Backend**: Python, FastAPI, Pillow, OpenCV, rembg
- **Frontend**: HTML5, Vanilla JavaScript, CSS3
- **Infrastructure**: Nginx, Docker, Docker Compose

## Setup and Running

### 1. Using Docker Compose (Recommended)

1. Ensure Docker and Docker Compose are installed.
2. In the root directory, run:
   ```bash
   docker-compose up --build -d
   ```
3. Open your browser and navigate to `http://localhost`.

### 2. Local Development (Without Docker)

#### Backend Configuration
Navigate to the `backend` directory and run:
```powershell
cd backend
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```
The FastAPI server will be available at `http://localhost:8000`.

#### Frontend Configuration
Serve the static files locally. For example:
```powershell
cd frontend
python -m http.server 8080
```
Open your browser at `http://localhost:8080/public/index.html`.

*Note*: If you run the frontend locally without Nginx, the API fetch requests are automatically mapped directly to the local FastAPI port (`http://127.0.0.1:8000`) within `frontend/src/js/api.js`. For production via Docker, they route to the `/api/v1` Nginx proxy.

## Project Structure
```text
passport-photo-app/
├── backend/                  # FastAPI backend
│   ├── app/                  # Application code
│   │   ├── api/              # Route endpoints
│   │   ├── core/             # Configuration and logging
│   │   ├── services/         # Image & Layout business logic
│   │   └── utils/            # Pillow, OpenCV arrays
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Vanilla JS frontend
│   ├── public/               # Main index.html
│   └── src/                  # JS & CSS assets
├── nginx/                    # Reverse-proxy configuration
│   └── nginx.conf
├── docker-compose.yml        # Multi-container orchestration
└── README.md                 # Project Documentation
```
