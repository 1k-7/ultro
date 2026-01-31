from datetime import datetime
from utils import ultroid_cmd, eor

@ultroid_cmd("ping")
async def ping_handler(client, message):
    """
    Usage: .ping
    Checks the bot's response speed.
    """
    start = datetime.now()
    
    # Use our custom eor function
    msg = await eor(message, "Pong!")
    
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    
    await msg.edit(f"**Pong!**\nResponse: `{ms}ms`")