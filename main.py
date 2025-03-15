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

# Simple in-memory storage for consumed products
consumed_products = {}

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
		
		# Create a new message with the final response and product tracking buttons
		final_msg = cl.Message(
			content=response_text,
			elements=elements,
			actions=[
				cl.Action(
					name="add_product", 
					label="✅ Add current product to my list",
					payload={"action": "add"}
				),
				cl.Action(
					name="skip_product", 
					label="❌ Skip",
					payload={"action": "skip"}
				)
			]
		)
		await final_msg.send()
		
		# Remove the loading message
		await loading_msg.remove()
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

@cl.action_callback("add_product")
async def add_product_callback(action: cl.Action):
	"""
	Handles adding a product to the user's consumed products list.
	"""
	# user_id = action.from_user.identifier
	
	# # Get the product name from the message that triggered the action
	# product_name = "Unknown Product"  # Default value
	
	# # Try to extract product name from the message content
	# if action.message and action.message.content:
	# 	# Look for product name in the message content
	# 	content_lines = action.message.content.split('\n')
	# 	for line in content_lines:
	# 		if "Response" in line and len(line.split("Response")) > 1:
	# 			product_name = line.split("Response")[1].strip()
	# 			break
	
	# # Add to user's consumed products
	# if user_id not in consumed_products:
	# 	consumed_products[user_id] = []
	
	# consumed_products[user_id].append(product_name)
	
	# Send confirmation message
	await cl.Message(content=f"✅  a été ajouté à votre liste de produits consommés.").send()
	
	# # Show current list
	# product_list = "\n".join([f"- {product}" for product in consumed_products[user_id]])
	# await cl.Message(content=f"📋 Votre liste actuelle:\n{product_list}").send()

@cl.action_callback("skip_product")
async def skip_product_callback(action: cl.Action):
	"""
	Handles skipping a product (not adding it to the consumed list).
	"""
	await cl.Message(content="⏭️ Produit non ajouté à votre liste.").send()

@cl.on_chat_end
async def on_chat_end():
	"""
	Cleanup tasks when the chat ends.
	"""
	pass