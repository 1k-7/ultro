from utils import ultroid_cmd, eor
from database import db

@ultroid_cmd("setvar")
async def set_var_handler(client, message):
    """
    Usage: .setvar <key> <value>
    Saves a value to the DB (Redis or Mongo).
    """
    if len(message.command) < 3:
        return await eor(message, "Usage: `.setvar key value`")
        
    key = message.command[1]
    value = message.text.split(maxsplit=2)[2]
    
    await db.set_key(key, value)
    await eor(message, f"Saved to DB:\n**{key}** = `{value}`")

@ultroid_cmd("getvar")
async def get_var_handler(client, message):
    """
    Usage: .getvar <key>
    Retrieves a value from the DB.
    """
    if len(message.command) < 2:
        return await eor(message, "Usage: `.getvar key`")
        
    key = message.command[1]
    
    value = await db.get_key(key)
    
    if value:
        await eor(message, f"Value for **{key}**:\n`{value}`")
    else:
        await eor(message, f"No value found for **{key}**")

@ultroid_cmd("delvar")
async def del_var_handler(client, message):
    """
    Usage: .delvar <key>
    Deletes a value from the DB.
    """
    if len(message.command) < 2:
        return await eor(message, "Usage: `.delvar key`")

    key = message.command[1]
    await db.del_key(key)
    await eor(message, f"Deleted **{key}** from DB.")