import re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database import db
from utils import ultroid_cmd, eor

# --- Database Logic ---

async def get_blacklist(chat_id):
    """Returns a list of blacklisted trigger words for the chat."""
    data = await db.get_key("BLACKLIST") or {}
    return data.get(str(chat_id), [])

async def add_blacklist_db(chat_id, word):
    """Adds a word to the blacklist."""
    data = await db.get_key("BLACKLIST") or {}
    chat_str = str(chat_id)
    if chat_str not in data:
        data[chat_str] = []
    
    if word not in data[chat_str]:
        data[chat_str].append(word)
        await db.set_key("BLACKLIST", data)
        return True
    return False

async def rem_blacklist_db(chat_id, word):
    """Removes a word from the blacklist."""
    data = await db.get_key("BLACKLIST") or {}
    chat_str = str(chat_id)
    if chat_str in data and word in data[chat_str]:
        data[chat_str].remove(word)
        if not data[chat_str]:
            del data[chat_str]
        await db.set_key("BLACKLIST", data)
        return True
    return False

# --- Helper ---

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False

# --- Commands ---

@ultroid_cmd("blacklist")
async def add_bl(client: Client, message: Message):
    """
    Add words to blacklist.
    Usage: .blacklist <word1> <word2>
    """
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await eor(message, "❌ **Admin Only!**")

    if len(message.command) < 2:
        return await eor(message, "Usage: `.blacklist word`")
    
    words = message.text.split(None, 1)[1].lower().split()
    chat_id = message.chat.id
    
    for w in words:
        await add_blacklist_db(chat_id, w)
        
    await eor(message, f"🚫 **Added to Blacklist:** `{', '.join(words)}`")

@ultroid_cmd("remblacklist")
async def rem_bl(client: Client, message: Message):
    """
    Remove words from blacklist.
    Usage: .remblacklist <word1> <word2>
    """
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await eor(message, "❌ **Admin Only!**")

    if len(message.command) < 2:
        return await eor(message, "Usage: `.remblacklist word`")
        
    words = message.text.split(None, 1)[1].lower().split()
    chat_id = message.chat.id
    removed = []
    
    for w in words:
        if await rem_blacklist_db(chat_id, w):
            removed.append(w)
            
    if removed:
        await eor(message, f"🗑 **Removed from Blacklist:** `{', '.join(removed)}`")
    else:
        await eor(message, "⚠️ Words not found in blacklist.")

@ultroid_cmd("listblacklist")
async def list_bl(client: Client, message: Message):
    """
    List blacklisted words.
    """
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await eor(message, "❌ **Admin Only!**")
        
    bl_list = await get_blacklist(message.chat.id)
    if not bl_list:
        return await eor(message, "✅ No blacklisted words in this chat.")
        
    await eor(message, f"🚫 **Blacklisted Words:**\n\n`{', '.join(bl_list)}`")

# --- Watcher ---

@Client.on_message(filters.text & filters.group, group=2)
async def blacklist_watcher(client: Client, message: Message):
    """
    Checks messages against blacklist and deletes matches.
    """
    if not message.chat or not message.text: return
    
    # Skip admins/self
    if message.from_user:
        if message.from_user.is_self: return
        if await is_admin(client, message.chat.id, message.from_user.id): return
        
    bl_list = await get_blacklist(message.chat.id)
    if not bl_list: return
    
    text = message.text.lower()
    
    for bad_word in bl_list:
        # Regex to match exact word boundary to prevent false positives (e.g. 'ass' in 'class')
        # handles punctuation like "badword!" correctly.
        pattern = r"(^|\W)" + re.escape(bad_word) + r"(\W|$)"
        if re.search(pattern, text):
            try:
                await message.delete()
            except:
                pass
            break