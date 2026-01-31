import sys, os, glob
from utils import ultroid_cmd, eor, run_cmd
from config import Config

@ultroid_cmd("restart", full_sudo=True)
async def restart_handler(client, message):
    msg = await eor(message, "Restarting...")
    with open("restart.info", "w") as f: f.write(f"{msg.chat.id}\n{msg.id}")
    os.execl(sys.executable, sys.executable, "main.py")

@ultroid_cmd("shutdown", full_sudo=True)
async def shutdown_handler(client, message):
    await eor(message, "Shutting down...")
    sys.exit()

@ultroid_cmd("logs", full_sudo=True)
async def logs_handler(client, message):
    if os.path.exists("pyroblack.log"):
        await client.send_document(message.chat.id, "pyroblack.log", caption="Logs")
    else:
        await eor(message, "No logs found.")

@ultroid_cmd("update", full_sudo=True)
async def update_handler(client, message):
    msg = await eor(message, "Checking updates...")
    await run_cmd("git fetch origin")
    stdout, _, _, _ = await run_cmd("git status -uno")
    if "up to date" in stdout: return await msg.edit("Already up to date.")
    
    await msg.edit("Updating...")
    await run_cmd("git pull")
    await msg.edit("Updated! Restarting...")
    
    with open("restart.info", "w") as f: f.write(f"{msg.chat.id}\n{msg.id}")
    os.execl(sys.executable, sys.executable, "main.py")