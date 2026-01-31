import asyncio
import requests
from pyrogram import Client, filters # Fixed Import
from utils import ultroid_cmd, eor

# Cache for Echo
ECHO_CHATS = set()

@ultroid_cmd("echo", full_sudo=True)
async def echo_handler(c, m):
    if m.chat.id in ECHO_CHATS:
        ECHO_CHATS.remove(m.chat.id)
        await eor(m, "Echo Disabled.")
    else:
        ECHO_CHATS.add(m.chat.id)
        await eor(m, "Echo Enabled.")

@ultroid_cmd("spam", full_sudo=True)
async def spam_handler(c, m):
    if len(m.command)<3: return await eor(m, "Usage: .spam 5 Hello")
    try:
        count = int(m.command[1])
        text = " ".join(m.command[2:])
        await m.delete()
        for _ in range(count):
            await c.send_message(m.chat.id, text)
            await asyncio.sleep(0.1)
    except: pass

@ultroid_cmd("wiki", full_sudo=True)
async def wiki_handler(client, message):
    if len(message.command) < 2: return await eor(message, "Give me a query.")
    query = " ".join(message.command[1:])
    status = await eor(message, "Searching...")
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        res = requests.get(url).json()
        if "extract" in res:
            text = f"<b>{res['title']}</b>\n\n{res['extract']}\n\n<a href='{res['content_urls']['desktop']['page']}'>Read More</a>"
            await status.edit(text)
        else:
            await status.edit("No results found.")
    except Exception as e:
        await status.edit(f"Error: {e}")

# Echo Watcher
@Client.on_message(filters.text & ~filters.me, group=3)
async def echo_watcher(c, m):
    if m.chat.id in ECHO_CHATS:
        await m.copy(m.chat.id)