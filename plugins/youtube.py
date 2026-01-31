import os, glob, asyncio, yt_dlp
from utils import ultroid_cmd, eor

@ultroid_cmd("yt")
async def yt_dl(client, message):
    """Usage: .yt <link>"""
    if len(message.command) < 2: return await eor(message, "Give me a link.")
    
    url = message.text.split(maxsplit=1)[1]
    status = await eor(message, "⬇️ Downloading...")
    temp = f"downloads/yt_{message.id}"
    os.makedirs(temp, exist_ok=True)
    
    opts = {'outtmpl': f'{temp}/%(title)s.%(ext)s', 'noplaylist': True, 'quiet': True}
    
    try:
        # Run sync function in thread
        await asyncio.to_thread(run_yt, opts, url)
        
        files = glob.glob(f"{temp}/*")
        if files:
            await status.edit("⬆️ Uploading...")
            await client.send_document(message.chat.id, document=files[0], caption=f"`{os.path.basename(files[0])}`")
            await status.delete()
        else:
            await status.edit("❌ Download failed.")
    except Exception as e:
        await status.edit(f"Error: {e}")
    finally:
        import shutil
        if os.path.exists(temp): shutil.rmtree(temp)

def run_yt(opts, url):
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])