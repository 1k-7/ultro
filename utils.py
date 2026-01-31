import asyncio
import math
import time
import os
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from config import Config

# --- DECORATORS ---

def ultroid_cmd(pattern: str, full_sudo=False, only_devs=False, **kwargs):
    """
    The Master Decorator.
    Handles commands, prefixes, and permissions (Sudo/Owner).
    """
    def func(flt, _, message):
        user = message.from_user
        if not user: return False
        
        # 1. Owner always has access
        if user.is_self: return True
        
        # 2. If 'only_devs' is True, ONLY owner access (Sudo cannot use)
        if only_devs: return False 
        
        # 3. Sudo Access (if full_sudo=True)
        if full_sudo and user.id in Config.SUDO_USERS:
            return True
            
        return False

    auth_filter = filters.create(func)
    prefixes = Config.HANDLER if hasattr(Config, "HANDLER") else [".", "!"]
    
    return Client.on_message(filters.command(pattern, prefixes=prefixes) & auth_filter)


# --- MESSAGING HELPERS ---

async def eor(message: Message, text: str, time: int = None, **kwargs):
    """
    Edit Or Reply.
    Tries to edit the message if sent by you, otherwise replies.
    """
    # Default to HTML to support Ultroid's bold/code styles
    kwargs.setdefault("parse_mode", enums.ParseMode.HTML)
    kwargs.setdefault("disable_web_page_preview", True)
    
    try:
        if message.from_user and message.from_user.is_self:
            sent_msg = await message.edit_text(text, **kwargs)
        else:
            sent_msg = await message.reply_text(text, **kwargs)

        if time:
            await asyncio.sleep(time)
            await sent_msg.delete()
            
        return sent_msg
    except Exception as e:
        print(f"EOR Error: {e}")
        # Fallback: if edit fails (e.g. message too old), try reply
        try:
             return await message.reply_text(text, **kwargs)
        except:
             return None


# --- SYSTEM HELPERS ---

async def run_cmd(cmd: str):
    """
    Runs shell commands asynchronously.
    Required for: Updater, Bash, Devtools.
    """
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


# --- ADMIN & USER HELPERS ---

async def get_user_id(message: Message):
    """
    Extracts the user ID from a reply or command argument.
    Required for: Admin Tools (Ban, Kick, Promote).
    """
    # 1. Check Reply
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
        
    # 2. Check Arguments (e.g., .ban @username or .ban 12345)
    if len(message.command) > 1:
        arg = message.command[1]
        
        # If it's a numeric ID
        if arg.lstrip("-").isdigit():
            return int(arg)
            
        # If it's a username (requires client resolution)
        if arg.startswith("@"):
            try:
                user = await message._client.get_users(arg)
                return user.id
            except:
                pass
                
    return None


# --- FORMATTING & PROGRESS HELPERS ---

def humanbytes(size):
    """Converts bytes to readable format (KB, MB, GB)."""
    if not size: return "0 B"
    for unit in ["", "K", "M", "G", "T"]:
        if size < 1024: break
        size /= 1024
    return f"{size:.2f} {unit}B"

def time_formatter(milliseconds):
    """Converts milliseconds to readable time (1h 2m 3s)."""
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ""
    if days: tmp += f"{days}d "
    if hours: tmp += f"{hours}h "
    if minutes: tmp += f"{minutes}m "
    tmp += f"{seconds}s"
    return tmp.strip() or "0s"

async def progress(current, total, message, start, type_of_ps):
    """
    Progress bar for downloads/uploads.
    Matches Ultroid style.
    """
    now = time.time()
    diff = now - start
    
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        
        # Progress Bar Logic
        filled_length = int(percentage / 10) # 10 blocks total
        progress_str = "●" * filled_length + "○" * (10 - filled_length)
        
        tmp = (
            f"[{progress_str}] {round(percentage, 2)}%\n"
            f"<b>{type_of_ps}</b>\n"
            f"📦 <b>Size:</b> {humanbytes(current)} / {humanbytes(total)}\n"
            f"🚀 <b>Speed:</b> {humanbytes(speed)}/s\n"
            f"⏱ <b>ETA:</b> {time_formatter(time_to_completion)}"
        )
        try:
            await message.edit(tmp)
        except:
            pass