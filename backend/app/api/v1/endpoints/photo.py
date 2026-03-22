from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import Response
from app.services.image_service import process_photo_service, generate_pdf_service

router = APIRouter()

@router.post("/process")
def process_photo(
    file: UploadFile = File(...),
    copies: int = Form(8),
    remove_bg: bool = Form(False),
    enhance: bool = Form(True),
    page_size: str = Form("A4"),
    orientation: str = Form("portrait")
):
    try:
        a4_output = process_photo_service(file, copies, remove_bg, enhance, page_size, orientation)
        return Response(content=a4_output.getvalue(), media_type="image/png")
    except Exception as e:
        return Response(content=str(e), status_code=500)


@router.post("/generate-pdf")
def generate_pdf(
    file: UploadFile = File(...),
    copies: int = Form(8),
    remove_bg: bool = Form(False),
    enhance: bool = Form(True),
    page_size: str = Form("A4"),
    orientation: str = Form("portrait")
):
    try:
        pdf_output = generate_pdf_service(file, copies, remove_bg, enhance, page_size, orientation)
        return Response(
            content=pdf_output.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=passport_photos.pdf"},
        )
    except Exception as e:
        return Response(content=str(e), status_code=500)
