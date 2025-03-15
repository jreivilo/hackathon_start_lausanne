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

# Simple in-memory storage for user IDs
dict_user_ids = {}

def get_or_create_user_id(user_name: str) -> int:
	"""
	Get or create a user ID for the given user name.
	
	Args:
		user_name: The user name to get or create an ID for.
	
	Returns:
		int: The user ID.
	"""
	print(f"User name: {user_name}")
	if user_name not in dict_user_ids:
		dict_user_ids[user_name] = len(dict_user_ids) + 1
	return dict_user_ids[user_name]

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



# @on_chat_start
# async def main():
# 	content = (
# 		"Welcome! I'm your personal wellness coach, here to help you decode the nutritive aspects of food and its ingredients. "
# 		"For the best advice, please share some details about your general health condition. \n\n"
# 	)

# 	await Message(
# 		content=content + "Let's get started on optimizing your nutrition! Please provide me with pictures of the food you are consuming today."
# 	).send()


@cl.on_message
async def main(message: cl.Message):
	"""
	Main entry point for handling incoming messages from Chainlit.
	"""
	global last_json_response

	# Intercepter les commandes spéciales des starters
	if message.content.startswith("!"):
		await handle_starter_command(message)
		return

	session_id = cl.user_session.get("id")
	user_name = cl.user_session.get("user").identifier
	user_id = get_or_create_user_id(user_name)

	print(f"Received message from {user_name} (session ID: {session_id})")
	print(f"Message content: {message.content}")

	trace = langfuse.trace(
		name="Question",
		input=message.content,
		session_id=session_id,
		user_id=user_id,
	)

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
		
		# Initialize consumed_products for this user if it doesn't exist
		if user_id not in consumed_products:
			consumed_products[user_id] = []
		
		# Process the message and get a response
		response = await process_message(message, trace, consumed_products[user_id])
		
		# Unpack the response
		response_text, elements = response[:2]
		last_json_response = response[2] if len(response) > 2 else None

		# Determine actions based on last_json_response
		actions = []
		if last_json_response:
			user_id = cl.user_session.get("user").identifier  # Get the user identifier
			actions = [
				cl.Action(
					name="add_product", 
					label="✅ Add current product to my list",
					payload={"action": "add", "product_data": last_json_response, "user_id": user_id}
				),
				cl.Action(
					name="skip_product", 
					label="❌ Skip",
					payload={"action": "skip", "user_id": user_id}
				)
			]

		# Create a new message with the final response and product tracking buttons if applicable
		final_msg = cl.Message(
			content=response_text,
			elements=elements,
			actions=actions
		)
		await final_msg.send()
		
		# Remove the loading message
		await loading_msg.remove()

		# Add repopnse to the trace
		trace.update(output=response_text)
		trace.close()
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
			await asyncio.sleep(2.5)
		
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
	# Extract user identifier from the action payload
	user_id = action.payload.get("user_id")

	# Extract product information from the action payload
	product_data = action.payload.get("product_data", {})

	product_name = product_data.get("product", {}).get("name", "Unknown Product")

	# Add product to the user's list
	if user_id not in consumed_products:
		consumed_products[user_id] = []
	
	consumed_products[user_id].append(product_data)

	# Send confirmation message
	await cl.Message(content=f"✅ {product_name} has been added to your consumed list.").send()


	# Optionally, show the current list of consumed products for the user
	product_list = "\n".join([f"- {product.get('product', {}).get('name', 'Unknown Product')}" for product in consumed_products[user_id]])
	
	# Calculate total calories from all products in the user's list
	total_calories = 0
	for product in consumed_products[user_id]:
		if isinstance(product, dict) and 'product' in product:
			print(product.get('product', {}).get('nutritive_value', {}).get('calories', 0))
			total_calories += product.get('product', {}).get('nutritive_value', {}).get('calories', 0)
	
	await cl.Message(content=f"📋 Your current list:\n{product_list}\n\n"
					   f"📊 Total calories today: {total_calories} calories").send()

