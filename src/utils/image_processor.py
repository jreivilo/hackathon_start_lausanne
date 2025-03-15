import base64
from typing import List, Tuple, Any
import chainlit as cl
from io import BytesIO
from PIL import Image



def compress_image(base64_image, max_size_kb=2048):
    """
    Compresses and resizes a base64 encoded image.

    Args:
        base64_image: Base64 encoded image
        max_size_kb: Maximum desired size in KB (increased to 2MB)

    Returns:
        Tuple (compressed_img_base64, media_type): Compressed base64 image and its MIME type
    """
    try:
        # Decode base64 to binary
        img_data = base64.b64decode(base64_image)
        img = Image.open(BytesIO(img_data))

        # Get original size for logging
        original_size = len(img_data)
        print(f"Original image size: {original_size / 1024:.2f} KB")

        # First compression - resize to maximum allowed size
        max_size = (2048, 2048)  # Increased to 2048x2048
        img.thumbnail(max_size, Image.LANCZOS)

        # Determine format based on image mode
        is_transparent = img.mode == 'RGBA'
        img_format = "PNG" if is_transparent else "JPEG"
        media_type = f"image/{img_format.lower()}"

        # Initial compression with higher quality
        buffer = BytesIO()
        if is_transparent:
            img.save(buffer, format="PNG", optimize=True, compress_level=6)
        else:
            img.save(buffer, format="JPEG", quality=80, optimize=True)

        compressed_data = buffer.getvalue()
        compressed_size = len(compressed_data)
        print(f"Compressed image size: {compressed_size / 1024:.2f} KB")
        print(f"Compression ratio: {compressed_size / original_size:.2f}")

        # If still too large, reduce further but maintain higher quality
        if compressed_size > max_size_kb * 1024:
            print("Image still too large, reducing further...")
            img.thumbnail((1600, 1600), Image.LANCZOS)  # Fallback size
            buffer = BytesIO()
            if is_transparent:
                img.save(buffer, format="PNG", optimize=True, compress_level=6)
            else:
                img.save(buffer, format="JPEG", quality=70, optimize=True)
            compressed_data = buffer.getvalue()
            print(f"Final image size: {len(compressed_data) / 1024:.2f} KB")

        # Encode to base64 and return
        compressed_img = base64.b64encode(compressed_data).decode("utf-8")
        return compressed_img, media_type

    except Exception as e:
        print(f"Error processing image: {e}")
        return None, None

def extract_images(elements: List[Any]) -> Tuple[List[Any], List[str]]:
    """
    Extract images from Chainlit elements and convert them to base64.
    
    Args:
        elements: List of Chainlit elements
        
    Returns:
        Tuple containing elements to display and list of base64 encoded images
    """
    processed_elements = []
    image_list = []
    
    for element in elements:
        if isinstance(element, cl.Image):
            # Add image to response elements
            processed_elements.append(element)
            
            # Get image data for Claude
            image_data = element.path
            with open(image_data, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode("utf-8")
                image_list.append(base64_image)
    
    return processed_elements, image_list