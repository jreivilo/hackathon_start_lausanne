import chainlit as cl
import asyncio

from src.handlers.message_handler import process_message

import chainlit as cl
from chainlit import AskUserMessage, Message, on_chat_start

from typing import Optional
import chainlit as cl

from langfuse import Langfuse
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the keys from environment variables
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
host = os.getenv("LANGFUSE_HOST")

langfuse = Langfuse(
	secret_key=secret_key,
	public_key=public_key,
	host=host
)

@cl.password_auth_callback
def auth_callback(username: str, password: str):
	# Fetch the user matching username from your database
	# and compare the hashed password with the value stored in the database
	if (username, password) == ("admin", "admin"):
		return cl.User(
			identifier="admin", metadata={"role": "admin", "provider": "credentials"}
		)
	elif (username, password) == ("user", "user"):
		return cl.User(
			identifier="user", metadata={"role": "user", "provider": "credentials"}
		)
	elif (username, password) == ("user1", "password1"):
		return cl.User(
			identifier="user1", metadata={"role": "user", "provider": "credentials"}
		)
	elif (username, password) == ("user2", "password2"):
		return cl.User(
			identifier="user2", metadata={"role": "user", "provider": "credentials"}
		)
	else:
		return None

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
	# Get user id
	user_id = message.user.id
	print(f"User ID: {user_id}")

	# Create a loading message with initial text
	loading_msg = cl.Message(content="⏳ Initializing request...")
	loading_msg_id = await loading_msg.send()
	
	# Define progress steps
	progress_steps = [
		"🔍 Analyzing your request...",
		"📸 Processing image data..." if message.elements else "🧠 Thinking...",
		"📊 Extracting nutritional information...",
		"📝 Formulating response...",
		"✨ Almost done..."
	]
	
	try:
		# Process each step with visible progress
		for i, step in enumerate(progress_steps):
			# Update message with current step
			loading_msg.content = step
			await loading_msg.update()
			
			# Simulate processing time for each step (except the last one)
			if i < len(progress_steps) - 1:
				await asyncio.sleep(1.5)
		
		# Process the message and get a response
		response_text, elements = await process_message(message)
		
		# Update the loading message with the final response
		loading_msg.content = response_text
		if elements:
			loading_msg.elements = elements
		await loading_msg.update()
	except Exception as e:
		# Update with error message
		loading_msg.content = f"❌ An error occurred: {str(e)}"
		await loading_msg.update()

async def animate_progress(message, message_id, steps):
	"""
	Animates the progress message by updating it with different steps.
	
	Args:
		message: The message object to update
		message_id: The ID of the message
		steps: List of step messages to display
	"""
	try:
		for step in steps:
			# Update message with current step
			message.content = step
			await message.update()
			
			# Wait for a short time before next update
			await asyncio.sleep(1.5)
		
		# If we've gone through all steps but processing is still ongoing,
		# show a cycling animation
		dots = 1
		while True:
			dot_text = "." * dots
			message.content = f"⏳ Finalizing{dot_text}"
			await message.update()
			dots = (dots % 3) + 1
			await asyncio.sleep(0.8)
	except asyncio.CancelledError:
		# Task was cancelled, which is expected when processing completes
		pass
	except Exception as e:
		# Log any unexpected errors
		print(f"Animation error: {e}")

@cl.action_callback("upvote")
async def upvote_callback(action: cl.Action):
	"""
	Handles the upvote action.
	"""
	await cl.Message(content="Thank you for your positive feedback!").send()

@cl.action_callback("downvote")
async def downvote_callback(action: cl.Action):
	"""
	Handles the downvote action.
	"""
	await cl.Message(content="We'll do better next time!").send()

@cl.on_chat_end
async def on_chat_end():
	"""
	Cleanup tasks when the chat ends.
	"""
	pass