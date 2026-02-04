import re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database import db
from utils import ultroid_cmd, eor

# --- Database Logic ---

async def get_all_filters():
    """
    Retrieves the entire FILTERS dictionary from the database.
    """
    return await db.get_key("FILTERS") or {}

async def add_filter_db(chat_id, word, text, media, button):
    """
    Adds a filter to the database.
    Structure: {chat_id: {word: {text, media, button}}}
    """
    all_filters = await get_all_filters()
    chat_str = str(chat_id)
    if chat_str not in all_filters:
        all_filters[chat_str] = {}
    
    all_filters[chat_str][word] = {
        "text": text,
        "media": media, # Storing file_id
        "button": button
    }
    await db.set_key("FILTERS", all_filters)

async def remove_filter_db(chat_id, word):
    """
    Removes a filter from the database.
    """
    all_filters = await get_all_filters()
    chat_str = str(chat_id)
    if chat_str in all_filters and word in all_filters[chat_str]:
        del all_filters[chat_str][word]
        await db.set_key("FILTERS", all_filters)
        return True
    return False

async def get_chat_filters(chat_id):
    """
    Retrieves filters specific to a chat.
    """
    all_filters = await get_all_filters()
    return all_filters.get(str(chat_id), {})

# --- Commands ---

@ultroid_cmd(pattern="addfilter", full_sudo=False)
async def add_filter(client: Client, message: Message):
    """
    Save a filter.
    Usage: .addfilter <trigger> (Reply to content)
    """
    # Check if a trigger word was provided
    if len(message.command) < 2:
        return await eor(message, "❌ **Usage:** `.addfilter <trigger>` (reply to a message).")
    
    # Extract trigger word (everything after the command)
    trigger = message.text.split(None, 1)[1].strip().lower()
    reply = message.reply_to_message
    
    if not reply:
        return await eor(message, "❌ **Error:** You must reply to a message to save it as a filter.")
    
    media_id = None
    msg_text = reply.caption or reply.text or ""
    
    # Detect Media and extract file_id
    if reply.media:
        # Check all standard media attributes in Pyrogram
        for attr in ["photo", "video", "audio", "voice", "document", "sticker", "animation", "video_note"]:
            media = getattr(reply, attr, None)
            if media:
                media_id = media.file_id
                break
                
    await add_filter_db(message.chat.id, trigger, msg_text, media_id, None)
    await eor(message, f"✅ **Filter Saved:** `{trigger}`")

@ultroid_cmd(pattern="remfilter")
async def rem_filter(client: Client, message: Message):
    """
    Remove a filter.
    Usage: .remfilter <trigger>
    """
    if len(message.command) < 2:
        return await eor(message, "❌ **Usage:** `.remfilter <trigger>`")
        
    trigger = message.text.split(None, 1)[1].strip().lower()
    
    if await remove_filter_db(message.chat.id, trigger):
        await eor(message, f"🗑 **Filter Removed:** `{trigger}`")
    else:
        await eor(message, f"⚠️ **Error:** Filter `{trigger}` not found.")

@ultroid_cmd(pattern="listfilter")
async def list_filter(client: Client, message: Message):
    """
    List all filters in the current chat.
    """
    filters_map = await get_chat_filters(message.chat.id)
    if not filters_map:
        return await eor(message, "❌ No filters found in this chat.")
    
    msg = "**Filters in this chat:**\n\n"
    for trigger in filters_map.keys():
        msg += f"👉 `{trigger}`\n"
        
    await eor(message, msg)

# --- Watcher ---

@Client.on_message(filters.text & filters.incoming & ~filters.bot, group=1)
async def filter_watcher(client: Client, message: Message):
    """
    Checks incoming messages for filter triggers.
    Running in group=1 to avoid blocking other handlers.
    """
    if not message.chat: return
    
    chat_filters = await get_chat_filters(message.chat.id)
    if not chat_filters: return
    
    text = message.text.lower()
    
    for trigger, data in chat_filters.items():
        # Word boundary regex to match exact words (e.g., 'hi' matches 'hi' but not 'high')
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, text):
            msg_text = data.get("text")
            media_id = data.get("media")
            
            try:
                if media_id:
                    # Reply with media (and caption if exists)
                    await message.reply_cached_media(media_id, caption=msg_text)
                elif msg_text:
                    # Reply with text only
                    await message.reply_text(msg_text)
            except Exception:
                # Silently fail if media is invalid or bot lacks permissions
                pass
            break