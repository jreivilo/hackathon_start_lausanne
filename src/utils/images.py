import base64
from io import BytesIO
from PIL import Image

def compress_image(base64_image, max_size_kb=1024):
    """
    Compresse et redimensionne une image encodée en base64.
    
    Args:
        base64_image: Image encodée en base64
        max_size_kb: Taille maximale souhaitée en KB
        
    Returns:
        Tuple (compressed_img_base64, media_type): Image compressée en base64 et son type MIME
    """
    try:
        # Decode base64 to binary
        img_data = base64.b64decode(base64_image)
        img = Image.open(BytesIO(img_data))
        
        # Get original size for logging
        original_size = len(img_data)
        print(f"Original image size: {original_size / 1024:.2f} KB")
        
        # Première compression - réduction modérée
        max_size = (512, 512)
        img.thumbnail(max_size, Image.LANCZOS)
        
        # Déterminer le format selon le mode de l'image
        is_transparent = img.mode == 'RGBA'
        img_format = "PNG" if is_transparent else "JPEG"
        media_type = f"image/{img_format.lower()}"
        
        # Compression initiale
        buffer = BytesIO()
        if is_transparent:
            img.save(buffer, format="PNG", optimize=True, compress_level=9)
        else:
            img.save(buffer, format="JPEG", quality=60, optimize=True)
        
        compressed_data = buffer.getvalue()
        compressed_size = len(compressed_data)
        print(f"Compressed image size: {compressed_size / 1024:.2f} KB")
        print(f"Compression ratio: {compressed_size / original_size:.2f}")
        
        # Si encore trop grande, réduire davantage
        if compressed_size > max_size_kb * 1024:
            print("Image still too large, reducing further...")
            img.thumbnail((384, 384), Image.LANCZOS)
            buffer = BytesIO()
            if is_transparent:
                img.save(buffer, format="PNG", optimize=True, compress_level=9)
            else:
                img.save(buffer, format="JPEG", quality=50, optimize=True)
            compressed_data = buffer.getvalue()
            print(f"Final image size: {len(compressed_data) / 1024:.2f} KB")
        
        # Encoder en base64 et retourner
        compressed_img = base64.b64encode(compressed_data).decode("utf-8")
        return compressed_img, media_type
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None, None
