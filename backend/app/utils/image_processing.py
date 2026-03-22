import io
import logging
from PIL import Image, ImageEnhance
from rembg import remove

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton ONNX / rembg session
# ---------------------------------------------------------------------------
# WHY: rembg lazily creates an ONNX InferenceSession with default options.
#   In Gunicorn's forked-worker model, the ONNX Runtime logger and thread
#   pools initialized by the master process are left in an invalid state
#   after fork(), causing:
#     "Attempt to use DefaultLogger but none has been registered" → SIGABRT
#
# FIX: We create the session ourselves with safe SessionOptions:
#   • log_severity_level = 3  → suppress verbose logs, avoid DefaultLogger crash
#   • inter/intra_op_num_threads = 1  → no thread-pool issues post-fork
#   • CPUExecutionProvider only  → skip GPU auto-detection (fails in containers)
#
# NOTE: We bypass rembg.new_session() because it creates its own
#   SessionOptions internally and ignores any we pass in. We construct
#   U2netSession directly to get full control.
# ---------------------------------------------------------------------------

_rembg_session = None


def _create_session_options():
    """Build ONNX SessionOptions safe for forked / containerized workers."""
    # DEFERRED IMPORT: onnxruntime must NOT be imported at module level.
    # Importing it in the Gunicorn master process initializes C++ loggers
    # and thread pools that become invalid after fork() → SIGABRT.
    import onnxruntime as ort

    opts = ort.SessionOptions()
    opts.log_severity_level = 3          # ERROR only — prevents DefaultLogger crash
    opts.inter_op_num_threads = 1        # single thread between ops (fork-safe)
    opts.intra_op_num_threads = 1        # single thread within ops  (fork-safe)
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return opts


def get_rembg_session():
    """Lazily create and return a singleton rembg session with safe ONNX options."""
    # DEFERRED IMPORT: rembg.sessions.u2net triggers onnxruntime import
    # internally, so it must also be deferred to avoid master-process init.
    from rembg.sessions.u2net import U2netSession

    global _rembg_session
    if _rembg_session is None:
        logger.info("Initializing rembg/ONNX session (u2net, CPUExecutionProvider)…")
        sess_opts = _create_session_options()
        _rembg_session = U2netSession(
            model_name="u2net",
            sess_opts=sess_opts,
            providers=["CPUExecutionProvider"],
        )
        logger.info("rembg/ONNX session ready.")
    return _rembg_session


def warmup_onnx_session():
    """Eagerly initialize the session — call from FastAPI lifespan / startup."""
    get_rembg_session()


def remove_background(image: Image.Image) -> Image.Image:
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or "PNG")
    input_data = img_byte_arr.getvalue()

    # Remove background using the pre-initialized session
    session = get_rembg_session()
    output_data = remove(input_data, session=session)

    # Convert bytes back to PIL Image
    output_image = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # Create white background
    white_bg = Image.new("RGBA", output_image.size, "WHITE")
    white_bg.paste(output_image, (0, 0), output_image)
    return white_bg.convert("RGB")

def enhance_image(image: Image.Image, brightness=1.1, contrast=1.1, sharpness=1.2) -> Image.Image:
    # Brightness
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)
    
    # Contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)
    
    # Sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(sharpness)
    
    return image

def resize_to_passport(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    # Resize and crop to fill the target dimensions, maintaining aspect ratio
    original_width, original_height = image.size
    aspect_ratio_target = target_width / target_height
    aspect_ratio_original = original_width / original_height
    
    if aspect_ratio_original > aspect_ratio_target:
        # Image is wider than target
        new_height = target_height
        new_width = int(new_height * aspect_ratio_original)
    else:
        # Image is taller than target
        new_width = target_width
        new_height = int(new_width / aspect_ratio_original)
        
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Center crop
    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = (new_width + target_width) / 2
    bottom = (new_height + target_height) / 2
    
    image = image.crop((left, top, right, bottom))
    return image
