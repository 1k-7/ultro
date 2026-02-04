from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from utils import ultroid_cmd, eor

# --- DB Logic ---
async def get_echo_list(chat_id):
    data = await db.get_key("ECHO") or {}
    return data.get(str(chat_id), [])

async def toggle_echo(chat_id, user_id, add=True):
    data = await db.get_key("ECHO") or {}
    chat_str = str(chat_id)
    if chat_str not in data:
        data[chat_str] = []
        
    if add:
        if user_id not in data[chat_str]:
            data[chat_str].append(user_id)
    else:
        if user_id in data[chat_str]:
            data[chat_str].remove(user_id)
            
    await db.set_key("ECHO", data)

# --- Commands ---

@ultroid_cmd("echo")
async def echo_cmd(client: Client, message: Message):
    """
    Echo messages from a user.
    Usage: .echo (Reply to user)
    """
    if not message.reply_to_message:
        return await eor(message, "❌ Reply to a user.")
        
    user_id = message.reply_to_message.from_user.id
    if user_id == client.me.id:
        return await eor(message, "❌ Cannot echo self.")
        
    echo_list = await get_echo_list(message.chat.id)
    
    if user_id in echo_list:
        await toggle_echo(message.chat.id, user_id, add=False)
        await eor(message, f"❌ **Echo Stopped** for `{user_id}`")
    else:
        await toggle_echo(message.chat.id, user_id, add=True)
        await eor(message, f"✅ **Echo Started** for `{user_id}`")

@ultroid_cmd("listecho")
async def list_echo_cmd(client: Client, message: Message):
    echo_list = await get_echo_list(message.chat.id)
    if not echo_list:
        return await eor(message, "❌ No users being echoed.")
    
    await eor(message, f"📢 **Echo List:**\n`{echo_list}`")

# --- Watcher ---

@Client.on_message(filters.text & filters.group, group=4)
async def echo_watcher(client: Client, message: Message):
    if not message.from_user: return
    
    echo_list = await get_echo_list(message.chat.id)
    if message.from_user.id in echo_list:
        try:
            await message.reply_text(message.text, quote=True)
        except:
            pass