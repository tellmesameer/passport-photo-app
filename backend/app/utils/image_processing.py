import io
from PIL import Image, ImageEnhance
from rembg import remove

def remove_background(image: Image.Image) -> Image.Image:
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or "PNG")
    input_data = img_byte_arr.getvalue()
    
    # Remove background
    output_data = remove(input_data)
    
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
