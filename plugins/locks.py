from pyrogram.types import ChatPermissions
from utils import ultroid_cmd, eor

@ultroid_cmd("lock", full_sudo=True)
async def lock_handler(client, message):
    """
    Usage: .lock <all/msg/media/stickers/polls/info/invite/pin>
    """
    if len(message.command) < 2:
        return await eor(message, "Usage: `.lock <type>`")
    
    lock_type = message.command[1].lower()
    chat_id = message.chat.id
    
    # Get current permissions to avoid resetting others
    current = (await client.get_chat(chat_id)).permissions
    if not current:
        current = ChatPermissions()

    # Define new permission state (False = Locked)
    perms = {}
    
    if lock_type == "all":
        perms = {
            "can_send_messages": False,
            "can_send_media_messages": False,
            "can_send_other_messages": False,
            "can_send_polls": False,
            "can_add_web_page_previews": False,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False
        }
    elif lock_type == "msg":
        perms["can_send_messages"] = False
    elif lock_type == "media":
        perms["can_send_media_messages"] = False
    elif lock_type == "stickers":
        perms["can_send_other_messages"] = False
    elif lock_type == "polls":
        perms["can_send_polls"] = False
    elif lock_type == "info":
        perms["can_change_info"] = False
    elif lock_type == "invite":
        perms["can_invite_users"] = False
    elif lock_type == "pin":
        perms["can_pin_messages"] = False
    else:
        return await eor(message, "Invalid lock type.")

    # Apply Update
    new_perms = ChatPermissions(
        can_send_messages=perms.get("can_send_messages", current.can_send_messages),
        can_send_media_messages=perms.get("can_send_media_messages", current.can_send_media_messages),
        can_send_other_messages=perms.get("can_send_other_messages", current.can_send_other_messages),
        can_send_polls=perms.get("can_send_polls", current.can_send_polls),
        can_change_info=perms.get("can_change_info", current.can_change_info),
        can_invite_users=perms.get("can_invite_users", current.can_invite_users),
        can_pin_messages=perms.get("can_pin_messages", current.can_pin_messages)
    )
    
    try:
        await client.set_chat_permissions(chat_id, new_perms)
        await eor(message, f"🔒 **Locked:** `{lock_type}`")
    except Exception as e:
        await eor(message, f"Error: {e}")

@ultroid_cmd("unlock", full_sudo=True)
async def unlock_handler(client, message):
    """
    Usage: .unlock <type>
    """
    if len(message.command) < 2:
        return await eor(message, "Usage: `.unlock <type>`")
        
    lock_type = message.command[1].lower()
    chat_id = message.chat.id
    current = (await client.get_chat(chat_id)).permissions or ChatPermissions()
    
    perms = {}
    if lock_type == "all":
        perms = {"can_send_messages": True, "can_send_media_messages": True, "can_send_other_messages": True, "can_send_polls": True, "can_invite_users": True}
    elif lock_type == "msg": perms["can_send_messages"] = True
    elif lock_type == "media": perms["can_send_media_messages"] = True
    elif lock_type == "stickers": perms["can_send_other_messages"] = True
    elif lock_type == "polls": perms["can_send_polls"] = True
    elif lock_type == "info": perms["can_change_info"] = True
    elif lock_type == "invite": perms["can_invite_users"] = True
    elif lock_type == "pin": perms["can_pin_messages"] = True
    
    new_perms = ChatPermissions(
        can_send_messages=perms.get("can_send_messages", current.can_send_messages),
        can_send_media_messages=perms.get("can_send_media_messages", current.can_send_media_messages),
        can_send_other_messages=perms.get("can_send_other_messages", current.can_send_other_messages),
        can_send_polls=perms.get("can_send_polls", current.can_send_polls),
        can_change_info=perms.get("can_change_info", current.can_change_info),
        can_invite_users=perms.get("can_invite_users", current.can_invite_users),
        can_pin_messages=perms.get("can_pin_messages", current.can_pin_messages)
    )
    
    try:
        await client.set_chat_permissions(chat_id, new_perms)
        await eor(message, f"🔓 **Unlocked:** `{lock_type}`")
    except Exception as e:
        await eor(message, f"Error: {e}")