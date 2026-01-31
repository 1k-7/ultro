import os
import glob
from utils import ultroid_cmd, eor

@ultroid_cmd("help")
async def help_handler(client, message):
    """
    Lists available plugins.
    """
    plugins = glob.glob("plugins/*.py")
    # Clean up names
    plugin_names = sorted([
        os.path.basename(p)[:-3] 
        for p in plugins 
        if not p.endswith("__init__.py")
    ])
    
    count = len(plugin_names)
    
    # Ultroid Style Text
    txt = f"<b>Pyroblack Userbot</b>\n"
    txt += f"<b>Modules:</b> <code>{count}</code>\n\n"
    
    # Grid Layout
    for name in plugin_names:
        txt += f"• <code>{name}</code>\n"
        
    await eor(message, txt)