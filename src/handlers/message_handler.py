import json

import chainlit as cl

from src.model.query_claude_3_7 import query_claude_3_7, function_calling_query, create_bedrock_payload
from src.utils.image_processor import extract_images
from src.config.schemas import get_analysis_schema


# Global variable to store the last JSON response
last_json_response = None

async def process_message(message: cl.Message, trace, consumed_products):
	"""
	Process incoming messages and generate appropriate responses.

	Args:
		message: The incoming Chainlit message

	Returns:
		Tuple containing response text and elements to display
	"""
	global last_json_response

	# Check if message contains images
	if message.elements:
		span = trace.span(
			name = "Extract images from message",
			input = message.elements
		)
		# Extract images from message
		elements, image_list = extract_images(message.elements)
		span.end(
			output = image_list
		)

		# Get structured response from Claude with images
		function_response = function_calling_query(
			input_text=message.content,
			json_schema=get_analysis_schema(),
			images=image_list,
			trace=trace
		)

		# Store the JSON response
		last_json_response = function_response.get("structured_data", {})

		# Extract structured data and explanation
		structured_data = last_json_response
		explanation = function_response.get("explanation", "")

		# Build an enriched response
		response_text = explanation
	else:
		if last_json_response:
			# Use the last JSON response to make a new query to Claude
			explanation_prompt = f"""
			Here is the last known product information:
			
			```json
			{json.dumps(last_json_response, ensure_ascii=False, indent=2)}
			```
			
			User question: {message.content}
			
			Please provide insights and explanations based on this data and the user's question.
			Keep your response clear, precise, and concise - no more than 3-4 sentences.
			Respond in the same language as the user's question.
			"""

			# Create payload using create_bedrock_payload
			span = trace.span(
				name="Create payload for Bedrock",
				input=explanation_prompt
			)

			explanation_response = query_claude_3_7(explanation_prompt, None, trace, goal="Answer user question")

			response_text = explanation_response['content'][0]['text']
			span.end(
				output=response_text
			)
			elements = None
		else:
			# Safe approach: don't try to check length or iterate if type is unknown
			try:
				# Check if consumed_products is a valid iterable (like list or dict)
				consumed_products_info = ""
				has_products = False

				print(f"Processing consumed products: {consumed_products}")

				# Try to safely iterate through products if they exist
				try:
					if consumed_products:
						iterator = iter(consumed_products)
						has_products = True
						print("Successfully validated consumed_products as iterable")
				except (TypeError, ValueError) as e:
					# If consumed_products is not iterable or empty
					has_products = False
					print(f"Error validating consumed_products: {e}")

				if has_products:
					print("Building consumption history summary...")
					consumed_products_info = "\nUser's previously consumed products:\n"
					total_calories = 0
					total_protein = 0
					total_carbs = 0
					total_fat = 0

					for i, product in enumerate(consumed_products):
						print(f"Processing product {i+1}: {product}")
						if isinstance(product, dict) and 'product' in product:
							product_name = product.get('product', {}).get('name', 'Unknown Product')
							nutritive_values = product.get('product', {}).get('nutritive_value', {})
							calories = nutritive_values.get('calories', 0)
							protein = nutritive_values.get('protein', 0)
							carbs = nutritive_values.get('carbohydrates', 0)
							fat = nutritive_values.get('fat', 0)

							print(f"Extracted values for {product_name}: cal={calories}, prot={protein}, carbs={carbs}, fat={fat}")

							# Add to totals
							total_calories += calories
							total_protein += protein
							total_carbs += carbs
							total_fat += fat

							# Add detailed product info
							consumed_products_info += f"{i+1}. {product_name}:\n"
							consumed_products_info += f"   - Calories: {calories} kcal\n"
							consumed_products_info += f"   - Protein: {protein} g\n"
							consumed_products_info += f"   - Carbohydrates: {carbs} g\n"
							consumed_products_info += f"   - Fat: {fat} g\n"

					print(f"Daily totals calculated: cal={total_calories}, prot={total_protein}, carbs={total_carbs}, fat={total_fat}")

					# Add daily totals summary
					consumed_products_info += f"\nDaily totals so far:\n"
					consumed_products_info += f"- Total Calories: {total_calories} kcal\n"
					consumed_products_info += f"- Total Protein: {total_protein} g\n"
					consumed_products_info += f"- Total Carbohydrates: {total_carbs} g\n"
					consumed_products_info += f"- Total Fat: {total_fat} g\n"
					consumed_products_info += f"- Approximate % of 2000 kcal diet: {(total_calories/2000)*100:.1f}%\n"


				prompt = f"""
				The user has the following consumption history:
				
				{consumed_products_info}
				User question: {message.content if message.content else "No question provided"}
				
				Please provide insights and recommendations based on their consumption history and question.
				If the user hasn't provided any message content, suggest they can:
				- Upload a photo of their food to analyze nutritional content
				- Ask questions about their consumption history
				- Get recommendations based on their goals
				- Request calculations or insights about specific foods
				
				If they're asking about a new product but haven't provided an image, kindly remind them to share an image.
				Keep your response clear, precise, and concise - no more than 3-4 sentences.
				Respond in the same language as the user's question.
				"""

				print("Preparing to query Claude with consumption history...")


				response = query_claude_3_7(prompt, None, trace, goal="Answer based on consumption history")

				print(f"Claude response received: {response}")
				response_text = response['content'][0]['text']

				elements = []

			except Exception as e:
				# Fallback in case of any error
				print(f"Error processing consumption data: {e}")
				span = trace.span(
					name="No image or previous JSON",
					input=message
				)
				response_text = "Hello! If you have a question about a product's nutrition, please share an image of the product, and I'll be happy to assist you."
				elements = []
				span.end(
					output=response_text
				)

	# Log structured data for debugging
	if last_json_response:
		print(f"Structured data: {json.dumps(last_json_response, indent=2)}")

	return response_text, elements, last_json_response

def format_response(structured_data, explanation):
	"""
	Format the response text with structured data and explanation.
	"""
	return f"""
### Response
{structured_data.get('product', {}).get('name', 'No product name available')}

### Additional Details
{explanation}
	"""