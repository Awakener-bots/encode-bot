import os
import time
from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..utils.encoding import get_duration, get_thumbnail, get_width_height
from ..utils.uploads.telegram import upload_video
from ..core.cfg import cfg

@Client.on_message(filters.command('vupload'))
async def vupload_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    path = " ".join(message.command[1:]).strip()
    if not path or not os.path.exists(path):
        await message.reply("▸ <b>Upload</b>\nStatus: ✗ Failed\nReason: Invalid path provided.")
        return
        
    msg = await message.reply("▸ <b>Upload</b>\nStatus: ● Preparing metadata...")
    try:
        duration = get_duration(path)
        thumb = get_thumbnail(path, cfg.DOWNLOAD_DIR, duration / 4)
        width, height = get_width_height(path)
        
        await msg.edit("▸ <b>Upload</b>\nStatus: ● Uploading video...")
        await upload_video(message, msg, path, os.path.basename(path), time.time(), thumb, duration, width, height)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"▸ <b>Upload</b>\nStatus: ✗ Failed\nReason: {str(e)}")