@cl.action_callback("skip_product")
async def skip_product_callback(action: cl.Action):
	"""
	Handles skipping a product (not adding it to the consumed list).
	"""
	await cl.Message(content="⏭️ Product not added to your list.").send()

@cl.on_chat_end
async def on_chat_end():
	"""
	Cleanup tasks when the chat ends.
	"""
	pass

@cl.set_starters
async def set_starters():
	return [
		cl.Starter(
			label="📋 View my daily consumption",
			message="!view_consumption",  # Message spécial qui sera intercepté
		),
		cl.Starter(
			label="🔍 Analyze a new product", 
			message="!analyze_product",  # Message spécial qui sera intercepté
		),
		cl.Starter(
			label="📊 Nutrition summary",
			message="!nutrition_summary",  # Message spécial qui sera intercepté
		),
		cl.Starter(
			label="💡 Healthy alternatives",
			message="!healthy_alternatives",  # Message spécial qui sera intercepté
		)
	]

async def handle_starter_command(message: cl.Message):
	"""
	Handle special commands triggered by starters.
	"""
	user_id = cl.user_session.get("user").identifier
	command = message.content.strip()

	if command == "!view_consumption":
		# Afficher la liste des produits consommés
		if user_id in consumed_products and consumed_products[user_id]:
			product_list = "\n".join([f"- {product.get('product', {}).get('name', 'Unknown Product')}" 
									 for product in consumed_products[user_id]])
			
			# Calculer le total des calories
			total_calories = 0
			for product in consumed_products[user_id]:
				if isinstance(product, dict) and 'product' in product:
					print(product)
					total_calories += product.get('product', {}).get('nutritive_value', {}).get('calories', 0)
			
			await cl.Message(content=f"📋 Your daily consumption:\n{product_list}\n\n"
									   f"📊 Total calories today: {total_calories} calories").send()
		else:
			await cl.Message(content="You haven't added any products to your list yet.").send()
	
	elif command == "!analyze_product":
		# Inviter l'utilisateur à télécharger une image ou décrire un produit
		await cl.Message(content="Please upload an image of the product you want to analyze, or describe it in detail.").send()
	
	elif command == "!nutrition_summary":
		# Générer un résumé nutritionnel
		if user_id in consumed_products and consumed_products[user_id]:
			# Calculer les totaux nutritionnels
			total_calories = 0
			total_protein = 0
			total_carbs = 0
			total_fat = 0
			
			for product in consumed_products[user_id]:
				if isinstance(product, dict) and 'product' in product:
					nutritive_values = product.get('product', {}).get('nutritive_value', {})
					total_calories += nutritive_values.get('calories', 0)
					total_protein += nutritive_values.get('protein', 0)
					total_carbs += nutritive_values.get('carbohydrates', 0)
					total_fat += nutritive_values.get('fat', 0)
			
			summary = f"""📊 **Nutrition Summary for Today**

**Total Calories:** {total_calories} kcal
**Total Protein:** {total_protein} g
**Total Carbohydrates:** {total_carbs} g
**Total Fat:** {total_fat} g

Based on a 2000 kcal diet, you've consumed approximately {(total_calories/2000)*100:.1f}% of your daily calorie needs.
"""
			await cl.Message(content=summary).send()
		else:
			await cl.Message(content="You haven't added any products to your list yet.").send()
	
	elif command == "!healthy_alternatives":
		# Suggérer des alternatives plus saines
		if user_id in consumed_products and consumed_products[user_id]:
			await cl.Message(content="Analyzing your consumption to suggest healthier alternatives...").send()
			# Ici, vous pourriez appeler une fonction qui génère des suggestions basées sur les produits consommés
			# Pour cet exemple, nous utilisons une réponse générique
			await cl.Message(content="Here are some healthier alternatives to consider for your next meals...").send()
		else:
			await cl.Message(content="You haven't added any products to your list yet.").send()