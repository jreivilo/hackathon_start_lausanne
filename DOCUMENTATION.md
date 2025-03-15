# NutriTrack Project Documentation - Hackathon Start Lausanne 2025

## 🔍 Project Overview

NutriTrack is a conversational web application that allows users to analyze nutritional information of food products from photos. Developed for the Hackathon Start Lausanne 2025, this application uses artificial intelligence to extract nutritional data from food product images and help users track their daily consumption.

## 🏗️ System Architecture

### Overview

The application is built with the following technologies:

- **Backend**: Python with a conversational chat framework (Chainlit)
- **AI**: Claude 3.7 Sonnet via AWS Bedrock for image analysis and response generation
- **Monitoring**: Langfuse for tracing and performance analytics
- **Deployment**: Docker for containerization

### Component Diagram

```
                      +---------------+
                      |               |
                      |   Interface   |
                      |   Chainlit    |
                      |               |
                      +-------+-------+
                              |
                              v
+------------+        +---------------+        +--------------+
|            |        |               |        |              |
|  Memory    | <----> |  Application  | <----> |    Claude    |
|  Storage   |        |    Logic      |        |    3.7 API   |
|            |        |               |        |              |
+------------+        +-------+-------+        +--------------+
                              |
                              v
                      +---------------+
                      |               |
                      |    Langfuse   |
                      |   Analytics   |
                      |               |
                      +---------------+
```

## 📁 Project Structure

```
.
├── .chainlit/                # Chainlit configuration
├── .env                      # Environment variables
├── .env.template             # Template for environment variables
├── Dockerfile                # Docker configuration
├── README.md                 # Basic documentation
├── chainlit.config.py        # Chainlit configuration
├── chainlit.md               # Chainlit welcome page
├── main.py                   # Main entry point
├── pyproject.toml            # Project configuration and dependencies
├── src/                      # Source code
│   ├── config/               # Configuration
│   │   └── schemas.py        # JSON schemas for AI
│   ├── handlers/             # Request handlers
│   │   └── message_handler.py # Message handler
│   ├── model/                # AI models
│   │   └── query_claude_3_7.py # Claude 3.7 integration
│   └── utils/                # Utilities
│       ├── bedrock_runtime.py # AWS Bedrock client
│       └── image_processor.py # Image processing
└── uv.lock                   # Dependency lock for uv
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.12
- AWS account with Bedrock access (for Claude 3.7)
- Langfuse account (for monitoring)

### Installation Instructions

1. **Install `uv`**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Generate Chainlit Secret**
   ```bash
   uv run chainlit secret
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.template .env
   ```
   
   Then modify the `.env` file with your own values:
   - AWS_DEFAULT_REGION
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_SESSION_TOKEN
   - CHAINLIT_AUTH_SECRET
   - LANGFUSE_SECRET_KEY
   - LANGFUSE_PUBLIC_KEY
   - LANGFUSE_HOST

5. **Launch the Application**
   ```bash
   uv run chainlit run main.py -w
   ```

## 📦 Main Components

### 1. Message Handling (`src/handlers/message_handler.py`)

This module processes incoming user messages:
- Extract images from messages
- Send images and text to Claude 3.7 for analysis
- Build and return structured responses
- Maintain history of products consumed by each user

#### Main functions:
- `process_message()`: Processes messages and generates responses
- `format_response()`: Formats a response with nutritional data

### 2. Claude 3.7 Integration (`src/model/query_claude_3_7.py`)

This module manages interaction with the Claude 3.7 API via AWS Bedrock:
- Creation of payloads for the Bedrock API
- Sending requests with text and images
- Structured queries with function calling
- Processing AI responses

#### Main functions:
- `create_bedrock_payload()`: Prepares data for the Bedrock API
- `invoke_claude_model()`: Calls the Claude 3.7 API
- `query_claude_3_7()`: Main function to query Claude
- `function_calling_query()`: Queries with "function calling" to obtain structured data

### 3. Image Processing (`src/utils/image_processor.py`)

This module handles image processing before sending to the AI:
- Image compression to respect size limits
- Format conversion
- Extraction of images from Chainlit elements

#### Main functions:
- `compress_image()`: Compresses images for the Claude API
- `extract_images()`: Extracts images from Chainlit messages

### 4. Configuration (`src/config/schemas.py`)

Defines JSON schemas to structure AI responses:
- Schema for nutritional information
- Food product structure

#### Main functions:
- `get_analysis_schema()`: Returns the JSON schema for product analysis

### 5. AWS Bedrock Client (`src/utils/bedrock_runtime.py`)

Configures connection to AWS Bedrock:
- AWS client initialization
- Authentication information management

#### Main functions:
- `get_bedrock_runtime()`: Initializes and returns the Bedrock client

### 6. Main Application (`main.py`)

Entry point of the application:
- Chainlit configuration
- Authentication management
- Special command processing
- User action management (add/skip a product)

## 👤 Authentication and Users

The application implements simple credential-based authentication:
- admin/admin (administrator role)
- user/user (user role)
- user1/password1 (user role)
- user2/password2 (user role)

Each user has their own consumption history stored in memory.

## 🔄 Data Flow

1. User sends a message with or without an image
2. The message is processed by `process_message()` in `message_handler.py`
3. If an image is present:
   - The image is extracted and compressed
   - The image and text are sent to Claude 3.7 for analysis
   - Claude 3.7 generates a structured response via function calling
4. If no image is present:
   - If products have been previously analyzed, this information is used
   - Claude 3.7 is queried to provide a response based on history
5. The response is sent back to the user
6. The user can choose to add or skip the analyzed product

## 🔍 Monitoring and Analytics

The application uses Langfuse for tracing and monitoring:
- Each user session is traced
- Inputs and outputs of Claude 3.7 calls are recorded
- Performance and metrics are available in the Langfuse dashboard

## 🐳 Docker Deployment

The application can be deployed via Docker:
```bash
# Build the image
docker build -t nutritrack .

# Run the container
docker run -p 8080:8080 nutritrack
```

## 💡 Special Commands

The application supports special commands via Chainlit "starters":
- `!view_consumption`: Displays consumed products
- `!analyze_product`: Prompts to upload an image for analysis
- `!nutrition_summary`: Generates a nutritional summary of consumed products
- `!healthy_alternatives`: Suggests healthier alternatives

## 🧑‍💻 Development Team

- **Jérémy Olivier**
- **Alexandre Mugg**
- **Isabel Tovar**
- **Jérémy Dos Santos**

## 📋 Best Practices for Contributors

1. **Environment Variables**: Never commit secrets or credentials in the code
2. **Image Processing**: Ensure images are properly compressed before sending to Claude
3. **Traces**: Always use Langfuse spans to trace important operations
4. **Error Handling**: Capture and log all exceptions
5. **Comments**: Keep code documentation up to date 