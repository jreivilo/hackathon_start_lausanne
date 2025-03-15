import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials from environment variables
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")
aws_region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")  # Ensure this matches the Inference Profile Region

# Initialize the Bedrock runtime client
bedrock_runtime = boto3.client(
    "bedrock-runtime",
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    aws_session_token=aws_session_token  # Include if using temporary credentials
)

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
                    "text": "hello world"
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
print(response_body)
