from pyrogram import filters, handlers, enums
from utils import ultroid_cmd, eor
from database import db

# Cache for speed (Optimization)
APPROVED_USERS = set()
WARN_LIMIT = 5 # Ultroid default is 5

@ultroid_cmd("a", full_sudo=True)
async def approve(client, message):
    """
    Approve a user to PM you.
    """
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif message.chat.type == enums.ChatType.PRIVATE:
        user_id = message.chat.id
    
    if not user_id:
        return await eor(message, "Reply to a user or use in PM.")

    APPROVED_USERS.add(user_id)
    # Optimization: Save as space-separated string
    await db.set_key("APPROVED_USERS", " ".join(map(str, APPROVED_USERS)))
    
    await eor(message, f"Approved to PM.")

@ultroid_cmd("da", full_sudo=True)
async def disapprove(client, message):
    """
    Disapprove a user from PMing you.
    """
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif message.chat.type == enums.ChatType.PRIVATE:
        user_id = message.chat.id

    if not user_id:
        return await eor(message, "Reply to a user or use in PM.")

    if user_id in APPROVED_USERS:
        APPROVED_USERS.remove(user_id)
        await db.set_key("APPROVED_USERS", " ".join(map(str, APPROVED_USERS)))
    
    await eor(message, f"Disapproved to PM.")

async def pm_guard(client, message):
    # 1. Check if Private Chat (FIXED ERROR HERE)
    if message.chat.type != enums.ChatType.PRIVATE:
        return
        
    # 2. Ignore Self, Bots, and Approved Users
    sender = message.from_user
    if not sender or sender.is_self or sender.is_bot:
        return
    if sender.id in APPROVED_USERS:
        return

    # 3. Warn Logic (Ultroid Style)
    key = f"warn_{sender.id}"
    warns = int(await db.get_key(key) or 0) + 1
    
    if warns >= WARN_LIMIT:
        await message.reply("<b>Start Spam Protection...</b>\nBlocked.")
        await client.block_user(sender.id)
        await db.del_key(key)
    else:
        await db.set_key(key, warns)
        # Exact Ultroid-style text response
        txt = (
            f"<b>Hello, {sender.first_name}!</b>\n"
            f"I am currently busy. Please wait for my approval.\n\n"
            f"<b>Do not send more messages or you will be blocked.</b>\n"
            f"<code>{warns}/{WARN_LIMIT}</code>"
        )
        await message.reply(txt)

def register_pmpermit(app):
    # Group 2 ensures this runs in parallel to commands
    app.add_handler(handlers.MessageHandler(pm_guard), group=2)