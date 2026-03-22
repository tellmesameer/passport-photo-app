import io
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas
from PIL import Image


# Page sizes in points (reportlab units)
PAGE_SIZES = {
    "A4": A4,
    "Letter": letter,
    "4x6": (4 * 72, 6 * 72),   # 4x6 inches in points
    "5x7": (5 * 72, 7 * 72),   # 5x7 inches in points
}


def generate_pdf(layout_image: Image.Image, page_size: str = "A4", orientation: str = "portrait") -> io.BytesIO:
    """
    Convert a full-bleed layout image into a print-ready PDF.
    
    The layout image is drawn edge-to-edge on the PDF page with zero margins,
    ensuring pixel-perfect reproduction at 300 DPI when printed.
    """
    # Determine page dimensions in points
    page_w, page_h = PAGE_SIZES.get(page_size, A4)
    if orientation.lower() == "landscape":
        page_w, page_h = page_h, page_w

    # Save the PIL image to a temporary BytesIO as PNG for reportlab
    img_buffer = io.BytesIO()
    layout_image.save(img_buffer, format="PNG", dpi=(300, 300))
    img_buffer.seek(0)

    # Create the PDF
    pdf_buffer = io.BytesIO()
    c = pdf_canvas.Canvas(pdf_buffer, pagesize=(page_w, page_h))

    # Draw the image full-bleed (origin is bottom-left in reportlab)
    c.drawImage(
        _pil_to_reportlab_image(img_buffer),
        x=0,
        y=0,
        width=page_w,
        height=page_h,
        preserveAspectRatio=False,
    )

    c.setTitle("Passport Photo Layout")
    c.setAuthor("Passport Photo Pro")
    c.save()

    pdf_buffer.seek(0)
    return pdf_buffer


def _pil_to_reportlab_image(img_buffer: io.BytesIO):
    """
    Wrap a PNG BytesIO buffer as a reportlab ImageReader.
    """
    from reportlab.lib.utils import ImageReader
    return ImageReader(img_buffer)
