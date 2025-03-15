import json
import base64
from io import BytesIO
from PIL import Image

from src.utils.bedrock_runtime import get_bedrock_runtime
from src.utils.image_processor import compress_image

bedrock_runtime = get_bedrock_runtime()

def create_bedrock_payload(input_text, images=None, system_prompt=None, tools=None):
	"""
	Creates the payload for Claude's Bedrock API.
	
	Args:
		input_text: Query text
		images: List of base64 encoded images
		system_prompt: Optional system prompt
		tools: List of tools for function calling
		
	Returns:
		Dict: Formatted payload for Bedrock API
	"""
	# Initialize with text
	content_items = [{"type": "text", "text": input_text}]
	
	# Add images if present
	if images and len(images) > 0:
		# Limit to the first image to avoid "Too many packets" error
		base64_image = images[0]
		
		# Compress the image
		compressed_img, media_type = compress_image(base64_image)
		
		# Add the image to content if compression was successful
		if compressed_img and media_type:
			content_items.append({
				"type": "image",
				"source": {
					"type": "base64",
					"media_type": media_type,
					"data": compressed_img
				}
			})
	
	# Build the base payload
	payload = {
		"anthropic_version": "bedrock-2023-05-31",
		"max_tokens": 1000,  # Increased for longer responses
		"top_k": 250,
		"stop_sequences": [],
		"temperature": 0.7,  # Reduced for more precision
		"top_p": 0.999,
		"messages": [
			{
				"role": "user",
				"content": content_items
			}
		]
	}
	
	# Add system prompt if provided
	if system_prompt:
		payload["system"] = system_prompt
	
	# Add tools if provided
	if tools:
		payload["tools"] = tools
	
	return payload

def invoke_claude_model(payload, trace=None, goal=None):
	"""
	Invokes the Claude model via Bedrock.
	
	Args:
		payload: Formatted API payload
		
	Returns:
		Dict: Model response
	"""
	# Convert payload to JSON
	body_str = json.dumps(payload)
	
	# Claude model ID
	model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
	
	# Call Bedrock API
	generation = trace.generation(
		name=goal,
		model="claude-3-7-sonnet-latest",
		input=body_str
	)
	response = bedrock_runtime.invoke_model(
		modelId=model_id,
		contentType="application/json",
		accept="application/json",
		body=body_str
	)
	
	# Process and return response
	response_body = json.loads(response['body'].read().decode('utf-8'))

	generation.end(
		output=response_body,
		usage_details=response_body["usage"],
	)

	return response_body

def query_claude_3_7(input_text, images=None, trace=None, goal=None):
	"""
	Main function to query Claude via Bedrock.
	
	Args:
		input_text: Query text
		images: List of base64 encoded images
		
	Returns:
		Dict: Formatted model response
	"""
	# Create payload
	payload = create_bedrock_payload(input_text, images)
	
	# Invoke model and return response
	return invoke_claude_model(payload, trace, goal)

def function_calling_query(input_text, json_schema, images=None, trace=None):
	"""
	Executes a two-step query:
	1. Generates structured JSON according to the provided schema
	2. Explains the content of the generated JSON
	
	Args:
		input_text: Query text
		json_schema: JSON schema for output structure
		images: List of base64 encoded images (optional)
		
	Returns:
		Dict: Contains structured JSON and its explanation
	"""
	# Define JSON generation tool
	tools = [{
		"name": "generate_structured_data",
		"description": "Generate structured data according to a specified JSON schema",
		"input_schema": {
			"type": "object",
			"properties": {
				"structured_data": {
					"type": "object",
					"description": "Structured data according to the provided schema",
					"properties": json_schema["properties"]
				}
			},
			"required": ["structured_data"]
		}
	}]
	
	# System prompt to guide Claude towards using the tool
	system_prompt = """
	You are an assistant specialized in generating structured data.
	Analyze the request and use the 'generate_structured_data' tool to generate data in JSON format.
	Do not provide explanations in your first response, only the JSON.
	"""
	
	# 1. First request - Generate structured JSON
	json_payload = create_bedrock_payload(
		input_text=input_text,
		images=images,
		system_prompt=system_prompt,
		tools=tools
	)
	
	json_response = invoke_claude_model(json_payload, trace, goal="Extract structured data")
	
	# Extract generated JSON
	tool_response = None
	if "content" in json_response and len(json_response["content"]) > 0:
		for content_item in json_response["content"]:
			if content_item.get("type") == "tool_use":
				# Extract JSON tool response
				tool_response = content_item.get("input", {}).get("structured_data", {})
				break
	
	if not tool_response:
		print("Error: No JSON was generated")
		return {
			"error": "No JSON was generated",
			"raw_response": json_response
		}
	
	# 2. Second request - Explain the generated JSON
	explanation_prompt = f"""
	Data: {json.dumps(tool_response, ensure_ascii=False)}
	Question: "{input_text}"
	
	Answer the question directly based on this data. Be concise (2-3 sentences).
	Respond in the same language as the question.
	"""
	
	explanation_payload = create_bedrock_payload(
		input_text=explanation_prompt,
		system_prompt="You are an expert in data analysis. Clearly and simply explain the content of the provided JSON."
	)
	
	explanation_response = invoke_claude_model(explanation_payload, trace, goal="Answer user question")
	
	# Format final response
	explanation_text = ""
	if "content" in explanation_response and len(explanation_response["content"]) > 0:
		for content_item in explanation_response["content"]:
			if content_item.get("type") == "text":
				explanation_text += content_item.get("text", "")
	
	return {
		"structured_data": tool_response,
		"explanation": explanation_text,
		"raw_json_response": json_response,
		"raw_explanation_response": explanation_response
	}