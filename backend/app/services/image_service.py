from fastapi import UploadFile
from PIL import Image
import io
from app.utils.image_processing import remove_background, enhance_image, resize_to_passport
from app.utils.layout import generate_layout
from app.utils.pdf_generator import generate_pdf
from app.core.config import settings


def _prepare_passport_image(file: UploadFile, remove_bg: bool, enhance: bool) -> Image.Image:
    """Common pipeline: load → bg removal → enhance → resize to passport dimensions."""
    file_bytes = file.file.read()
    image = Image.open(io.BytesIO(file_bytes))

    if image.mode != "RGB":
        image = image.convert("RGB")

    if remove_bg:
        image = remove_background(image)

    if enhance:
        image = enhance_image(image)

    return resize_to_passport(image, settings.PHOTO_WIDTH_PX, settings.PHOTO_HEIGHT_PX)


def process_photo_service(file: UploadFile, copies: int, remove_bg: bool, enhance: bool = True, page_size: str = "A4", orientation: str = "portrait") -> io.BytesIO:
    """Returns the layout as a PNG image."""
    passport_image = _prepare_passport_image(file, remove_bg, enhance)
    return generate_layout(passport_image, copies=copies, page_size=page_size, orientation=orientation)


def generate_pdf_service(file: UploadFile, copies: int, remove_bg: bool, enhance: bool = True, page_size: str = "A4", orientation: str = "portrait") -> io.BytesIO:
    """Returns the layout as a print-ready PDF with exact page dimensions at 300 DPI."""
    passport_image = _prepare_passport_image(file, remove_bg, enhance)

    # Generate the pixel layout (PIL Image) on the canvas
    layout_buffer = generate_layout(passport_image, copies=copies, page_size=page_size, orientation=orientation)
    layout_image = Image.open(layout_buffer)

    # Convert to PDF
    return generate_pdf(layout_image, page_size=page_size, orientation=orientation)
