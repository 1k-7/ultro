import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from utils import ultroid_cmd, eor, get_user_id, SUDO_USERS

# --- Startup Helper ---
async def load_sudos():
    """
    Called by main.py to load sudo users from DB on startup.
    """
    try:
        stored_sudos = await db.get_key("SUDOS")
        if stored_sudos:
            count = 0
            for user_id in stored_sudos:
                # Ensure we only load integers
                uid = int(user_id)
                if uid not in SUDO_USERS:
                    SUDO_USERS.append(uid)
                    count += 1
            print(f"[Ultro] Loaded {count} Sudo Users from Database.")
    except Exception as e:
        print(f"[Ultro] Error loading Sudoers: {e}")

async def update_sudo_db():
    await db.set_key("SUDOS", SUDO_USERS)

# --- Commands ---

@ultroid_cmd("addsudo", full_sudo=True)
async def add_sudo_handler(client: Client, message: Message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user or provide an ID/Username.")
    
    if user_id in SUDO_USERS:
        try:
            u = await client.get_users(user_id)
            name = f"[{u.first_name}](tg://user?id={u.id})"
        except:
            name = f"`{user_id}`"
        return await eor(message, f"{name} `is already a SUDO User ...`")
    
    # Add
    SUDO_USERS.append(user_id)
    await update_sudo_db()
    
    try:
        u = await client.get_users(user_id)
        name = f"[{u.first_name}](tg://user?id={u.id})"
    except:
        name = f"`{user_id}`"
        
    # Ultroid Style Message
    await eor(message, f"**Added** {name} **as SUDO User**")

@ultroid_cmd("delsudo", full_sudo=True)
async def del_sudo_handler(client: Client, message: Message):
    user_id = await get_user_id(message)
    if not user_id:
        return await eor(message, "Reply to a user or provide an ID/Username.")
    
    try:
        u = await client.get_users(user_id)
        name = f"[{u.first_name}](tg://user?id={u.id})"
    except:
        name = f"`{user_id}`"

    if user_id not in SUDO_USERS:
        return await eor(message, f"{name} `wasn't a SUDO User ...`")
        
    # Remove
    SUDO_USERS.remove(user_id)
    await update_sudo_db()
    
    # Ultroid Style Message
    await eor(message, f"**Removed** {name} **from SUDO User(s)**")

@ultroid_cmd("listsudo", full_sudo=True)
async def list_sudo_handler(client: Client, message: Message):
    if not SUDO_USERS:
        return await eor(message, "❌ No Sudo Users found.")
        
    msg = "**SUDO MODE : True\n\nList of SUDO Users :**\n"
    
    for user_id in SUDO_USERS:
        try:
            user = await client.get_users(user_id)
            name = f"[{user.first_name}](tg://user?id={user_id})"
            msg += f"• {name} ( `{user_id}` )\n"
        except:
            msg += f"• `{user_id}` -> Invalid User\n"
            
    await eor(message, msg)