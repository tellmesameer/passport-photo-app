from fastapi import UploadFile
from PIL import Image
import io
from app.utils.image_processing import remove_background, enhance_image, resize_to_passport
from app.utils.layout import generate_layout
from app.core.config import settings

def process_photo_service(file: UploadFile, copies: int, remove_bg: bool, enhance: bool = True, page_size: str = "A4", orientation: str = "portrait") -> io.BytesIO:
    # 1. Load image
    file_bytes = file.file.read()
    image = Image.open(io.BytesIO(file_bytes))
    
    # Convert RGBA to RGB if not removing background
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    # 2. Background removal
    if remove_bg:
        image = remove_background(image)
        
    # 3. Enhance image
    if enhance:
        image = enhance_image(image)
    
    # 4. Resize to passport size
    passport_image = resize_to_passport(image, settings.PHOTO_WIDTH_PX, settings.PHOTO_HEIGHT_PX)
    
    # 5. Generate layout
    output = generate_layout(passport_image, copies=copies, page_size=page_size, orientation=orientation)
    
    return output
