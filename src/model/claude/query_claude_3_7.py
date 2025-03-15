import json
import base64
from io import BytesIO
from PIL import Image

from src.utils.bedrock_runtime import get_bedrock_runtime
from src.utils.images import compress_image
from src.model.claude.utils import invoke_claude_model

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