import logging
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import Response, JSONResponse
from ....services.image_service import process_photo_service, generate_pdf_service

logger = logging.getLogger(__name__)
router = APIRouter()


def _error_response(exc: Exception, status_code: int = 500) -> JSONResponse:
    """Return a JSON error body so the frontend can display a clean message."""
    exc_type = type(exc).__name__
    detail = str(exc) or "An unexpected error occurred."
    logger.error("[%s] %s", exc_type, detail, exc_info=exc)
    return JSONResponse(
        status_code=status_code,
        content={"error": exc_type, "detail": detail},
    )


@router.post("/process")
def process_photo(
    file: UploadFile = File(...),
    copies: int = Form(8),
    remove_bg: bool = Form(False),
    enhance: bool = Form(True),
    page_size: str = Form("A4"),
    orientation: str = Form("portrait"),
):
    try:
        a4_output = process_photo_service(file, copies, remove_bg, enhance, page_size, orientation)
        return Response(content=a4_output.getvalue(), media_type="image/png")
    except ValueError as e:
        return _error_response(e, status_code=422)
    except Exception as e:
        return _error_response(e, status_code=500)


@router.post("/generate-pdf")
def generate_pdf(
    file: UploadFile = File(...),
    copies: int = Form(8),
    remove_bg: bool = Form(False),
    enhance: bool = Form(True),
    page_size: str = Form("A4"),
    orientation: str = Form("portrait"),
):
    try:
        pdf_output = generate_pdf_service(file, copies, remove_bg, enhance, page_size, orientation)
        return Response(
            content=pdf_output.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=passport_photos.pdf"},
        )
    except ValueError as e:
        return _error_response(e, status_code=422)
    except Exception as e:
        return _error_response(e, status_code=500)
