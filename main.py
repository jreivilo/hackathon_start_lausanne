from src.utils.bedrock_runtime import get_bedrock_runtime
from src.model.query_claude_3_7 import query_claude_3_7

import chainlit as cl


@cl.on_message
async def main(msg: cl.Message):
	# Check if there is an image uploaded
	if msg.elements:
		# Filter out image files based on their MIME types
		images = [file for file in msg.elements if "image" in file.mime]
		print(F"An image was uploaded: {images[0].url}")
		await cl.Message(content="I see you uploaded an image!").send()

	# Send a response back to the user
	response_json = query_claude_3_7(msg.content)
	response_text = response_json['content'][0]['text']
	print(response_text)
	await cl.Message(
		content=response_text
	).send()