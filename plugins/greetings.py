from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database import db
from utils import ultroid_cmd, eor

# --- DB Logic ---
async def get_greeting(chat_id, type_):
    data = await db.get_key(f"GREETING_{type_}") or {}
    return data.get(str(chat_id))

async def set_greeting(chat_id, type_, text):
    data = await db.get_key(f"GREETING_{type_}") or {}
    data[str(chat_id)] = text
    await db.set_key(f"GREETING_{type_}", data)

async def del_greeting(chat_id, type_):
    data = await db.get_key(f"GREETING_{type_}") or {}
    if str(chat_id) in data:
        del data[str(chat_id)]
        await db.set_key(f"GREETING_{type_}", data)
        return True
    return False

# --- Commands ---

@ultroid_cmd("setwelcome")
async def set_welcome(client, message):
    """Set welcome message. Use {mention} or {firstname}."""
    if len(message.command) < 2:
        return await eor(message, "Usage: `.setwelcome Hello {mention}!`")
    
    text = message.text.split(None, 1)[1]
    await set_greeting(message.chat.id, "WELCOME", text)
    await eor(message, "✅ **Welcome message set!**")

@ultroid_cmd("clearwelcome")
async def clear_welcome(client, message):
    if await del_greeting(message.chat.id, "WELCOME"):
        await eor(message, "🗑 **Welcome message deleted.**")
    else:
        await eor(message, "⚠️ No welcome message found.")

@ultroid_cmd("setgoodbye")
async def set_goodbye(client, message):
    """Set goodbye message."""
    if len(message.command) < 2:
        return await eor(message, "Usage: `.setgoodbye Bye {firstname}!`")
    
    text = message.text.split(None, 1)[1]
    await set_greeting(message.chat.id, "GOODBYE", text)
    await eor(message, "✅ **Goodbye message set!**")

@ultroid_cmd("cleargoodbye")
async def clear_goodbye(client, message):
    if await del_greeting(message.chat.id, "GOODBYE"):
        await eor(message, "🗑 **Goodbye message deleted.**")
    else:
        await eor(message, "⚠️ No goodbye message found.")

# --- Watcher ---

@Client.on_message(filters.new_chat_members, group=5)
async def welcome_watcher(client, message):
    welcome_text = await get_greeting(message.chat.id, "WELCOME")
    if not welcome_text: return
    
    for member in message.new_chat_members:
        if member.is_self: continue
        try:
            # Formatting
            txt = welcome_text.format(
                mention=member.mention,
                firstname=member.first_name,
                username=member.username or "",
                id=member.id
            )
            await client.send_message(message.chat.id, txt)
        except Exception as e:
            print(f"Welcome Error: {e}")

@Client.on_message(filters.left_chat_member, group=6)
async def goodbye_watcher(client, message):
    goodbye_text = await get_greeting(message.chat.id, "GOODBYE")
    if not goodbye_text: return
    
    member = message.left_chat_member
    if member.is_self: return
    
    try:
        txt = goodbye_text.format(
            mention=member.mention,
            firstname=member.first_name,
            username=member.username or "",
            id=member.id
        )
        await client.send_message(message.chat.id, txt)
    except Exception as e:
        print(f"Goodbye Error: {e}")