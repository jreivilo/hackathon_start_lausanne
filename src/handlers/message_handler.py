import json
import base64
import chainlit as cl

from src.model.query_claude_3_7 import query_claude_3_7, function_calling_query, create_bedrock_payload
from src.model.utils import invoke_claude_model
from src.utils.image_processor import extract_images
from src.config.schemas import get_analysis_schema


# Global variable to store the last JSON response
last_json_response = None

async def process_message(message: cl.Message, trace):
    """
    Process incoming messages and generate appropriate responses.
    
    Args:
        message: The incoming Chainlit message
        
    Returns:
        Tuple containing response text and elements to display
    """
    global last_json_response

    # Check if message contains images
    if message.elements:
        # Extract images from message
        elements, image_list = extract_images(message.elements)
        
        # Get structured response from Claude with images
        function_response = function_calling_query(
            input_text=message.content,
            json_schema=get_analysis_schema(),
            images=image_list
        )
        
        # Store the JSON response
        last_json_response = function_response.get("structured_data", {})
        
        # Extract structured data and explanation
        structured_data = last_json_response
        explanation = function_response.get("explanation", "")
        
        # Build an enriched response
        response_text = explanation
    else:
        if last_json_response:
            # Use the last JSON response to make a new query to Claude
            explanation_prompt = f"""
            Here is the last known product information:
            
            ```json
            {json.dumps(last_json_response, ensure_ascii=False, indent=2)}
            ```
            
            User question: {message.content}
            
            Please provide insights and explanations based on this data and the user's question.
            Keep your response clear, precise, and concise - no more than 3-4 sentences.
            Respond in the same language as the user's question.
            """
            
            # Create payload using create_bedrock_payload
            explanation_response = query_claude_3_7(explanation_prompt)


            response_text = explanation_response['content'][0]['text']
            elements = None
        else:
            # If no image is sent and no previous JSON, respond politely
            response_text = "Hello! If you have a question about a product's nutrition, please share an image of the product, and I'll be happy to assist you."
            elements = []

    # Log structured data for debugging
    if last_json_response:
        print(f"Structured data: {json.dumps(last_json_response, indent=2)}")
    
    return response_text, elements

def format_response(structured_data, explanation):
    """
    Format the response text with structured data and explanation.
    """
    return f"""
### Response
{structured_data.get('product', {}).get('name', 'No product name available')}

### Additional Details
{explanation}
    """