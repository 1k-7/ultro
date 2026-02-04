import logging, os, ast
from pyrogram import Client, idle
from config import Config
from database import db

# Try to import optimized watchers and loaders
try:
    from plugins.afk import register_afk, AFK_CACHE
    from plugins.pmpermit import register_pmpermit, APPROVED_USERS
except ImportError:
    register_afk = register_pmpermit = None

try:
    from plugins.sudo import load_sudos
except ImportError:
    load_sudos = None

logging.basicConfig(level=logging.INFO)
app = Client(
    name="UltroPyro",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION,
    plugins=dict(root="plugins"), 
    in_memory=True,
    ipv6=False # ⚡ FIX: Disables IPv6 to prevent connection drops/timeouts
)

async def start_bot():
    print("--- Starting Pyroblack ---")
    await db.connect()
    
    # LOAD CACHE (Optimization)
    if register_afk:
        saved = await db.get_key("AFK_STATUS")
        if saved: AFK_CACHE.update(ast.literal_eval(saved))
        register_afk(app) # Enable Watcher

    if register_pmpermit:
        saved = await db.get_key("APPROVED_USERS")
        if saved: 
            for u in saved.split(): APPROVED_USERS.add(int(u))
        register_pmpermit(app) # Enable Watcher

    # Load Sudo Users
    if load_sudos:
        await load_sudos()

    await app.start()
    print("✅ Bot Running...")
    
    # Restart Handler
    if os.path.exists("restart.info"):
        with open("restart.info") as f:
            c, m = f.read().split()
            await app.edit_message_text(int(c), int(m), "✅ **Restarted!**")
        os.remove("restart.info")

    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(start_bot())