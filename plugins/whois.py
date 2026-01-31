from pyrogram import enums
from utils import ultroid_cmd, eor

@ultroid_cmd("whois")
async def whois_handler(client, message):
    """
    Usage: .whois <reply/username>
    Fetches user info.
    """
    status = await eor(message, "Fetching info...")
    
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = message.command[1]
        
    if not user_id:
        user_id = message.from_user.id

    try:
        user = await client.get_users(user_id)
        if not user:
            return await status.edit("User not found.")
            
        # Determine Profile Photo
        photo_id = None
        if user.photo:
            photo_id = user.photo.big_file_id

        # Format info
        info = f"**WHOIS REPORT**\n\n"
        info += f"🆔 **ID:** `{user.id}`\n"
        info += f"👤 **First Name:** {user.first_name}\n"
        if user.last_name:
            info += f"🗣 **Last Name:** {user.last_name}\n"
        if user.username:
            info += f"🔗 **Username:** @{user.username}\n"
        
        info += f"🏢 **DC:** {user.dc_id or 'Unknown'}\n"
        info += f"🤖 **Is Bot:** {user.is_bot}\n"
        info += f"🚫 **Scam:** {user.is_scam}\n"
        info += f"👑 **Premium:** {user.is_premium}\n"
        
        # Get Chat Member status if in a group
        if message.chat.type in [enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
            try:
                member = await client.get_chat_member(message.chat.id, user.id)
                info += f"🛡 **Group Status:** {member.status.name}\n"
            except:
                pass
                
        # Send Photo if available, else text
        if photo_id:
            await message.reply_photo(photo_id, caption=info)
            await status.delete()
        else:
            await status.edit(info)

    except Exception as e:
        await status.edit(f"Error: {e}")

@ultroid_cmd("id")
async def id_handler(client, message):
    """
    Usage: .id (reply)
    Quickly gets the ID of the chat and the replied user/media.
    """
    txt = f"**Chat ID:** `{message.chat.id}`\n"
    
    if message.reply_to_message:
        reply = message.reply_to_message
        txt += f"**User ID:** `{reply.from_user.id}`\n"
        if reply.forward_from:
             txt += f"**Fwd From:** `{reply.forward_from.id}`\n"
        if reply.sticker:
             txt += f"**Sticker ID:** `{reply.sticker.file_id}`\n"
             
    await eor(message, txt)