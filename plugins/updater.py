import os
import sys
from utils import ultroid_cmd, eor, run_cmd
from config import Config

@ultroid_cmd("update")
async def update_handler(client, message):
    """
    Usage: .update
    Pulls changes from the upstream git repo.
    """
    msg = await eor(message, "Checking for updates...")
    
    # Check if git exists
    try:
        await run_cmd("git --version")
    except:
        return await msg.edit("Git is not installed on this server.")

    # 1. Fetch
    await run_cmd("git fetch origin")
    
    # 2. Check status
    stdout, _, _, _ = await run_cmd("git status -uno")
    
    if "Your branch is up to date" in stdout:
        return await msg.edit(f"✅ Bot is already up to date with `{Config.UPSTREAM_REPO}`")
    
    # 3. Pull
    await msg.edit(f"Updates found! Pulling from `{Config.UPSTREAM_REPO}`...")
    
    stdout, stderr, _, _ = await run_cmd("git pull")
    
    if "Already up to date" in stdout:
        return await msg.edit("Strange... Git says already up to date.")
        
    # 4. Restart
    await msg.edit(f"✅ **Updated!**\n\n**Changelog:**\n`{stdout[:500]}`\n\nRestarting...")
    
    # Persistence for restart message (from previous logic)
    with open("restart.info", "w") as f:
        f.write(f"{message.chat.id}\n{msg.id}")

    os.execl(sys.executable, sys.executable, "main.py")