from pyrogram import filters, handlers, enums
from utils import ultroid_cmd, eor
from database import db

# Cache
APPROVED_USERS = set()
BLOCKED_USERS = set()
WARN_LIMIT = 5

@ultroid_cmd("a", full_sudo=True)
async def approve(client, message):
    """Approve a user to PM you."""
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif message.chat.type == enums.ChatType.PRIVATE:
        user_id = message.chat.id
    
    if not user_id:
        return await eor(message, "Reply to a user or use in PM.")

    if user_id in BLOCKED_USERS:
        BLOCKED_USERS.remove(user_id)
        await db.set_key("BLOCKED_USERS", " ".join(map(str, BLOCKED_USERS)))

    APPROVED_USERS.add(user_id)
    await db.set_key("APPROVED_USERS", " ".join(map(str, APPROVED_USERS)))
    
    await eor(message, f"✅ **Approved to PM.**")

@ultroid_cmd("da", full_sudo=True)
async def disapprove(client, message):
    """Disapprove a user."""
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
    
    await eor(message, f"❌ **Disapproved to PM.**")

@ultroid_cmd("block", full_sudo=True)
async def block_pm(client, message):
    """Block a user from PMing."""
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

    BLOCKED_USERS.add(user_id)
    await db.set_key("BLOCKED_USERS", " ".join(map(str, BLOCKED_USERS)))
    
    await client.block_user(user_id)
    await eor(message, f"🚫 **Blocked User.**")

@ultroid_cmd("unblock", full_sudo=True)
async def unblock_pm(client, message):
    """Unblock a user."""
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif message.chat.type == enums.ChatType.PRIVATE:
        user_id = message.chat.id

    if not user_id:
        return await eor(message, "Reply to a user or use in PM.")

    if user_id in BLOCKED_USERS:
        BLOCKED_USERS.remove(user_id)
        await db.set_key("BLOCKED_USERS", " ".join(map(str, BLOCKED_USERS)))
    
    await client.unblock_user(user_id)
    await eor(message, f"✅ **Unblocked User.**")

@ultroid_cmd("listapproved", full_sudo=True)
async def list_approved(client, message):
    """List all approved users."""
    if not APPROVED_USERS:
        return await eor(message, "No approved users.")
    
    text = "📝 **Approved Users:**\n\n"
    for uid in APPROVED_USERS:
        text += f"• <code>{uid}</code>\n"
        
    await eor(message, text)

async def pm_guard(client, message):
    if message.chat.type != enums.ChatType.PRIVATE: return
    
    sender = message.from_user
    if not sender or sender.is_self or sender.is_bot: return
    
    # Check Approved
    if sender.id in APPROVED_USERS: return
    
    # Check Blocked
    if sender.id in BLOCKED_USERS:
        await message.delete() # Auto-delete msg from blocked users
        return

    # Warn Logic
    key = f"warn_{sender.id}"
    warns = int(await db.get_key(key) or 0) + 1
    
    if warns >= WARN_LIMIT:
        await message.reply("<b>Start Spam Protection...</b>\nBlocked.")
        await client.block_user(sender.id)
        
        BLOCKED_USERS.add(sender.id)
        await db.set_key("BLOCKED_USERS", " ".join(map(str, BLOCKED_USERS)))
        await db.del_key(key)
    else:
        await db.set_key(key, warns)
        txt = (
            f"<b>Hello, {sender.first_name}!</b>\n"
            f"I am currently busy. Please wait for my approval.\n\n"
            f"<b>Do not send more messages or you will be blocked.</b>\n"
            f"<code>{warns}/{WARN_LIMIT}</code>"
        )
        await message.reply(txt)

def register_pmpermit(app):
    app.add_handler(handlers.MessageHandler(pm_guard), group=2)