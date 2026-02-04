import asyncio
from pyrogram import Client, enums
from pyrogram.types import Message
from utils import ultroid_cmd, eor

def get_mention(member):
    """Returns a mention string for the member."""
    user = member.user
    name = user.first_name if user.first_name else "User"
    return f"<a href='tg://user?id={user.id}'>{name}</a>"

@ultroid_cmd(
    pattern="tagall|tagadmins|tagowner|tagbots|tagrec|tagon|tagoff",
    groups_only=True
)
async def tag_handler(client: Client, message: Message):
    cmd = message.command[0].lower()
    
    # Extract custom text if provided (e.g., .tagall Hello)
    custom_text = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    
    status_msg = await eor(message, "<code>Fetching members...</code>")
    
    mentions = f"{custom_text}\n" if custom_text else ""
    count = 0
    limit = 100 # Match Ultroid's limit to prevent flood
    
    async for member in client.get_chat_members(message.chat.id, limit=limit):
        if member.user.is_deleted:
            continue

        should_tag = False
        user = member.user
        
        # Logic Mapping
        if cmd == "tagall" and not user.is_bot:
            should_tag = True
            
        elif cmd == "tagadmins" and (member.status == enums.ChatMemberStatus.ADMINISTRATOR or member.status == enums.ChatMemberStatus.OWNER):
            should_tag = True
            
        elif cmd == "tagowner" and member.status == enums.ChatMemberStatus.OWNER:
            should_tag = True
            
        elif cmd == "tagbots" and user.is_bot:
            should_tag = True
            
        elif cmd == "tagon" and user.status == enums.UserStatus.ONLINE:
            should_tag = True
            
        elif cmd == "tagoff" and user.status == enums.UserStatus.OFFLINE:
            should_tag = True
            
        elif cmd == "tagrec" and user.status in [enums.UserStatus.ONLINE, enums.UserStatus.RECENTLY]:
            should_tag = True

        if should_tag:
            mentions += f"{get_mention(member)}\n"
            count += 1

    if count == 0:
        await status_msg.edit(f"❌ Found no members to tag for `{cmd}`.")
    else:
        await status_msg.delete()
        await client.send_message(
            message.chat.id,
            mentions,
            reply_to_message_id=message.reply_to_message_id or message.id
        )