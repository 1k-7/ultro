import os
import aiohttp
from pyrogram import Client, filters
from utils import ultroid_cmd, eor

# --- Uploaders ---

async def upload_catbox(file_path):
    """Uploads file to catbox.moe"""
    url = "https://catbox.moe/user/api.php"
    data = aiohttp.FormData()
    data.add_field('reqtype', 'fileupload')
    data.add_field('userhash', '')
    data.add_field('fileToUpload', open(file_path, 'rb'))
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as resp:
            return await resp.text()

async def upload_0x0(file_path):
    """Uploads file to 0x0.st"""
    url = "https://0x0.st"
    data = aiohttp.FormData()
    data.add_field('file', open(file_path, 'rb'))
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as resp:
            return await resp.text()

# --- Command ---

@ultroid_cmd("webupload")
async def webupload_handler(client, message):
    """
    Upload files to the web.
    Usage: .webupload (Reply to file) [catbox|0x0]
    """
    if not message.reply_to_message:
        return await eor(message, "❌ **Reply to a file/media.**")
    
    # 1. Determine Provider
    text = message.text.lower()
    provider = "catbox" # Default
    if "0x0" in text:
        provider = "0x0"
        
    status = await eor(message, f"<code>Downloading to host on {provider}...</code>")
    
    # 2. Download
    try:
        file_path = await message.reply_to_message.download()
    except Exception as e:
        return await status.edit(f"❌ **Download Failed:** `{e}`")
    
    if not file_path:
        return await status.edit("❌ **Error:** File not found.")

    # 3. Upload
    await status.edit(f"<code>Uploading to {provider}...</code>")
    
    try:
        link = None
        if provider == "catbox":
            link = await upload_catbox(file_path)
        elif provider == "0x0":
            link = await upload_0x0(file_path)
            
        # 4. Result
        if link and link.startswith("http"):
            await status.edit(
                f"✅ **Upload Success!**\n\n"
                f"🔗 **Link:** `{link}`\n"
                f"☁️ **Host:** `{provider}`"
            )
        else:
            await status.edit(f"❌ **Upload Failed.**\nResponse: `{link}`")
            
    except Exception as e:
        await status.edit(f"❌ **Error:** `{e}`")
        
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)