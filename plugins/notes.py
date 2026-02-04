import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database import db
from utils import ultroid_cmd, eor

# --- Database Logic ---

async def get_all_notes():
    return await db.get_key("NOTES") or {}

async def add_note_db(chat_id, word, text, media):
    data = await get_all_notes()
    chat_str = str(chat_id)
    if chat_str not in data:
        data[chat_str] = {}
    
    data[chat_str][word] = {
        "text": text,
        "media": media
    }
    await db.set_key("NOTES", data)

async def rem_note_db(chat_id, word):
    data = await get_all_notes()
    chat_str = str(chat_id)
    if chat_str in data and word in data[chat_str]:
        del data[chat_str][word]
        await db.set_key("NOTES", data)
        return True
    return False

async def get_chat_notes(chat_id):
    data = await get_all_notes()
    return data.get(str(chat_id), {})

# --- Commands ---

@ultroid_cmd("addnote", admins_only=True)
async def add_note_handler(client, message):
    """
    Save a note.
    Usage: .addnote <word> (Reply to message)
    """
    if len(message.command) < 2:
        return await eor(message, "❌ Usage: `.addnote <word>` (reply to content)")
    
    word = message.text.split(None, 1)[1].split()[0].lower()
    # Strip # if user provided it manually
    if word.startswith("#"): word = word[1:]
        
    reply = message.reply_to_message
    if not reply:
        return await eor(message, "❌ Reply to a message to save it.")
        
    text = reply.caption or reply.text or ""
    media_id = None
    
    if reply.media:
        for attr in ["photo", "video", "audio", "voice", "document", "sticker", "animation", "video_note"]:
            media = getattr(reply, attr, None)
            if media:
                media_id = media.file_id
                break
    
    await add_note_db(message.chat.id, word, text, media_id)
    await eor(message, f"✅ **Note Saved:** `#{word}`")

@ultroid_cmd("remnote", admins_only=True)
async def rem_note_handler(client, message):
    """
    Remove a note.
    Usage: .remnote <word>
    """
    if len(message.command) < 2:
        return await eor(message, "❌ Usage: `.remnote <word>`")
    
    word = message.text.split(None, 1)[1].lower()
    if word.startswith("#"): word = word[1:]
    
    if await rem_note_db(message.chat.id, word):
        await eor(message, f"🗑 **Note Removed:** `#{word}`")
    else:
        await eor(message, f"⚠️ Note `#{word}` not found.")

@ultroid_cmd("listnote", admins_only=True)
async def list_note_handler(client, message):
    """
    List all notes in chat.
    """
    notes = await get_chat_notes(message.chat.id)
    if not notes:
        return await eor(message, "❌ No notes found in this chat.")
        
    msg = "**📝 Notes in this chat:**\n\n"
    for word in notes.keys():
        msg += f"• `#{word}`\n"
        
    await eor(message, msg)

# --- Watcher ---

@Client.on_message(filters.text & filters.group, group=3)
async def note_watcher(client: Client, message: Message):
    """
    Checks for #hashtags in messages and replies with note.
    """
    if not message.chat or not message.text: return
    
    # Simple check for efficiency
    if "#" not in message.text: return
    
    notes = await get_chat_notes(message.chat.id)
    if not notes: return
    
    # Split text and find words starting with #
    words = set(message.text.lower().split())
    
    for word_raw in words:
        if word_raw.startswith("#"):
            key = word_raw[1:] # Remove #
            if key in notes:
                note_data = notes[key]
                msg_text = note_data.get("text")
                media_id = note_data.get("media")
                
                try:
                    if media_id:
                        await message.reply_cached_media(media_id, caption=msg_text)
                    elif msg_text:
                        await message.reply_text(msg_text)
                except:
                    pass
                # Stop after one note to prevent spam
                break