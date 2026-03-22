import io
import logging
import numpy as np
import cv2
from PIL import Image, ImageEnhance

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Backend auto-detection
# ---------------------------------------------------------------------------
# Strategy: try to use rembg (ONNX-based, best quality) and fall back to
# OpenCV GrabCut (pure OpenCV, fork-safe) if rembg/onnxruntime is not
# installed or fails to initialise.
# ---------------------------------------------------------------------------

_BACKEND = None          # "onnx" | "grabcut" — resolved lazily on first use
_rembg_session = None    # singleton rembg session (only used when BACKEND==onnx)


# ──────────────────────────────────────────────────────────────────────────────
# ONNX / rembg path
# ──────────────────────────────────────────────────────────────────────────────

def _create_onnx_session_options():
    """Build ONNX SessionOptions safe for forked / containerised workers."""
    import onnxruntime as ort

    opts = ort.SessionOptions()
    opts.log_severity_level = 3           # ERROR only — avoids DefaultLogger crash
    opts.inter_op_num_threads = 1         # single thread between ops (fork-safe)
    opts.intra_op_num_threads = 1         # single thread within ops  (fork-safe)
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return opts


def _get_rembg_session():
    """Lazily create and return a singleton rembg/ONNX session."""
    from rembg.sessions.u2net_human_seg import U2netHumanSegSession

    global _rembg_session
    if _rembg_session is None:
        logger.info("Initialising rembg/ONNX session (u2net_human_seg, CPUExecutionProvider)…")
        sess_opts = _create_onnx_session_options()
        _rembg_session = U2netHumanSegSession(
            model_name="u2net_human_seg",
            sess_opts=sess_opts,
            providers=["CPUExecutionProvider"],
        )
        logger.info("rembg/ONNX session ready.")
    return _rembg_session


def _remove_background_onnx(image: Image.Image) -> Image.Image:
    """Background removal via rembg (ONNX u2net_human_seg model)."""
    from rembg import remove as rembg_remove

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or "PNG")
    input_data = img_byte_arr.getvalue()

    session = _get_rembg_session()
    output_data = rembg_remove(input_data, session=session)

    output_image = Image.open(io.BytesIO(output_data)).convert("RGBA")
    white_bg = Image.new("RGBA", output_image.size, "WHITE")
    white_bg.paste(output_image, (0, 0), output_image)
    return white_bg.convert("RGB")


# ──────────────────────────────────────────────────────────────────────────────
# GrabCut fallback path
# ──────────────────────────────────────────────────────────────────────────────

def _pil_to_bgr(image: Image.Image) -> np.ndarray:
    rgb = image.convert("RGB")
    return cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)


def _grabcut_mask(bgr: np.ndarray, iterations: int = 10) -> np.ndarray:
    """
    Run GrabCut and return a binary foreground mask (uint8, 0/255).

    Assumes the subject occupies most of the frame (typical passport photo).
    A 5 % border is treated as definite background; the rest as foreground.
    """
    h, w = bgr.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    margin_y = max(5, int(h * 0.05))
    margin_x = max(5, int(w * 0.05))
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

    bgd_model = np.zeros((1, 65), dtype=np.float64)
    fgd_model = np.zeros((1, 65), dtype=np.float64)
    cv2.grabCut(bgr, mask, rect, bgd_model, fgd_model, iterations, cv2.GC_INIT_WITH_RECT)

    fg_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    return fg_mask


def _refine_mask(fg_mask: np.ndarray) -> np.ndarray:
    """Morphological close + Gaussian blur for soft alpha edges."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    closed = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return cv2.GaussianBlur(closed, (21, 21), 0)


def _remove_background_grabcut(image: Image.Image) -> Image.Image:
    """Background removal via OpenCV GrabCut (no ONNX, fork-safe)."""
    bgr = _pil_to_bgr(image)
    fg_mask = _grabcut_mask(bgr)
    alpha = _refine_mask(fg_mask)

    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA)
    rgba[:, :, 3] = alpha

    pil_rgba = Image.fromarray(rgba, "RGBA")
    white_bg = Image.new("RGBA", pil_rgba.size, "WHITE")
    white_bg.paste(pil_rgba, (0, 0), pil_rgba)
    return white_bg.convert("RGB")


# ──────────────────────────────────────────────────────────────────────────────
# Public API — auto-selects backend on first call
# ──────────────────────────────────────────────────────────────────────────────

def _resolve_backend() -> str:
    """
    Return 'onnx' if rembg + onnxruntime are importable, 'grabcut' otherwise.
    Result is cached in the module-level _BACKEND variable.
    """
    global _BACKEND
    if _BACKEND is not None:
        return _BACKEND

    try:
        import onnxruntime  # noqa: F401
        import rembg        # noqa: F401
        _BACKEND = "onnx"
        logger.info("Background removal backend: rembg/ONNX (u2net_human_seg)")
    except ImportError:
        _BACKEND = "grabcut"
        logger.info("rembg/onnxruntime not available — using OpenCV GrabCut fallback")

    return _BACKEND


def remove_background(image: Image.Image) -> Image.Image:
    """
    Remove the background from *image* and composite it over white.

    Uses rembg (ONNX u2net) when available; falls back to OpenCV GrabCut
    if rembg / onnxruntime is not installed.
    """
    backend = _resolve_backend()
    if backend == "onnx":
        try:
            return _remove_background_onnx(image)
        except Exception as exc:
            logger.warning("rembg/ONNX failed (%s) — retrying with GrabCut fallback", exc)
            # Mark backend as unavailable for subsequent requests in this worker
            global _BACKEND
            _BACKEND = "grabcut"

    return _remove_background_grabcut(image)


def warmup_onnx_session() -> None:
    """
    Eagerly initialise the rembg session — call from FastAPI lifespan so the
    first real request doesn't pay the model-load cost.
    Only has effect when the ONNX backend is active.
    """
    if _resolve_backend() == "onnx":
        _get_rembg_session()


# ──────────────────────────────────────────────────────────────────────────────
# Image helpers
# ──────────────────────────────────────────────────────────────────────────────

def enhance_image(image: Image.Image, brightness=1.1, contrast=1.1, sharpness=1.2) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)

    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(sharpness)

    return image


def resize_to_passport(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """Resize and centre-crop *image* to exactly (target_width × target_height)."""
    original_width, original_height = image.size
    aspect_ratio_target = target_width / target_height
    aspect_ratio_original = original_width / original_height

    if aspect_ratio_original > aspect_ratio_target:
        new_height = target_height
        new_width = int(new_height * aspect_ratio_original)
    else:
        new_width = target_width
        new_height = int(new_width / aspect_ratio_original)

    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = (new_width + target_width) / 2
    bottom = (new_height + target_height) / 2

    return image.crop((left, top, right, bottom))
