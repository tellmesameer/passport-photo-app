# backend/app/main.py
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.router import api_router
from app.utils.image_processing import warmup_onnx_session

# Configure logging so ONNX init messages are visible in Gunicorn
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — runs ONCE per worker process (after Gunicorn fork)
# ---------------------------------------------------------------------------
# WHY: Eagerly creating the ONNX session here guarantees it is initialized
#   *inside* the worker process, not in the Gunicorn master. This avoids the
#   corrupted logger / thread-pool state that causes SIGABRT.
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # warmup_onnx_session is a no-op if rembg/onnxruntime is not installed;
    # it eagerly loads the u2net model when the ONNX backend is active.
    warmup_onnx_session()
    logger.info("Worker starting.")
    yield
    logger.info("Worker shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


# ---------------------------------------------------------------------------
# Health-check endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/kaithheathcheck")
def leapcell_health_check():
    """Leapcell platform health-check probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Serve the frontend via Jinja2 templates + static asset mounts
# ---------------------------------------------------------------------------
# Structure:
#   frontend/index.html   → rendered by Jinja2 at GET /
#   frontend/src/         → served as /static  (CSS, JS)
#   frontend/public/      → served as /public  (images, icons, etc.)
# ---------------------------------------------------------------------------
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"

if _frontend_dir.is_dir():
    templates = Jinja2Templates(directory=str(_frontend_dir))

    # CSS / JS assets
    _src_dir = _frontend_dir / "src"
    if _src_dir.is_dir():
        app.mount("/static", StaticFiles(directory=str(_src_dir)), name="static")
        logger.info("Serving static assets (CSS/JS) from %s", _src_dir)

    # Public assets (images, icons, fonts …)
    _public_dir = _frontend_dir / "public"
    if _public_dir.is_dir():
        app.mount("/public", StaticFiles(directory=str(_public_dir)), name="public")
        logger.info("Serving public assets from %s", _public_dir)

    @app.get("/")
    async def serve_index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    logger.info("Serving frontend (Jinja2) from %s", _frontend_dir)
else:
    logger.warning(
        "Frontend directory not found at %s — UI will not be served.", _frontend_dir
    )

