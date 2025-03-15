from src.utils.bedrock_runtime import get_bedrock_runtime
from src.model.claude.query_claude_3_7 import query_claude_3_7

import chainlit as cl
import base64


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Check if message contains images
    if message.elements:
        # Process message with images
        elements = []
        image_list = []

        for element in message.elements:
            if isinstance(element, cl.Image):
                # Add image to response elements
                elements.append(element)

                # Get image data for Claude
                image_data = element.path
                with open(image_data, "rb") as img_file:
                    base64_image = base64.b64encode(img_file.read()).decode("utf-8")
                    image_list.append(base64_image)

        # Get text response from Claude with images
        response_json = query_claude_3_7(message.content, image_list)
        response_text = response_json['content'][0]['text']
        print(response_text)

        # Send response with both text and images
        await cl.Message(
            content=response_text,
            elements=elements
        ).send()
    else:
        # Process text-only message
        response_json = query_claude_3_7(message.content)
        response_text = response_json['content'][0]['text']
        print(response_text)
        await cl.Message(
            content=response_text
        ).send()