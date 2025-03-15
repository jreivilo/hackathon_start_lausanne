import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials from environment variables
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")
aws_region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")  # Ensure this matches the Inference Profile Region

def get_bedrock_runtime():
    """Initialize and return the Bedrock runtime client."""
    return boto3.client(
        "bedrock-runtime",
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        aws_session_token=aws_session_token  # Include if using temporary credentials
    )