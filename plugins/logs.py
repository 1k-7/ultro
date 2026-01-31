import os
from utils import ultroid_cmd, eor

@ultroid_cmd("logs")
async def logs_handler(client, message):
    """
    Usage: .logs
    Uploads the current log file.
    """
    # Assuming standard pyrogram logging or custom file
    # If using Docker, logs usually go to stdout, but we can try to read previous files
    # Or if you set up logging to file in main.py
    
    log_file = "pyroblack.log" 
    
    # Note: In the main.py provided earlier, we used basicConfig to stdout.
    # To make this work, update main.py to save to file (see below note).
    
    if os.path.exists(log_file):
        await message.reply_document(
            log_file, 
            caption="**System Logs**"
        )
    else:
        # Fallback: Read local 'nohup.out' or similar if existing
        await eor(message, "Log file not found. (Are you logging to a file?)")

@ultroid_cmd("die")
async def die_handler(client, message):
    """
    Usage: .die
    Kill the bot process (Shutdown).
    """
    await eor(message, "Shutting down... Goodbye!")
    os.abort()