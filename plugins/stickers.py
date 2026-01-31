import os
import asyncio
from PIL import Image
from utils import ultroid_cmd, eor, resize_photo_sticker, get_response

STICKER_BOT = "Stickers"

@ultroid_cmd("kang")
async def kang_handler(client, message):
    reply = message.reply_to_message
    if not reply: return await eor(message, "Reply to a sticker or image.")
    status = await eor(message, "<code>Kanging...</code>")
    
    # 1. Process File
    file_path = await reply.download()
    if not reply.sticker or not reply.sticker.is_animated:
        if resize_photo_sticker(file_path, "sticker.png"):
            file_path = "sticker.png"
    
    # 2. Pack Info
    me = await client.get_me()
    pack_num = 1
    user_name = me.username if me.username else me.first_name
    pack_name = f"kang_{me.id}_{pack_num}"
    pack_title = f"{me.first_name}'s Kang V{pack_num}"
    emoji = message.command[1] if len(message.command) > 1 else "🤔"
    if reply.sticker and reply.sticker.emoji: emoji = reply.sticker.emoji

    # 3. Automate @Stickers
    try:
        await client.send_message(STICKER_BOT, "/cancel")
        await asyncio.sleep(0.5)
        await client.send_message(STICKER_BOT, "/addsticker")
        
        # Select Pack
        await asyncio.sleep(0.5)
        await client.send_message(STICKER_BOT, pack_name)
        response = await get_response(client, STICKER_BOT)
        
        # If Pack Invalid -> Create New
        if response and "Invalid set" in response.text:
            await client.send_message(STICKER_BOT, "/newpack")
            await asyncio.sleep(0.5)
            await client.send_message(STICKER_BOT, pack_title)
            await asyncio.sleep(0.5)
            await client.send_document(STICKER_BOT, file_path, force_document=True)
            await asyncio.sleep(1)
            await client.send_message(STICKER_BOT, emoji)
            await asyncio.sleep(0.5)
            await client.send_message(STICKER_BOT, "/publish")
            await asyncio.sleep(0.5)
            await client.send_message(STICKER_BOT, "/skip")
            await asyncio.sleep(0.5)
            await client.send_message(STICKER_BOT, pack_name)
        else:
            await client.send_document(STICKER_BOT, file_path, force_document=True)
            await asyncio.sleep(1)
            await client.send_message(STICKER_BOT, emoji)
            await asyncio.sleep(0.5)
            await client.send_message(STICKER_BOT, "/done")
            
        await status.edit(f"<b>Sticker Kanged!</b>\n<a href='t.me/addstickers/{pack_name}'>View Pack</a>")
        
    except Exception as e:
        await status.edit(f"Error: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)
        if os.path.exists("sticker.png"): os.remove("sticker.png")