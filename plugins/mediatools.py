import os
import asyncio
from PIL import Image, ImageOps
from utils import ultroid_cmd, eor, resize_photo_sticker

@ultroid_cmd("rotate")
async def rotate_handler(client, message):
    """ .rotate <90/180/270>: Rotates image. """
    reply = message.reply_to_message
    if not reply: return await eor(message, "Reply to an image.")
    
    angle = 90
    if len(message.command) > 1 and message.command[1].isdigit():
        angle = int(message.command[1])
        
    path = await reply.download()
    status = await eor(message, "Rotating...")
    try:
        im = Image.open(path)
        im = im.rotate(angle, expand=True)
        im.save("rotate.png")
        await client.send_document(message.chat.id, "rotate.png", reply_to_message_id=reply.id)
    except Exception as e:
        await status.edit(f"Error: {e}")
    finally:
        if os.path.exists(path): os.remove(path)
        if os.path.exists("rotate.png"): os.remove("rotate.png")
    await status.delete()

@ultroid_cmd("invert")
async def invert_handler(client, message):
    """ .invert: Inverts image colors. """
    reply = message.reply_to_message
    if not reply: return await eor(message, "Reply to image.")
    path = await reply.download()
    status = await eor(message, "Inverting...")
    try:
        im = Image.open(path).convert("RGB")
        im = ImageOps.invert(im)
        im.save("invert.png")
        await client.send_document(message.chat.id, "invert.png", reply_to_message_id=reply.id)
    except Exception as e:
        await status.edit(f"Error: {e}")
    finally:
        if os.path.exists(path): os.remove(path)
        if os.path.exists("invert.png"): os.remove("invert.png")
    await status.delete()