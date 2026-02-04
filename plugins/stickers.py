import os
from pyrogram import Client, filters
from pyrogram.errors import StickersetInvalid, StickersTooMuch
from utils import ultroid_cmd, eor, resize_photo_sticker

@ultroid_cmd("kang")
async def kang_handler(client, message):
    reply = message.reply_to_message
    if not reply:
        return await eor(message, "Reply to a sticker or image.")
        
    status = await eor(message, "<code>Kanging...</code>")
    
    # 1. Determine Emoji
    emoji = "🤔"
    if len(message.command) > 1:
        emoji = message.command[1]
    elif reply.sticker and reply.sticker.emoji:
        emoji = reply.sticker.emoji
        
    # 2. Download Media
    try:
        file_path = await reply.download()
    except Exception as e:
        return await status.edit(f"Failed to download: {e}")

    # 3. Detect Type (Static / Animated / Video) & Resize if needed
    is_anim = False
    is_vid = False
    
    if reply.sticker:
        is_anim = getattr(reply.sticker, "is_animated", False)
        is_vid = getattr(reply.sticker, "is_video", False)
        
        # If it is a static sticker, we ensure it's resized/converted to PNG just in case
        if not (is_anim or is_vid):
            resized = resize_photo_sticker(file_path)
            if resized: file_path = resized
    elif reply.photo or reply.document:
        # Photos/Docs are treated as Static
        resized = resize_photo_sticker(file_path)
        if resized: file_path = resized
    
    # 4. Define Pack Naming Convention
    # Static:  kang_USERID_1
    # Anim:    kang_anim_USERID_1
    # Video:   kang_vid_USERID_1
    
    user = message.from_user
    pack_num = 1
    
    prefix = "kang"
    title_type = "Kang"
    
    if is_anim:
        prefix = "kang_anim"
        title_type = "Anim Kang"
    elif is_vid:
        prefix = "kang_vid"
        title_type = "Vid Kang"
        
    # 5. Add to Pack (Loop for handling full packs)
    while True:
        short_name = f"{prefix}_{user.id}_{pack_num}"
        pack_title = f"{user.first_name}'s {title_type} V{pack_num}"
        
        try:
            # Try adding to existing pack
            # Using POSITIONAL arguments to avoid 'unexpected keyword' errors
            # Signature typically: user_id, name (short_name), sticker, emoji
            await client.add_sticker_to_set(
                user.id,
                short_name,
                file_path,
                emoji
            )
            await status.edit(f"✅ **Sticker Kanged!**\nPack: [View Here](t.me/addstickers/{short_name})")
            break
            
        except StickersetInvalid:
            # Pack doesn't exist -> Create it
            try:
                # For creation, we used Keyword arguments as they are safer for booleans
                # User provided doc says: create_sticker_set(title, short_name, sticker, user_id, emoji, ...)
                # But Pyrogram standard is: user_id, title, short_name, sticker...
                # We will trust the keyword args based on your previous doc share.
                await client.create_sticker_set(
                    user_id=user.id,
                    title=pack_title,
                    short_name=short_name,
                    sticker=file_path,
                    emoji=emoji,
                    animated=is_anim, # Confirmed correct param name by user
                    videos=is_vid     # Confirmed correct param name by user
                )
                await status.edit(f"✅ **Pack Created!**\nPack: [View Here](t.me/addstickers/{short_name})")
                break
            except Exception as e:
                await status.edit(f"❌ Creation Failed: {e}")
                break
                
        except StickersTooMuch:
            # Pack is full -> Try next number
            pack_num += 1
            continue
            
        except Exception as e:
            # Fallback for "Pack Full" if exception name differs or other error
            if "stickers_too_much" in str(e).lower() or "pack is full" in str(e).lower():
                pack_num += 1
                continue
            
            await status.edit(f"❌ Error: {e}")
            break

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists("sticker.png"):
        os.remove("sticker.png")