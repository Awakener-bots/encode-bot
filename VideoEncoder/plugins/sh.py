import asyncio
import html
from io import BytesIO
from pyrogram import Client, filters
from ..utils.helper import check_chat

@Client.on_message(filters.command('sh'))
async def sh_handler(client, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    command = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not command:
        await message.reply_text("▸ <b>Usage</b>\n<code>/sh [command]</code>")
        return
        
    reply = await message.reply_text("▸ <b>Shell</b>\nStatus: ● Executing...")
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    
    stdout_text = stdout.decode().strip()
    stderr_text = stderr.decode().strip()
    
    output = f"<b>Exit Code:</b> <code>{process.returncode}</code>\n\n"
    if stderr_text:
        output += f"<b>Stderr:</b>\n<code>{html.escape(stderr_text)}</code>\n"
    if stdout_text:
        output += f"<b>Stdout:</b>\n<code>{html.escape(stdout_text)}</code>"
        
    if len(output) > 4000:
        f = BytesIO((stderr_text + "\n" + stdout_text).encode('utf-8'))
        f.name = "output.txt"
        await reply.delete()
        await message.reply_document(f, caption=f"▸ <b>Shell Result</b>\nStatus: ● Success\nExit Code: <code>{process.returncode}</code>")
    else:
        await reply.edit_text(f"▸ <b>Shell Result</b>\nStatus: ● Success\n{output}")
