from src.utils.bedrock_runtime import get_bedrock_runtime
from src.model.query_claude_3_7 import query_claude_3_7

import chainlit as cl


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
	response_json = query_claude_3_7(message.content)
	response_text = response_json['content'][0]['text']
	print(response_text)
	await cl.Message(
		content=response_text
	).send()