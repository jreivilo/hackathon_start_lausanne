# Developer Guide - NutriTrack

This document provides detailed technical information for developers working on the NutriTrack project.

## Table of Contents

- [Development Environment](#development-environment)
- [Detailed Architecture](#detailed-architecture)
- [APIs and Interfaces](#apis-and-interfaces)
- [AWS Bedrock Integration](#aws-bedrock-integration)
- [Image Management](#image-management)
- [Data Storage](#data-storage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Development Environment

### Local Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure Python 3.12
pyenv install 3.12
pyenv local 3.12

# Install dependencies
uv sync

# Generate Chainlit secret
uv run chainlit secret

# Configure environment variables
cp .env.template .env
# Edit .env with your own keys
```

### Detailed Project Structure

```
.
├── .chainlit/               # Chainlit configuration (auto-generated)
│   └── config.json          # User interface configuration
├── .env                     # Environment variables
├── .env.template            # Template for environment variables
├── .files/                  # Temporary files (uploads, etc.)
├── .git/                    # Git configuration
├── .gitignore               # Files ignored by Git
├── .gitmodules              # Git submodules
├── .idea/                   # PyCharm configuration
├── .python-version          # Python version for pyenv
├── .venv/                   # Python virtual environment
├── __pycache__/             # Python cache
├── Dockerfile               # Docker configuration
├── README.md                # Basic documentation
├── chainlit.config.py       # Specific Chainlit configuration
├── chainlit.md              # Chainlit welcome page
├── main.py                  # Main entry point
├── public/                  # Static resources for interface
├── pyproject.toml           # Project configuration and dependencies
├── src/                     # Source code
│   ├── config/              # Configuration
│   │   ├── __pycache__/     # Python cache
│   │   └── schemas.py       # JSON schemas for AI
│   ├── handler/             # Old handler folder (deprecated)
│   ├── handlers/            # Request handlers
│   │   ├── __pycache__/     # Python cache
│   │   └── message_handler.py # Message handler
│   ├── model/               # AI models
│   │   ├── __pycache__/     # Python cache
│   │   └── query_claude_3_7.py # Claude 3.7 integration
│   └── utils/               # Utilities
│       ├── __pycache__/     # Python cache
│       ├── bedrock_runtime.py # AWS Bedrock client
│       └── image_processor.py # Image processing
└── uv.lock                  # Dependency lock for uv
```

## Detailed Architecture

### Sequence Diagram

```
┌────────┐          ┌──────────┐          ┌───────────┐          ┌─────────┐          ┌─────────┐
│ Client │          │ Chainlit │          │ Handler   │          │ Claude  │          │ Langfuse│
└───┬────┘          └────┬─────┘          └─────┬─────┘          └────┬────┘          └────┬────┘
    │                     │                      │                     │                     │
    │  ── Message ──>     │                      │                     │                     │
    │                     │                      │                     │                     │
    │                     │  ── Message ──>      │                     │                     │
    │                     │                      │                     │                     │
    │                     │                      │  ── Trace Start ──> │                     │
    │                     │                      │                     │                     │
    │                     │                      │                     │  <── Trace ID ───   │
    │                     │                      │                     │                     │
    │                     │                      │  ── Query ──>       │                     │
    │                     │                      │                     │                     │
    │                     │                      │                     │ ── Log Request ──>  │
    │                     │                      │                     │                     │
    │                     │                      │  <── Response ───   │                     │
    │                     │                      │                     │                     │
    │                     │                      │                     │ ── Log Response ──> │
    │                     │                      │                     │                     │
    │                     │  <── Response ───    │                     │                     │
    │                     │                      │                     │                     │
    │  <── Response ───   │                      │                     │                     │
    │                     │                      │                     │                     │
```

### Detailed Data Flow

1. **Message Reception**:
   - The message arrives at Chainlit via the web interface
   - The `@cl.on_message` event is triggered in `main.py`
   - A loading message is created and displayed to the user

2. **Message Processing**:
   - If the message is a special command (starts with `!`), it is processed by `handle_starter_command()`
   - Otherwise, the message is sent to `process_message()` in `message_handler.py`

3. **Image Analysis** (if present):
   - Images are extracted with `extract_images()`
   - Images are compressed with `compress_image()`
   - Images and text are sent to Claude via `function_calling_query()`

4. **Response Generation**:
   - If the message contained an image, Claude generates a JSON structure with nutritional information
   - If the message was textual, Claude generates a response based on consumed products history
   - The response is formatted and enriched with actions (buttons to add or skip a product)

5. **Response Sending**:
   - The final response is sent to the user
   - The loading message is removed
   - The Langfuse trace is closed

## APIs and Interfaces

### Main Functions in `message_handler.py`

```python
async def process_message(message: cl.Message, trace, consumed_products)
```
- **Parameters**:
  - `message`: The Chainlit message object received from the user
  - `trace`: The Langfuse trace object for monitoring
  - `consumed_products`: List of products consumed by the user
- **Returns**: A tuple containing (response_text, elements, json_data)

```python
def format_response(structured_data, explanation)
```
- **Parameters**:
  - `structured_data`: Structured JSON data from Claude
  - `explanation`: Textual explanation from Claude
- **Returns**: A formatted text string for display

### Main Functions in `query_claude_3_7.py`

```python
def create_bedrock_payload(input_text, images=None, system_prompt=None, tools=None)
```
- **Parameters**:
  - `input_text`: Query text
  - `images`: List of base64 encoded images (optional)
  - `system_prompt`: System prompt for Claude (optional)
  - `tools`: Tools for function calling (optional)
- **Returns**: Formatted dictionary for the Bedrock API

```python
def invoke_claude_model(payload, trace=None, goal=None)
```
- **Parameters**:
  - `payload`: Formatted payload for the Bedrock API
  - `trace`: Langfuse trace object (optional)
  - `goal`: Description of the objective for monitoring (optional)
- **Returns**: Raw response from the Bedrock API

```python
def query_claude_3_7(input_text, images=None, trace=None, goal=None)
```
- **Parameters**:
  - `input_text`: Query text
  - `images`: List of base64 encoded images (optional)
  - `trace`: Langfuse trace object (optional)
  - `goal`: Description of the objective for monitoring (optional)
- **Returns**: Formatted response from Claude

```python
def function_calling_query(input_text, json_schema, images=None, trace=None)
```
- **Parameters**:
  - `input_text`: Query text
  - `json_schema`: JSON schema to structure the response
  - `images`: List of base64 encoded images (optional)
  - `trace`: Langfuse trace object (optional)
- **Returns**: Dictionary containing structured data and explanation

### Main Functions in `image_processor.py`

```python
def compress_image(base64_image, max_size_kb=2048)
```
- **Parameters**:
  - `base64_image`: Base64 encoded image
  - `max_size_kb`: Maximum size in KB (default 2048)
- **Returns**: Tuple (compressed_image_base64, media_type)

```python
def extract_images(elements: List[Any])
```
- **Parameters**:
  - `elements`: List of Chainlit elements
- **Returns**: Tuple (processed_elements, base64_images_list)

## AWS Bedrock Integration

### AWS Configuration

The application uses AWS Bedrock to access Claude 3.7 Sonnet. Authentication information is loaded from the `.env` file:

```python
# Retrieve AWS credentials from environment variables
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")
aws_region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
```

### Claude 3.7 Model ID

```python
model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
```

### Response Format

Claude 3.7 returns a JSON response with the following structure:

```json
{
  "id": "...",
  "type": "message",
  "role": "assistant",
  "model": "...",
  "content": [
    {
      "type": "text",
      "text": "..."
    }
  ],
  "usage": {
    "input_tokens": 123,
    "output_tokens": 456
  }
}
```

For function calling queries, the response contains an element of type `tool_use`:

```json
{
  "content": [
    {
      "type": "tool_use",
      "input": {
        "structured_data": {
          "product": {
            "name": "...",
            "nutritive_value": {
              "calories": 123,
              ...
            }
          }
        }
      }
    }
  ]
}
```

## Image Management

### Size Limits

Claude 3.7 has limits on image size:
- Recommended maximum size: 2048 KB (2 MB)
- Recommended maximum resolution: 2048x2048 pixels

### Compression Process

1. Decode base64 image to binary
2. Open with PIL (Python Imaging Library)
3. Resize if necessary (max 2048x2048)
4. Compress with adapted quality:
   - PNG for images with transparency
   - JPEG for images without transparency
5. Check final size
6. Additional compression if still too large

## Data Storage

### In-Memory Storage

Currently, the application uses simple in-memory storage for user data:

```python
# Simple in-memory storage for consumed products
consumed_products = {}

# Simple in-memory storage for user IDs
dict_user_ids = {}
```

### Product Data Structure

```python
{
  "product": {
    "name": "Product name",
    "origin": "Country of origin",
    "ingredients": ["ingredient1", "ingredient2", ...],
    "nutritive_value": {
      "calories": 123,
      "protein": 10,
      "fat": 5,
      "carbohydrates": 20,
      "sugar": 2,
      "fiber": 3,
      "sodium": 50
    }
  }
}
```

## Testing

To run tests (to be implemented):

```bash
# Install test dependencies
uv pip install pytest pytest-asyncio

# Run tests
uv run pytest
```

### Recommended Test Structure

```
tests/
├── conftest.py                  # pytest configuration
├── test_bedrock_integration.py  # Bedrock integration tests
├── test_image_processing.py     # Image processing tests
├── test_message_handling.py     # Message handling tests
└── test_schema_validation.py    # Schema validation tests
```

## Deployment

### Docker Deployment

```bash
# Build the image
docker build -t nutritrack .

# Run the container with environment variables
docker run -p 8080:8080 \
  -e AWS_ACCESS_KEY_ID=<your-key> \
  -e AWS_SECRET_ACCESS_KEY=<your-secret> \
  -e AWS_SESSION_TOKEN=<your-token> \
  -e AWS_DEFAULT_REGION=us-west-2 \
  -e CHAINLIT_AUTH_SECRET=<your-secret> \
  -e LANGFUSE_SECRET_KEY=<your-key> \
  -e LANGFUSE_PUBLIC_KEY=<your-key> \
  -e LANGFUSE_HOST=<your-host> \
  nutritrack
```

### AWS Deployment

For AWS deployment, consider:
- AWS App Runner for simple, managed deployment
- AWS ECS for more control and integration
- AWS Lambda for a serverless architecture

## Security Considerations

### Secret Management

- Use environment variables for all secrets
- Never store secrets in the source code
- Use AWS Secrets Manager or similar solutions in production

### Input Validation

- Validate all user inputs before processing
- Limit uploaded file sizes
- Clean text inputs

### Authentication

The current authentication is basic and suitable for the hackathon. For production:
- Implement more robust authentication (OAuth, JWT)
- Add session management
- Configure session expiration timeouts

## Troubleshooting

### Common Issues

#### 1. "Too many packets" Error

**Symptom**: Error when sending to Claude 3.7
**Cause**: Image too large or too numerous
**Solution**: Check image compression and limit to a single image per request

#### 2. "Missing Authentication Token" Error

**Symptom**: Failed authentication with AWS Bedrock
**Cause**: Missing or invalid AWS keys
**Solution**: Check AWS_* environment variables

#### 3. AWS Quota Exceeded

**Symptom**: "ThrottlingException" error
**Cause**: Too many requests to Claude 3.7
**Solution**: Implement a queuing or rate limiting system

#### 4. Images Not Processed

**Symptom**: Uploaded images are not analyzed
**Cause**: Unsupported image format or extraction error
**Solution**: Check logs and ensure format is supported (JPG, PNG)

### Logging

To improve diagnostics, add structured logs:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use the logger
logger = logging.getLogger(__name__)
logger.info("Informative message")
logger.error("Error: %s", str(error))
``` 