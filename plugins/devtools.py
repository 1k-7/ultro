import sys, traceback, io, os, asyncio
from utils import ultroid_cmd, eor

@ultroid_cmd("sysinfo", full_sudo=True)
async def sysinfo_handler(client, message):
    status = await eor(message, "Fetching info...")
    cmd = "neofetch --stdout"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    output = stdout.decode().strip() or f"Linux {os.uname().release}"
    await status.edit(f"**System Info:**\n\n`{output}`")

@ultroid_cmd("bash", full_sudo=True, only_devs=True)
async def bash_handler(client, message):
    if len(message.command) < 2: return await eor(message, "Usage: .bash <cmd>")
    cmd = message.text.split(maxsplit=1)[1]
    status = await eor(message, "Running...")
    
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    out, err = stdout.decode(), stderr.decode()
    
    res = f"**BASH:** `{cmd}`\n\n"
    if out: res += f"**Output:**\n`{out}`\n"
    if err: res += f"**Error:**\n`{err}`\n"
    
    if len(res) > 4096:
        with io.BytesIO(res.encode()) as f:
            f.name = "bash.txt"
            await client.send_document(message.chat.id, f, caption=f"`{cmd}`")
        await status.delete()
    else:
        await status.edit(res)

@ultroid_cmd("eval", full_sudo=True, only_devs=True)
async def eval_handler(client, message):
    if len(message.command) < 2: return await eor(message, "Usage: .eval <code>")
    cmd = message.text.split(maxsplit=1)[1]
    status = await eor(message, "Running...")
    
    old_stdout, old_stderr = sys.stdout, sys.stderr
    redirected_out = sys.stdout = io.StringIO()
    redirected_err = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    
    try:
        await aexec(cmd, client, message)
    except: exc = traceback.format_exc()
    
    stdout = redirected_out.getvalue()
    stderr = redirected_err.getvalue()
    sys.stdout, sys.stderr = old_stdout, old_stderr
    
    evaluation = exc or stderr or stdout or "Success"
    final = f"**EVAL:**\n`{cmd}`\n\n**OUTPUT:**\n`{evaluation}`"
    
    if len(final) > 4096:
        with io.BytesIO(final.encode()) as f:
            f.name = "eval.txt"
            await client.send_document(message.chat.id, f, caption="Eval Output")
        await status.delete()
    else:
        await status.edit(final)

async def aexec(code, client, message):
    exec(f"async def __aexec(client, message): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](client, message)

# C++ Support (Requires g++ installed)
@ultroid_cmd("cpp", full_sudo=True, only_devs=True)
async def cpp_handler(client, message):
    if len(message.command) < 2: return await eor(message, "Usage: .cpp <code/main>")
    code = message.text.split(maxsplit=1)[1]
    status = await eor(message, "Compiling...")
    
    if "main" not in code:
        code = f"#include <iostream>\nusing namespace std;\nint main() {{\n{code}\nreturn 0;\n}}"
        
    with open("temp.cpp", "w") as f: f.write(code)
    
    # Compile
    proc = await asyncio.create_subprocess_shell("g++ -o temp_exec temp.cpp", stderr=asyncio.subprocess.PIPE)
    _, stderr = await proc.communicate()
    
    if stderr:
        await status.edit(f"**Compile Error:**\n`{stderr.decode()}`")
        return os.remove("temp.cpp")

    # Run
    proc = await asyncio.create_subprocess_shell("./temp_exec", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    
    res = f"**CPP:**\n`{code}`\n\n**Output:**\n`{stdout.decode()}`"
    if stderr: res += f"\n**Runtime Error:**\n`{stderr.decode()}`"
    
    await status.edit(res)
    if os.path.exists("temp.cpp"): os.remove("temp.cpp")
    if os.path.exists("temp_exec"): os.remove("temp_exec")