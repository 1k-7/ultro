import os
import requests
from utils import ultroid_cmd, eor

@ultroid_cmd("install")
async def install_handler(client, message):
    """
    Usage: Reply to a .py file or provide a raw GitHub URL to install a plugin.
    Example: .install https://raw.githubusercontent.com/.../plugin.py
    """
    reply = message.reply_to_message
    
    # 1. Check for URL argument
    if len(message.command) > 1:
        url = message.text.split(maxsplit=1)[1]
        filename = os.path.basename(url)
        if not filename.endswith(".py"):
            return await eor(message, "URL must end with .py")
            
        await eor(message, f"Installing `{filename}` from URL...")
        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(f"plugins/{filename}", "w") as f:
                    f.write(r.text)
            else:
                return await eor(message, "Failed to fetch code from URL.")
        except Exception as e:
            return await eor(message, f"Error: {e}")

    # 2. Check for Reply to File
    elif reply and reply.document:
        filename = reply.document.file_name
        if not filename.endswith(".py"):
            return await eor(message, "File must be a python (.py) script.")
            
        await eor(message, f"Installing `{filename}`...")
        await reply.download(f"plugins/{filename}")

    else:
        return await eor(message, "Reply to a .py file or give me a link.")

    await eor(message, f"✅ **Installed:** `{filename}`\nRestarting to apply changes...")
    
    # Auto-Restart
    import sys
    os.execl(sys.executable, sys.executable, "main.py")


@ultroid_cmd("uninstall")
async def uninstall_handler(client, message):
    """
    Usage: .uninstall <plugin_name>
    Removes a plugin from the plugins folder.
    """
    if len(message.command) < 2:
        return await eor(message, "Give me the plugin name to uninstall.")

    name = message.command[1]
    if not name.endswith(".py"):
        name += ".py"
        
    path = f"plugins/{name}"
    
    if os.path.exists(path):
        os.remove(path)
        await eor(message, f"🗑 **Uninstalled:** `{name}`\nRestarting...")
        import sys
        os.execl(sys.executable, sys.executable, "main.py")
    else:
        await eor(message, f"❌ Plugin `{name}` not found.")