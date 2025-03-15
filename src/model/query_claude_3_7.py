import json
from src.utils.bedrock_runtime import get_bedrock_runtime

bedrock_runtime = get_bedrock_runtime()

def query_claude_3_7(input_text):
	# Define the request payload
	payload = {
		"anthropic_version": "bedrock-2023-05-31",
		"max_tokens": 200,
		"top_k": 250,
		"stop_sequences": [],
		"temperature": 1,
		"top_p": 0.999,
		"messages": [
			{
				"role": "user",
				"content": [
					{
						"type": "text",
						"text": input_text
					}
				]
			}
		]
	}

	# Convert payload to JSON string
	body_str = json.dumps(payload)

	# Use the correct Inference Profile ID as the modelId
	model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

	# Invoke the Bedrock API with the correct modelId
	response = bedrock_runtime.invoke_model(
		modelId=model_id,  # 🔥 Use Inference Profile ID here
		contentType="application/json",
		accept="application/json",
		body=body_str
	)

	# Parse and print the response
	response_body = json.loads(response['body'].read().decode('utf-8'))
	return json.loads(json.dumps(response_body, indent=2))
