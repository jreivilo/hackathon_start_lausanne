import json
import base64
from io import BytesIO
from PIL import Image
from src.utils.bedrock_runtime import get_bedrock_runtime

bedrock_runtime = get_bedrock_runtime()

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

def create_bedrock_payload(input_text, images=None):
    """
    Crée le payload pour l'API Bedrock de Claude.
    
    Args:
        input_text: Texte de la requête
        images: Liste d'images encodées en base64
        
    Returns:
        Dict: Payload formaté pour l'API Bedrock
    """
    # Initialiser avec le texte
    content_items = [{"type": "text", "text": input_text}]
    
    # Ajouter des images si présentes
    if images and len(images) > 0:
        # Limiter à la première image pour éviter l'erreur "Too many packets"
        base64_image = images[0]
        
        # Compresser l'image
        compressed_img, media_type = compress_image(base64_image)
        
        # Ajouter l'image au contenu si la compression a réussi
        if compressed_img and media_type:
            content_items.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": compressed_img
                }
            })
    
    # Construire le payload complet
    return {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "top_k": 250,
        "stop_sequences": [],
        "temperature": 1,
        "top_p": 0.999,
        "messages": [
            {
                "role": "user",
                "content": content_items
            }
        ]
    }

def invoke_claude_model(payload):
    """
    Invoque le modèle Claude via Bedrock.
    
    Args:
        payload: Payload formaté pour l'API
        
    Returns:
        Dict: Réponse du modèle
    """
    # Convertir le payload en JSON
    body_str = json.dumps(payload)
    
    # ID du modèle Claude
    model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    
    # Appeler l'API Bedrock
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=body_str
    )
    
    # Traiter et retourner la réponse
    response_body = json.loads(response['body'].read().decode('utf-8'))
    return json.loads(json.dumps(response_body, indent=2))

def query_claude_3_7(input_text, images=None):
    """
    Fonction principale pour interroger Claude via Bedrock.
    
    Args:
        input_text: Texte de la requête
        images: Liste d'images encodées en base64
        
    Returns:
        Dict: Réponse formatée du modèle
    """
    # Créer le payload
    payload = create_bedrock_payload(input_text, images)
    
    # Invoquer le modèle et retourner la réponse
    return invoke_claude_model(payload)