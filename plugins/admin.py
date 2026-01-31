import asyncio
import time
from pyrogram import filters, enums
from pyrogram.types import ChatPermissions, ChatPrivileges
from utils import ultroid_cmd, eor, get_user_id

# --- HELPER: Parse Time String (1m, 2h, 1d) ---
def parse_time(s):
    if not s: return 0
    multipliers = {'m': 60, 'h': 3600, 'd': 86400, 'w': 604800}
    try:
        return int(s[:-1]) * multipliers.get(s[-1], 1)
    except:
        return 0

# --- BAN / UNBAN / KICK / MUTE ---

@ultroid_cmd("ban", full_sudo=True)
async def ban_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id: return await eor(message, "Reply to a user.")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await eor(message, f"🚫 **Banned** `{user_id}`")
    except Exception as e: await eor(message, f"Error: {e}")

@ultroid_cmd("unban", full_sudo=True)
async def unban_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id: return await eor(message, "Reply to a user.")
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        await eor(message, f"✅ **Unbanned** `{user_id}`")
    except Exception as e: await eor(message, f"Error: {e}")

@ultroid_cmd("kick", full_sudo=True)
async def kick_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id: return await eor(message, "Reply to a user.")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
        await eor(message, f"🦶 **Kicked** `{user_id}`")
    except Exception as e: await eor(message, f"Error: {e}")

@ultroid_cmd("tban", full_sudo=True)
async def tban_handler(client, message):
    if len(message.command) < 2: return await eor(message, "Usage: .tban 1h (reply)")
    time_str = message.command[1]
    seconds = parse_time(time_str)
    user_id = await get_user_id(message)
    if not user_id: return await eor(message, "Reply to a user.")
    
    try:
        until = time.time() + seconds
        await client.ban_chat_member(message.chat.id, user_id, until_date=until)
        await eor(message, f"🚫 **Temp Banned** `{user_id}` for `{time_str}`")
    except Exception as e: await eor(message, f"Error: {e}")

# --- PROMOTE / DEMOTE ---

@ultroid_cmd("promote", full_sudo=True)
async def promote_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id: return await eor(message, "Reply to a user.")
    title = "Admin"
    if len(message.command) > 1 and not message.reply_to_message: title = " ".join(message.command[2:])
    elif len(message.command) > 1: title = " ".join(message.command[1:])
    try:
        await client.promote_chat_member(
            message.chat.id, user_id,
            privileges=ChatPrivileges(
                can_change_info=True, can_invite_users=True, can_delete_messages=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=True,
                can_manage_chat=True, can_manage_video_chats=True
            )
        )
        await client.set_administrator_title(message.chat.id, user_id, title)
        await eor(message, f"✅ **Promoted** `{user_id}` as `{title}`")
    except Exception as e: await eor(message, f"Error: {e}")

@ultroid_cmd("demote", full_sudo=True)
async def demote_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id: return await eor(message, "Reply to a user.")
    try:
        await client.promote_chat_member(
            message.chat.id, user_id,
            privileges=ChatPrivileges(can_manage_chat=False) # Revoke all
        )
        await eor(message, f"⬇️ **Demoted** `{user_id}`")
    except Exception as e: await eor(message, f"Error: {e}")

# --- PIN / UNPIN / LIST PINNED ---

@ultroid_cmd("pin", full_sudo=True)
async def pin_handler(client, message):
    if not message.reply_to_message: return await eor(message, "Reply to a message.")
    notify = "loud" in message.text.lower() or "notify" in message.text.lower()
    try:
        await message.reply_to_message.pin(disable_notification=not notify)
        await eor(message, f"📌 **Pinned!** (Notify: {notify})")
    except Exception as e: await eor(message, f"Error: {e}")

@ultroid_cmd("unpin", full_sudo=True)
async def unpin_handler(client, message):
    if "all" in message.text.lower():
        await client.unpin_all_chat_messages(message.chat.id)
        return await eor(message, "🗑 **Unpinned All.**")
    if not message.reply_to_message: return await eor(message, "Reply to a message.")
    await message.reply_to_message.unpin()
    await eor(message, "Unpinned.")

@ultroid_cmd("pinned", full_sudo=True)
async def get_pinned(client, message):
    chat = await client.get_chat(message.chat.id)
    if chat.pinned_message:
        await eor(message, f"📌 **Pinned Message:** [Click Here]({chat.pinned_message.link})")
    else:
        await eor(message, "No pinned message found.")

# --- PURGE TOOLS ---

@ultroid_cmd("purge", full_sudo=True)
async def purge_handler(client, message):
    if not message.reply_to_message: return await eor(message, "Reply to start purging.")
    await message.delete()
    try:
        msg_ids = list(range(message.reply_to_message.id, message.id))
        await client.delete_messages(message.chat.id, msg_ids)
        tmp = await client.send_message(message.chat.id, f"🗑 **Purged {len(msg_ids)} messages.**")
        await asyncio.sleep(3)
        await tmp.delete()
    except Exception as e: await client.send_message(message.chat.id, f"Error: {e}")

@ultroid_cmd("purgeme", full_sudo=True)
async def purgeme_handler(client, message):
    count = int(message.command[1]) if len(message.command) > 1 and message.command[1].isdigit() else 10
    await message.delete()
    my_msgs = []
    async for msg in client.get_chat_history(message.chat.id, limit=count):
        if msg.from_user and msg.from_user.is_self:
            my_msgs.append(msg.id)
    if my_msgs:
        await client.delete_messages(message.chat.id, my_msgs)
        tmp = await client.send_message(message.chat.id, f"✅ Purged {len(my_msgs)} of my messages.")
        await asyncio.sleep(3)
        await tmp.delete()