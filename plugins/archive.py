import os
import shutil
import zipfile
import time
import traceback
import asyncio
from utils import ultroid_cmd, eor

@ultroid_cmd("unzip")
async def unzip_handler(client, message):
    """
    Usage: Reply to a .zip file with .unzip
    Extracts the contents and uploads them to the current chat.
    """
    reply = message.reply_to_message
    
    if not reply or not reply.document:
        return await eor(message, "Please reply to a zip file.")
    
    status = await eor(message, "Downloading file...")
    
    # Define temporary paths
    timestamp = int(time.time())
    out_dir = f"downloads/unzip_{timestamp}"
    
    try:
        # 1. Download
        dl_path = await reply.download()
        
        if not dl_path:
            return await status.edit("Download failed.")
            
        await status.edit("Checking file integrity...")

        # 2. Verify it is a zip
        if not zipfile.is_zipfile(dl_path):
            await status.edit("❌ Error: This is not a valid zip file.")
            os.remove(dl_path)
            return

        # 3. Extract
        await status.edit(f"Unzipping to `{out_dir}`...")
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        try:
            with zipfile.ZipFile(dl_path, 'r') as zip_ref:
                zip_ref.extractall(out_dir)
        except zipfile.BadZipFile:
            await status.edit("❌ Error: Corrupt or password-protected zip file.")
            # Cleanup
            os.remove(dl_path)
            shutil.rmtree(out_dir)
            return

        # 4. Gather extracted files
        files_to_send = []
        for root, dirs, files in os.walk(out_dir):
            for file in files:
                files_to_send.append(os.path.join(root, file))

        if not files_to_send:
            await status.edit("The zip file was empty.")
            return

        # 5. Upload files
        total_files = len(files_to_send)
        await status.edit(f"Found {total_files} files. Starting upload...")
        
        chat_id = message.chat.id
        
        for i, file_path in enumerate(files_to_send):
            caption = os.path.basename(file_path)
            
            # Update status every 5 files to prevent floodwaits/lag
            if i % 5 == 0:
                await status.edit(f"Uploading {i+1}/{total_files}: `{caption}`")
            
            # Upload the file
            await client.send_document(
                chat_id=chat_id,
                document=file_path,
                caption=f"`{caption}`",
                force_document=True
            )
            # Small sleep to be kind to the API
            await asyncio.sleep(0.5)

        await status.edit(f"✅ Extracted and uploaded {total_files} files.")

    except Exception as e:
        await status.edit(f"❌ Error:\n`{str(e)[:1000]}`")
        traceback.print_exc()

    finally:
        # 6. Cleanup Storage
        if 'dl_path' in locals() and dl_path and os.path.exists(dl_path):
            os.remove(dl_path)
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)


@ultroid_cmd("zip")
async def zip_handler(client, message):
    """
    Usage: Reply to a file or media with .zip
    Downloads the file and compresses it into a zip archive.
    """
    reply = message.reply_to_message
    
    if not reply:
        return await eor(message, "Reply to a file/media to zip it.")

    status = await eor(message, "Downloading media...")
    
    timestamp = int(time.time())
    dl_folder = f"downloads/zip_{timestamp}"
    zip_path = f"downloads/archive_{timestamp}.zip"
    
    try:
        # 1. Download
        dl_file = await reply.download(file_name=dl_folder + "/")
        
        if not dl_file:
            return await status.edit("Download failed.")

        # 2. Compress
        await status.edit("Zipping...")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add file to zip (arcname ensures we don't include the full path structure)
            zipf.write(dl_file, arcname=os.path.basename(dl_file))

        # 3. Upload Zip
        await status.edit("Uploading archive...")
        
        await client.send_document(
            chat_id=message.chat.id,
            document=zip_path,
            caption=f"**Zipped:** `{os.path.basename(dl_file)}`",
            force_document=True
        )
        
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Error:\n`{str(e)}`")
        traceback.print_exc()

    finally:
        # 4. Cleanup
        if os.path.exists(dl_folder):
            shutil.rmtree(dl_folder)
        if os.path.exists(zip_path):
            os.remove(zip_path)