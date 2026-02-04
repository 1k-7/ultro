import asyncio
import time
from pyrogram import filters, enums
from pyrogram.types import ChatPermissions, ChatPrivileges
from pyrogram.errors import ChannelInvalid, ChatAdminRequired, UserAdminInvalid
from utils import ultroid_cmd, eor, get_user_id, ban_time

@ultroid_cmd("ban", full_sudo=True)
async def ban_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user or provide a username/ID.")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await eor(message, f"🚫 **Banned** `{user_id}`")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("unban", full_sudo=True)
async def unban_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user or provide a username/ID.")
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        await eor(message, f"✅ **Unbanned** `{user_id}`")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("kick", full_sudo=True)
async def kick_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user or provide a username/ID.")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await asyncio.sleep(0.5) # Prevent race conditions
        await client.unban_chat_member(message.chat.id, user_id)
        await eor(message, f"🦶 **Kicked** `{user_id}`")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("mute", full_sudo=True)
async def mute_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user.")
    try:
        await client.restrict_chat_member(
            message.chat.id, user_id,
            ChatPermissions(can_send_messages=False)
        )
        await eor(message, f"🔇 **Muted** `{user_id}`")
    except ChannelInvalid:
        await eor(message, "❌ **Error:** Basic Groups do not support Mute. Convert to Supergroup.")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("unmute", full_sudo=True)
async def unmute_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user.")
    try:
        # Unmute permissions (adjust as needed)
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_invite_users=True
        )
        await client.restrict_chat_member(message.chat.id, user_id, permissions)
        await eor(message, f"🔊 **Unmuted** `{user_id}`")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("tban", full_sudo=True)
async def tban_handler(client, message):
    if len(message.command) < 2:
        return await eor(message, "Usage: .tban 1h (reply)")
    
    seconds = ban_time(message.command[1])
    user_id = await get_user_id(message)
    
    if not user_id:
        return await eor(message, "Reply to a user.")
    if seconds == 0:
        return await eor(message, "Invalid time format. Use 1m, 1h, 1d.")
        
    try:
        until = time.time() + seconds
        await client.ban_chat_member(message.chat.id, user_id, until_date=until)
        await eor(message, f"🚫 **Temp Banned** `{user_id}` for `{message.command[1]}`")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("promote", full_sudo=True)
async def promote_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user.")
    
    # Title logic
    title = "Admin"
    if len(message.command) > 1 and not message.reply_to_message:
        title = " ".join(message.command[2:])
    elif len(message.command) > 1:
        title = " ".join(message.command[1:])
        
    try:
        await client.promote_chat_member(
            message.chat.id, user_id,
            privileges=ChatPrivileges(
                can_change_info=True, can_invite_users=True, can_delete_messages=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=True,
                can_manage_chat=True, can_manage_video_chats=True
            )
        )
        # Setting title might fail if bot is not owner/doesn't have permission
        try: await client.set_administrator_title(message.chat.id, user_id, title)
        except: pass
        
        await eor(message, f"✅ **Promoted** `{user_id}` as `{title}`")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("demote", full_sudo=True)
async def demote_handler(client, message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user.")
    try:
        await client.promote_chat_member(
            message.chat.id, user_id,
            privileges=ChatPrivileges(can_manage_chat=False)
        )
        await eor(message, f"⬇️ **Demoted** `{user_id}`")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("pin", full_sudo=True)
async def pin_handler(client, message):
    if not message.reply_to_message:
        return await eor(message, "Reply to a message to pin it.")
    
    # Check for "loud" or "notify" in the command text
    notify = "loud" in message.text.lower() or "notify" in message.text.lower()
    
    try:
        await message.reply_to_message.pin(disable_notification=not notify)
        await eor(message, f"📌 **Pinned!** (Notify: {notify})")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("unpin", full_sudo=True)
async def unpin_handler(client, message):
    try:
        if "all" in message.text.lower():
            await client.unpin_all_chat_messages(message.chat.id)
            return await eor(message, "🗑 **Unpinned All.**")
        
        if not message.reply_to_message:
            return await eor(message, "Reply to a message to unpin it.")
            
        await message.reply_to_message.unpin()
        await eor(message, "Unpinned.")
    except Exception as e:
        await eor(message, f"**Error:** `{e}`")

@ultroid_cmd("purge", full_sudo=True)
async def purge_handler(client, message):
    if not message.reply_to_message:
        return await eor(message, "Reply to the start message.")
    
    await message.delete() # Delete the command message
    try:
        # Pyrogram's delete_messages can accept a list of IDs
        msg_ids = list(range(message.reply_to_message.id, message.id))
        if not msg_ids: return

        # Delete in chunks if too large (optional optimization)
        await client.delete_messages(message.chat.id, msg_ids)
        
        status = await client.send_message(message.chat.id, f"🗑 **Purged {len(msg_ids)} messages.**")
        await asyncio.sleep(3)
        await status.delete()
    except Exception as e:
        await client.send_message(message.chat.id, f"**Error:** `{e}`")

@ultroid_cmd("zombies", full_sudo=True)
async def zombies_handler(client, message):
    if message.chat.type == enums.ChatType.PRIVATE: 
        return await eor(message, "Groups only.")
    
    status = await eor(message, "<code>Searching for zombies...</code>")
    deleted = []
    
    try:
        async for member in client.get_chat_members(message.chat.id):
            if member.user.is_deleted:
                deleted.append(member.user.id)
    except Exception as e:
        return await status.edit(f"Error fetching members: {e}")
    
    if not deleted: 
        return await status.edit("✅ No zombies found.")
    
    await status.edit(f"Found {len(deleted)} zombies. Cleaning...")
    
    count = 0
    for user_id in deleted:
        try:
            await client.ban_chat_member(message.chat.id, user_id)
            count += 1
            await asyncio.sleep(0.1) # Avoid floodwait
        except: pass
    
    await status.edit(f"✅ **Cleaned {count} Zombies!**")