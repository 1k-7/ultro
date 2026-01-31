import requests
from utils import ultroid_cmd, eor

@ultroid_cmd("tr")
async def translate_handler(client, message):
    """
    .tr <lang> <text/reply>
    Translates text.
    """
    if len(message.command) < 2 and not message.reply_to_message:
        return await eor(message, "Usage: .tr en <text>")
    
    target_lang = "en"
    text = ""
    
    if len(message.command) > 1:
        if len(message.command[1]) == 2: # heuristic for lang code
            target_lang = message.command[1]
            text = " ".join(message.command[2:])
        else:
            text = " ".join(message.command[1:])
            
    if message.reply_to_message:
        if not text: text = message.reply_to_message.text or message.reply_to_message.caption
        
    if not text: return await eor(message, "No text found.")
    
    status = await eor(message, "Translating...")
    
    try:
        # Using a free unofficial API endpoint for basic translation
        url = "https://clients5.google.com/translate_a/t"
        params = {
            "client": "dict-chrome-ex",
            "sl": "auto",
            "tl": target_lang,
            "q": text
        }
        r = requests.get(url, params=params).json()
        translated = r[0][0]
        
        await status.edit(f"<b>Translated ({target_lang}):</b>\n<code>{translated}</code>")
    except Exception as e:
        await status.edit(f"Error: {e}")

@ultroid_cmd("ud")
async def ud_handler(client, message):
    """ .ud <query>: Urban Dictionary Search """
    if len(message.command) < 2: return await eor(message, "Give me a word.")
    word = " ".join(message.command[1:])
    
    try:
        r = requests.get(f"https://api.urbandictionary.com/v0/define?term={word}").json()
        if not r['list']: return await eor(message, "No definition found.")
        
        item = r['list'][0]
        definition = item['definition'].replace("[", "").replace("]", "")
        example = item['example'].replace("[", "").replace("]", "")
        
        txt = (
            f"<b>Word:</b> {item['word']}\n\n"
            f"<b>Definition:</b>\n{definition[:500]}\n\n"
            f"<b>Example:</b>\n{example[:300]}"
        )
        await eor(message, txt)
    except Exception as e: await eor(message, f"Error: {e}")

@ultroid_cmd("short")
async def short_handler(client, message):
    """ .short <url>: Shorten URL using is.gd """
    if len(message.command) < 2: return await eor(message, "Give me a link.")
    link = message.command[1]
    try:
        r = requests.get(f"https://is.gd/create.php?format=simple&url={link}")
        if r.status_code == 200:
            await eor(message, f"<b>Shortened:</b> {r.text}")
        else:
            await eor(message, "Error shortening link.")
    except Exception as e: await eor(message, f"Error: {e}")