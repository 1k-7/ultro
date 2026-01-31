import time
from pyrogram import filters, handlers, enums
from utils import ultroid_cmd, eor
from database import db

# Global Cache
AFK_CACHE = {"status": False, "reason": "", "time": 0}

@ultroid_cmd("afk")
async def afk_handler(client, message):
    reason = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    
    AFK_CACHE.update({
        "status": True,
        "reason": reason,
        "time": int(time.time())
    })
    
    await db.set_key("AFK_STATUS", str(AFK_CACHE))
    
    # Ultroid style: Bold logic
    if reason:
        await eor(message, f"<b>AFK</b>\nReason: {reason}")
    else:
        await eor(message, "<b>AFK</b>")

async def afk_watcher(client, message):
    if not AFK_CACHE["status"]: 
        return

    # 1. Disable AFK if YOU send a message
    if message.from_user and message.from_user.is_self:
        # Ignore the .afk command itself
        if message.text and message.text.startswith((".afk", "!afk")): 
            return
        
        # Calculate duration
        start_time = AFK_CACHE["time"]
        end_time = int(time.time())
        total_time = end_time - start_time
        
        # Readable time format logic
        m, s = divmod(total_time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        
        t_str = ""
        if d: t_str += f"{d}d "
        if h: t_str += f"{h}h "
        if m: t_str += f"{m}m "
        t_str += f"{s}s"

        AFK_CACHE["status"] = False
        await db.del_key("AFK_STATUS")
        
        # Ultroid style "Back Alive" message
        await client.send_message(
            message.chat.id, 
            f"<b>No longer AFK.</b>\nWas away for: {t_str}"
        )
        return

    # 2. Reply if Mentioned or in PM
    should_reply = False
    if message.mentioned:
        should_reply = True
    elif message.chat.type == enums.ChatType.PRIVATE:
        should_reply = True
        
    if should_reply:
        # Prevent spam: basic check could be added here
        reason_txt = f"\nReason: {AFK_CACHE['reason']}" if AFK_CACHE['reason'] else ""
        await message.reply(f"<b>I am currently AFK.</b>{reason_txt}")

def register_afk(app):
    # Group 1 for watchers
    app.add_handler(handlers.MessageHandler(afk_watcher), group=1)