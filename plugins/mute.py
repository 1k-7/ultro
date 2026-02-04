from pyrogram import Client, types
from pyrogram.types import ChatPermissions
from utils import ultroid_cmd, eor, get_user_id

@ultroid_cmd("mute", admins_only=True)
async def mute_user(client, message):
    """Mute a user indefinitely."""
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user.")
        
    try:
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=False)
        )
        await eor(message, f"🔇 **Muted** `{user_id}`")
    except Exception as e:
        await eor(message, f"❌ Error: {e}")

@ultroid_cmd("unmute", admins_only=True)
async def unmute_user(client, message):
    """Unmute a user."""
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user.")
        
    try:
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_invite_users=True
            )
        )
        await eor(message, f"🔊 **Unmuted** `{user_id}`")
    except Exception as e:
        await eor(message, f"❌ Error: {e}")

@ultroid_cmd("tmute", admins_only=True)
async def tmute_user(client, message):
    """Temporarily mute a user. Usage: .tmute 1h"""
    # Logic similar to tban, implement if needed using utils.ban_time
    # This is a basic placeholder matching standard Admin structure
    pass