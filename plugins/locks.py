import asyncio
from pyrogram import Client, enums
from pyrogram.types import ChatPermissions, Message
from utils import ultroid_cmd, eor

# Permissions Mapping
# Key: (Pyrogram Attribute, Human Readable Name)
LOCK_TYPES = {
    "msgs": ("can_send_messages", "Messages"),
    "msg": ("can_send_messages", "Messages"),
    "media": ("can_send_media_messages", "Media"),
    "stickers": ("can_send_other_messages", "Stickers/GIFs"),
    "sticker": ("can_send_other_messages", "Stickers/GIFs"),
    "gifs": ("can_send_other_messages", "Stickers/GIFs"),
    "gif": ("can_send_other_messages", "Stickers/GIFs"),
    "games": ("can_send_other_messages", "Stickers/GIFs"),
    "inline": ("can_send_other_messages", "Stickers/GIFs"),
    "polls": ("can_send_polls", "Polls"),
    "poll": ("can_send_polls", "Polls"),
    "invites": ("can_invite_users", "Invites"),
    "invite": ("can_invite_users", "Invites"),
    "pin": ("can_pin_messages", "Pinning"),
    "info": ("can_change_info", "Info Change"),
    "changeinfo": ("can_change_info", "Info Change"),
    "webprev": ("can_add_web_page_previews", "Web Previews")
}

async def current_permissions(client, chat_id):
    """Fetches current chat permissions."""
    chat = await client.get_chat(chat_id)
    return chat.permissions or ChatPermissions()

@ultroid_cmd("lock")
async def lock_handler(client, message):
    """
    Lock a chat setting.
    Usage: .lock <msgs/media/stickers/polls/invites/pin/info>
    """
    if len(message.command) < 2:
        return await eor(message, "❌ Usage: `.lock <type>`")
        
    target = message.command[1].lower()
    if target not in LOCK_TYPES:
        return await eor(message, f"❌ Invalid type. Types: `{', '.join(LOCK_TYPES.keys())}`")
        
    perm_attr, human_name = LOCK_TYPES[target]
    
    # Get current perms to avoid resetting others
    current = await current_permissions(client, message.chat.id)
    
    # To LOCK, we set the permission to FALSE (User CANNOT do X)
    new_perms_dict = {}
    
    # Copy existing values (defaulting to True for public groups if None)
    for attr in [
        "can_send_messages", "can_send_media_messages", "can_send_other_messages",
        "can_send_polls", "can_add_web_page_previews", "can_change_info",
        "can_invite_users", "can_pin_messages"
    ]:
        val = getattr(current, attr)
        # If val is None, it usually means allowed in basic groups, but let's be safe
        new_perms_dict[attr] = val if val is not None else True

    # Apply the lock
    new_perms_dict[perm_attr] = False
    
    try:
        await client.set_chat_permissions(
            message.chat.id,
            ChatPermissions(**new_perms_dict)
        )
        await eor(message, f"🔒 **Locked:** `{human_name}`")
    except Exception as e:
        await eor(message, f"❌ **Error:** `{e}`")

@ultroid_cmd("unlock")
async def unlock_handler(client, message):
    """
    Unlock a chat setting.
    Usage: .unlock <msgs/media/stickers/polls/invites/pin/info>
    """
    if len(message.command) < 2:
        return await eor(message, "❌ Usage: `.unlock <type>`")
        
    target = message.command[1].lower()
    if target not in LOCK_TYPES:
        return await eor(message, f"❌ Invalid type. Types: `{', '.join(LOCK_TYPES.keys())}`")
        
    perm_attr, human_name = LOCK_TYPES[target]
    
    current = await current_permissions(client, message.chat.id)
    
    # To UNLOCK, we set the permission to TRUE (User CAN do X)
    new_perms_dict = {}
    
    for attr in [
        "can_send_messages", "can_send_media_messages", "can_send_other_messages",
        "can_send_polls", "can_add_web_page_previews", "can_change_info",
        "can_invite_users", "can_pin_messages"
    ]:
        val = getattr(current, attr)
        new_perms_dict[attr] = val if val is not None else True

    # Apply the unlock
    new_perms_dict[perm_attr] = True
    
    try:
        await client.set_chat_permissions(
            message.chat.id,
            ChatPermissions(**new_perms_dict)
        )
        await eor(message, f"🔓 **Unlocked:** `{human_name}`")
    except Exception as e:
        await eor(message, f"❌ **Error:** `{e}`")