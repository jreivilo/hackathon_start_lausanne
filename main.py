import chainlit as cl

from src.handlers.message_handler import process_message

import chainlit as cl
from chainlit import AskUserMessage, Message, on_chat_start

@on_chat_start
async def main():
	content = (
		"Welcome! I'm your personal wellness coach, here to help you decode the nutritive aspects of food and its ingredients. "
		"For the best advice, please share some details about your general health condition. \n\n"
	)

	await Message(
		content=content + "Let's get started on optimizing your nutrition! Please provide me with pictures of the food you are consuming today."
	).send()


@cl.on_message
async def main(message: cl.Message):
	"""
	Main entry point for handling incoming messages from Chainlit.
	"""
	# Create a loading message
	loading_msg = await cl.Message(content="⏳ Génération de la réponse...").send()
	
	# Process the message and get a response
	response_text, elements = await process_message(message)
	
	# Delete the loading message
	await loading_msg.remove()

	# Send the final response
	await cl.Message(
		content=response_text,
		elements=elements,
		actions=[
			cl.Action(name="upvote", label="👍 The response is great!", payload={"vote": "up"}),
			cl.Action(name="downvote", label="👎 Oh no...", payload={"vote": "down"})
		]
	).send()

@cl.action_callback("upvote")
async def upvote_callback(action: cl.Action):
	"""
	Handles the upvote action.
	"""
	await cl.Message(content="Merci pour ton retour positif!").send()

@cl.action_callback("downvote")
async def downvote_callback(action: cl.Action):
	"""
	Handles the downvote action.
	"""
	await cl.Message(content="On va faire mieux la prochaine fois!").send()
