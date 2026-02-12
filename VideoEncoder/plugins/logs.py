from pyrogram import Client, filters
from ..utils.helper import check_chat

@Client.on_message(filters.command('logs'))
async def logs_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    import os
    log_file = 'VideoEncoder/utils/extras/logs.txt'
    if not os.path.exists(log_file):
        await message.reply("▸ <b>Logs</b>\nStatus: ✗ Not Found")
        return
        
    await message.reply_document(log_file, caption="▸ <b>Logs</b>\nStatus: ● Active")
