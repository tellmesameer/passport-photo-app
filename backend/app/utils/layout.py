import io
from PIL import Image, ImageDraw
from app.core.config import settings

def get_page_dimensions(page_size: str, orientation: str):
    sizes = {
        "A4": (settings.A4_WIDTH_PX, settings.A4_HEIGHT_PX),
        "Letter": (settings.LETTER_WIDTH_PX, settings.LETTER_HEIGHT_PX),
        "4x6": (settings.PHOTO_4X6_WIDTH_PX, settings.PHOTO_4X6_HEIGHT_PX),
        "5x7": (settings.PHOTO_5X7_WIDTH_PX, settings.PHOTO_5X7_HEIGHT_PX),
    }
    width, height = sizes.get(page_size, sizes["A4"])
    if orientation.lower() == "landscape":
        return height, width
    return width, height

def generate_layout(photo: Image.Image, copies: int = 8, page_size: str = "A4", orientation: str = "portrait") -> io.BytesIO:
    page_w, page_h = get_page_dimensions(page_size, orientation)
    
    # Create canvas (white)
    canvas = Image.new("RGB", (page_w, page_h), "white")
    
    photo_w, photo_h = photo.size
    
    # We want to arrange `copies` number of photos
    margin_x = 100
    margin_y = 100
    spacing_x = 50
    spacing_y = 50
    
    # Max columns that can fit
    usable_width = page_w - (2 * margin_x)
    usable_height = page_h - (2 * margin_y)
    
    cols = (usable_width + spacing_x) // (photo_w + spacing_x)
    rows = (usable_height + spacing_y) // (photo_h + spacing_y)
    
    col = 0
    row = 0
    
    for _ in range(copies):
        if row >= rows:
            # Reached end of page capability
            break
            
        x = margin_x + col * (photo_w + spacing_x)
        y = margin_y + row * (photo_h + spacing_y)
        
        canvas.paste(photo, (x, y))
        
        # Draw 1px cut-line border around the photo
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([x - 1, y - 1, x + photo_w, y + photo_h], outline="black", width=1)
        
        col += 1
        if col >= cols:
            col = 0
            row += 1
            
    # Output to BytesIO
    output = io.BytesIO()
    canvas.save(output, format="PNG", dpi=(settings.DPI, settings.DPI))
    output.seek(0)
    return output
