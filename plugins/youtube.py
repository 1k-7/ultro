import os
import glob
import asyncio
import time
import math
import requests # Added for thumbnail download
import yt_dlp
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils import ultroid_cmd, eor

# --- Helpers for Progress & Formatting ---

def humanbytes(size):
    if not size: return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN.get(n, '') + 'B'

def time_formatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s") if seconds else "")
    return tmp

async def progress(current, total, message, start_time, action_name):
    now = time.time()
    diff = now - start_time
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        
        progress_str = "[{0}{1}] {2}%\n".format(
            ''.join(["●" for i in range(math.floor(percentage / 10))]),
            ''.join(["○" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2))
            
        tmp = progress_str + \
            f"{action_name}...\n" + \
            f"✅ Done: {humanbytes(current)} of {humanbytes(total)}\n" + \
            f"🚀 Speed: {humanbytes(speed)}/s\n" + \
            f"⏳ ETA: {time_formatter(estimated_total_time) if estimated_total_time else '0 s'}"
            
        try:
            await message.edit(tmp)
        except:
            pass

# --- YouTube Logic ---

def _run_download_sync(opts, url):
    """Blocking yt_dlp function to be run in a thread."""
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info

def _download_thumb_sync(url, path):
    """Blocking thumbnail download."""
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

async def download_yt_content(client, message, url, as_video=True, as_document=False):
    status = await eor(message, "🔎 **Fetching information...**")
    temp_dir = f"downloads/{message.id}"
    os.makedirs(temp_dir, exist_ok=True)

    # 1. Configure yt_dlp
    ydl_opts = {
        'quiet': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
        'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        'noplaylist': True,
        'writethumbnail': False, # We handle thumbnail manually for better compatibility
        'socket_timeout': 60,
        'ignoreerrors': True,
    }

    if as_video:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['key'] = 'FFmpegMetadata'
        ydl_opts['prefer_ffmpeg'] = True
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        ydl_opts['outtmpl'] = f'{temp_dir}/%(title)s.mp3'

    # 2. Run Download
    info_dict = None
    try:
        await status.edit("⬇️ **Downloading...**")
        loop = asyncio.get_running_loop()
        info_dict = await loop.run_in_executor(None, _run_download_sync, ydl_opts, url)
        
        if not info_dict:
            return await status.edit("❌ **Download Failed.**")
    except Exception as e:
        return await status.edit(f"❌ **Error:** `{str(e)}`")

    # 3. Handle Thumbnail (Manual Download like Ultroid)
    thumb_file = None
    if as_video:
        thumb_url = info_dict.get("thumbnail")
        if thumb_url:
            thumb_path = os.path.join(temp_dir, "thumb.jpg")
            # Download thumb in executor to avoid blocking
            success = await loop.run_in_executor(None, _download_thumb_sync, thumb_url, thumb_path)
            if success:
                thumb_file = thumb_path

    # 4. Locate Main File
    files = glob.glob(f"{temp_dir}/*")
    main_file = None

    for f in files:
        if f == thumb_file: continue
        # Robust video extension check
        if f.lower().endswith((".mp4", ".mkv", ".webm", ".avi", ".flv", ".mov", ".mp3", ".m4a", ".flac", ".ogg", ".wav")):
            main_file = f
            break
            
    if not main_file:
        # Fallback to any non-thumb file
        for f in files:
            if f != thumb_file:
                main_file = f
                break

    if not main_file:
        return await status.edit("❌ **Error:** Media file missing.")

    # 5. Upload
    await status.edit("⬆️ **Uploading...**")
    start_time = time.time()
    
    duration = int(info_dict.get("duration", 0))
    title = info_dict.get("title", "Unknown")
    performer = info_dict.get("uploader", "Unknown")
    w = 0
    h = 0
    
    if as_video:
        w = int(info_dict.get("width", 0))
        h = int(info_dict.get("height", 0))

    caption = f"🎬 **{title}**\n" \
              f"👤 {performer}\n" \
              f"🔗 [Source]({url})"

    try:
        if as_document:
            await client.send_document(
                message.chat.id,
                document=main_file,
                thumb=thumb_file,
                caption=caption,
                progress=progress,
                progress_args=(status, start_time, "Uploading File")
            )
        elif as_video:
            await client.send_video(
                message.chat.id,
                video=main_file,
                thumb=thumb_file, # Now explicitly a JPG
                caption=caption,
                supports_streaming=True,
                duration=duration,
                width=w,
                height=h,
                progress=progress,
                progress_args=(status, start_time, "Uploading Video")
            )
        else:
            await client.send_audio(
                message.chat.id,
                audio=main_file,
                thumb=thumb_file,
                caption=caption,
                duration=duration,
                title=title,
                performer=performer,
                progress=progress,
                progress_args=(status, start_time, "Uploading Audio")
            )
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ **Upload Error:** `{e}`")
    finally:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# --- Argument Parser ---
def parse_args(message):
    text = message.text
    args = text.split()
    as_doc = "-d" in args
    link_parts = [x for x in args[1:] if x != "-d"]
    url = link_parts[0] if link_parts else None
    return url, as_doc

# --- Commands ---

@ultroid_cmd("yt")
async def yt_handler(client, message):
    if len(message.command) < 2:
        return await eor(message, "Usage: .yt <link> [-d]")
    url, as_doc = parse_args(message)
    if not url: return await eor(message, "❌ Link not found.")
    await download_yt_content(client, message, url, as_video=True, as_document=as_doc)

@ultroid_cmd("ytv")
async def ytv_handler(client, message):
    if len(message.command) < 2:
        return await eor(message, "Usage: .ytv <link> [-d]")
    url, as_doc = parse_args(message)
    if not url: return await eor(message, "❌ Link not found.")
    await download_yt_content(client, message, url, as_video=True, as_document=as_doc)

@ultroid_cmd("yta")
async def yta_handler(client, message):
    if len(message.command) < 2:
        return await eor(message, "Usage: .yta <link> [-d]")
    url, as_doc = parse_args(message)
    if not url: return await eor(message, "❌ Link not found.")
    await download_yt_content(client, message, url, as_video=False, as_document=as_doc)

@ultroid_cmd("ytsv")
async def ytsv_handler(client, message):
    if len(message.command) < 2:
        return await eor(message, "Usage: .ytsv <query>")
    query = message.text.split(maxsplit=1)[1]
    url = f"ytsearch1:{query}"
    await download_yt_content(client, message, url, as_video=True)

@ultroid_cmd("ytsa")
async def ytsa_handler(client, message):
    if len(message.command) < 2:
        return await eor(message, "Usage: .ytsa <query>")
    query = message.text.split(maxsplit=1)[1]
    url = f"ytsearch1:{query}"
    await download_yt_content(client, message, url, as_video=False)