import os
import asyncio
from PIL import Image
from pyrogram.errors import StickersetInvalid, PeerIdInvalid
from utils import ultroid_cmd, eor

@ultroid_cmd("kang")
async def kang_handler(client, message):
    """
    Usage: Reply to an image/sticker with .kang
    """
    reply = message.reply_to_message
    if not reply:
        return await eor(message, "Reply to a sticker or image.")

    status = await eor(message, "<code>Kanging...</code>")
    
    # 1. Determine Type (Static vs Animated)
    is_animated = False
    if reply.sticker:
        is_animated = reply.sticker.is_animated
        if reply.sticker.is_video:
            return await status.edit("Video stickers not supported yet.")

    # 2. Download Media
    file_path = await reply.download()
    final_file = file_path

    # 3. Convert Image (If Static)
    if not is_animated:
        try:
            img = Image.open(file_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize logic (Ultroid Style: 512px max dimension)
            scale = 512 / max(img.width, img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.LANCZOS)
            
            final_file = file_path + ".png"
            img.save(final_file, "PNG")
        except Exception as e:
            if os.path.exists(file_path): os.remove(file_path)
            return await status.edit(f"❌ Image Error: {e}")

    # 4. Prepare Pack Details
    # CRITICAL FIX: Explicitly get 'me' to avoid identity errors
    me = await client.get_me()
    pack_num = 1
    
    # Handle Username (Fallback to ID if None)
    user_ref = me.username if me.username else str(me.id)
    name_ref = me.first_name if me.first_name else "User"

    if is_animated:
        pack_name = f"kang_anim_{me.id}_{pack_num}"
        pack_title = f"{name_ref}'s Animated V{pack_num}"
    else:
        pack_name = f"kang_{me.id}_{pack_num}"
        pack_title = f"{name_ref}'s Kang V{pack_num}"

    # Get Emoji
    emoji = "🤔"
    if len(message.command) > 1:
        emoji = message.command[1]
    elif reply.sticker and reply.sticker.emoji:
        emoji = reply.sticker.emoji

    # 5. Add Sticker (Retry Logic)
    try:
        # Try adding to existing pack
        # Only requires (short_name, file, emoji)
        await client.add_sticker_to_set(pack_name, final_file, emoji)
    
    except StickersetInvalid:
        # Pack doesn't exist -> Create New
        try:
            # CRITICAL FIX: Use "me" as user_id to bypass resolution errors
            await client.create_sticker_set(
                "me", 
                pack_name, 
                pack_title, 
                final_file, 
                emoji
            )
        except Exception as e:
            return await status.edit(f"❌ <b>Creation Error:</b>\n{e}")
            
    except Exception as e:
        if "STICKER_PACKS_TOO_MUCH" in str(e):
             return await status.edit("❌ Pack is full! (Switching packs not implemented yet)")
        return await status.edit(f"❌ <b>Error:</b>\n{e}")
        
    finally:
        # Cleanup
        if os.path.exists(file_path): os.remove(file_path)
        if final_file != file_path and os.path.exists(final_file): os.remove(final_file)

    # 6. Success Message (Ultroid Style)
    await status.edit(f"<b>Sticker Kanged!</b>\n<a href='t.me/addstickers/{pack_name}'>View Pack</a>")