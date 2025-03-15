import json
import base64

import chainlit as cl

from src.model.query_claude_3_7 import function_calling_query
from src.utils.image_processor import extract_images
from src.config.schemas import get_analysis_schema

async def process_message(message: cl.Message):
    """
    Process incoming messages and generate appropriate responses.
    
    Args:
        message: The incoming Chainlit message
        
    Returns:
        Tuple containing response text and elements to display
    """
    # Get the JSON schema for structured response
    json_schema = get_analysis_schema()
    
    # Initialize elements list for response
    elements = []
    
    # Check if message contains images
    if message.elements:
        # Extract images from message
        elements, image_list = extract_images(message.elements)
        
        # Get structured response from Claude with images
        function_response = function_calling_query(
            input_text=message.content,
            json_schema=json_schema,
            images=image_list
        )
    else:
        # Process text-only message
        function_response = function_calling_query(
            input_text=message.content,
            json_schema=json_schema
        )
    
    # Extract structured data and explanation
    structured_data = function_response.get("structured_data", {})
    explanation = function_response.get("explanation", "")
    
    # Build an enriched response
    response_text = format_response(structured_data, explanation)
    
    # Log structured data for debugging
    print(f"Structured data: {json.dumps(structured_data, indent=2)}")
    
    return response_text, elements

def format_response(structured_data, explanation):
    """
    Format the response text with structured data and explanation.
    """
    return f"""
### Response
{structured_data.get('analysis', {}).get('response', 'No response available')}

### Additional Details
{explanation}
    """