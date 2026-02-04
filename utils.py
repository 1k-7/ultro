import asyncio
import math
import time
import os
import io
import traceback
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from config import Config

# --- CONSTANTS ---
HANDLER = Config.HANDLER if hasattr(Config, "HANDLER") else [".", "!"]

def clean_sudo_list(sudo_list):
    clean = []
    if not sudo_list: return clean
    for x in sudo_list:
        try:
            clean.append(int(x))
        except ValueError:
            continue
    return clean

SUDO_USERS = clean_sudo_list(Config.SUDO_USERS) if hasattr(Config, "SUDO_USERS") else []

# --- DECORATOR ---
def ultroid_cmd(pattern: str, full_sudo=False, only_devs=False, **kwargs):
    def func(flt, _, message):
        user = message.from_user
        if not user: return False 
        
        if user.is_self: return True
        if only_devs: return False 
        
        # Sudo Check
        if user.id in SUDO_USERS: 
            return True
            
        return False

    auth_filter = filters.create(func)
    return Client.on_message(filters.command(pattern, prefixes=HANDLER) & auth_filter)

# --- MESSAGING ---
async def eor(message: Message, text: str, time: int = None, **kwargs):
    # Default to MARKDOWN to fix broken formatting
    kwargs.setdefault("parse_mode", enums.ParseMode.MARKDOWN)
    kwargs.setdefault("disable_web_page_preview", True)
    
    sent_msg = None
    try:
        if message.from_user and message.from_user.is_self:
            sent_msg = await message.edit_text(text, **kwargs)
        else:
            sent_msg = await message.reply_text(text, **kwargs)
    except Exception:
        # Fallback if Markdown fails (e.g. unclosed tags)
        try:
            kwargs["parse_mode"] = enums.ParseMode.DISABLED
            if message.from_user and message.from_user.is_self:
                sent_msg = await message.edit_text(text, **kwargs)
            else:
                sent_msg = await message.reply_text(text, **kwargs)
        except:
            pass

    if time and sent_msg:
        await asyncio.sleep(time)
        try: await sent_msg.delete()
        except: pass
    return sent_msg

# --- ADMIN HELPERS ---
async def get_user_id(message: Message):
    if message.reply_to_message:
        if message.reply_to_message.sender_chat:
            return message.reply_to_message.sender_chat.id
        if message.reply_to_message.from_user:
            return message.reply_to_message.from_user.id

    if len(message.command) > 1:
        arg = message.command[1]
        if arg.lstrip("-").isdigit(): 
            return int(arg)
        if arg.startswith("@"):
            try:
                u = await message._client.get_users(arg)
                return u.id
            except: pass
    return None

def ban_time(time_str: str) -> int:
    if not time_str: return 0
    unit = time_str[-1].lower()
    if not unit.isalpha(): return int(time_str)
    val = int(time_str[:-1])
    if unit == 's': return val
    if unit == 'm': return val * 60
    if unit == 'h': return val * 3600
    if unit == 'd': return val * 86400
    if unit == 'w': return val * 604800
    return 0

# --- STICKER HELPER ---
async def get_response(client, chat_id, timeout=5):
    async for message in client.get_chat_history(chat_id, limit=1):
        last_id = message.id
        break
    else:
        last_id = 0

    start = time.time()
    while time.time() - start < timeout:
        await asyncio.sleep(0.5)
        async for message in client.get_chat_history(chat_id, limit=1):
            if message.id > last_id:
                return message
    return None

# --- MEDIA HELPERS ---
def resize_photo_sticker(photo_path: str, output_path: str = "sticker.png"):
    try:
        from PIL import Image
        img = Image.open(photo_path)
        if (img.width and img.height) < 512:
            size1 = img.width
            size2 = img.height
            if img.width > img.height:
                scale = 512 / size1
                size1new = 512
                size2new = size2 * scale
            else:
                scale = 512 / size2
                size1new = size1 * scale
                size2new = 512
            size1new = math.floor(size1new)
            size2new = math.floor(size2new)
            sizenew = (size1new, size2new)
            img = img.resize(sizenew)
        else:
            maxsize = (512, 512)
            img.thumbnail(maxsize)
        img.save(output_path, "PNG")
        return output_path
    except:
        return None

# --- SYSTEM & SHELL ---
async def run_cmd(cmd: str):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode('utf-8', 'replace').strip(),
        stderr.decode('utf-8', 'replace').strip(),
        process.returncode,
        process.pid
    )