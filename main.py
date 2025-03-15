import chainlit as cl

from src.handlers.message_handler import process_message



#

@cl.on_message
async def main(message: cl.Message):
    """
    Main entry point for handling incoming messages from Chainlit.
    """
    # Process the message and get a response
    response_text, elements = await process_message(message)

    # Send the response back to the user with Upvote and Downvote buttons
    await cl.Message(
        content=response_text,
        elements=elements,
        actions=[
            cl.Action(name="upvote", label="👍 La réponse est top!", payload={"vote": "up"}),
            cl.Action(name="downvote", label="👎 Aie aie aie ...", payload={"vote": "down"})
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
