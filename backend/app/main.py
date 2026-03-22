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
    logger.info("Worker starting — warming up ONNX/rembg session…")
    warmup_onnx_session()
    logger.info("ONNX session warm-up complete.")
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
# Serve the frontend as static files (single-container deployment)
# ---------------------------------------------------------------------------
# The frontend directory is expected next to the backend `app/` package.
# In Docker it is COPY'd to /app/frontend.  Locally it lives at ../frontend.
# Mount LAST so API routes take priority over the catch-all static mount.
# ---------------------------------------------------------------------------
_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if _frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
    logger.info("Serving frontend from %s", _frontend_dir)
else:
    logger.warning("Frontend directory not found at %s — static files will not be served.", _frontend_dir)

