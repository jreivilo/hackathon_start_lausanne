import chainlit as cl

from src.handler.message_handler import process_message


@cl.on_message
async def main(message: cl.Message):
    """
    Main entry point for handling incoming messages from Chainlit.
    """
    # Process the message and get a response
    response_text, elements = await process_message(message)
    
    # Send the response back to the user
    await cl.Message(
        content=response_text,
        elements=elements
    ).send()