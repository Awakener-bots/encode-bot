import os
import time
from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..utils.uploads.telegram import upload_doc

@Client.on_message(filters.command('dupload'))
async def dupload_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    path = " ".join(message.command[1:]).strip()
    if not path or not os.path.exists(path):
        await message.reply("▸ <b>Upload</b>\nStatus: ✗ Failed\nReason: Invalid path provided.")
        return
        
    msg = await message.reply("▸ <b>Upload</b>\nStatus: ● Uploading...")
    try:
        await upload_doc(message, msg, time.time(), os.path.basename(path), path)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"▸ <b>Upload</b>\nStatus: ✗ Failed\nReason: {str(e)}")
