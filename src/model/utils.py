import json
import base64
from io import BytesIO
from PIL import Image

from src.utils.bedrock_runtime import get_bedrock_runtime

bedrock_runtime = get_bedrock_runtime()

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