import os
import requests
from utils import ultroid_cmd, eor

@ultroid_cmd("tm")
async def telegraph_media_handler(client, message):
    """
    Usage: Reply to media with .tm
    Uploads it to Telegra.ph and returns a link.
    """
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await eor(message, "Reply to a photo or video.")

    status = await eor(message, "Downloading...")
    file_path = await reply.download()

    await status.edit("Uploading to Telegraph...")
    
    try:
        # Use the unofficial upload endpoint
        files = {'file': open(file_path, 'rb')}
        r = requests.post("https://telegra.ph/upload", files=files)
        response = r.json()
        
        if isinstance(response, list) and "src" in response[0]:
            link = "https://telegra.ph" + response[0]["src"]
            await status.edit(f"**Telegraph Link:**\n`{link}`")
        else:
            await status.edit(f"Error: {response}")
            
    except Exception as e:
        await status.edit(f"Failed: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@ultroid_cmd("txt")
async def telegraph_text_handler(client, message):
    """
    Usage: .txt <title> | <content> (or reply to text)
    Pastes text to a Telegraph page.
    """
    # Simple logic using 'tm' shorthand for now, strictly requires requests
    # For full page creation with formatting, we usually need 'html_telegraph_poster'
    # This is a basic raw text version
    
    text = ""
    title = "Pyroblack Paste"
    
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        text = message.text.split(maxsplit=1)[1]
        
    if not text:
        return await eor(message, "Give me text to paste.")

    # Create page via API
    try:
        # We create a simple account on the fly or use a hardcoded one
        # This is a simplified requests version
        api_url = "https://api.telegra.ph/createPage"
        params = {
            "access_token": "d3b25feccb89e508a9114afb82aa421fe2a9712b963b387cc5ad71e58722", # Public Sandbox Token
            "title": title,
            "content": f'[{{"tag":"p","children":["{text}"]}}]',
            "return_content": False
        }
        r = requests.post(api_url, json=params)
        res = r.json()
        
        if res.get("ok"):
            url = res["result"]["url"]
            await eor(message, f"**Pasted:** [Link]({url})", disable_web_page_preview=True)
        else:
            await eor(message, f"Error: {res}")
            
    except Exception as e:
        await eor(message, f"Error: {e}")