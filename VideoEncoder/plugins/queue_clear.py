from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..svcs.queue_svc import queue_svc

@Client.on_message(filters.command('clear'))
async def clear_queue_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    queue_svc.clear_queue()
    await message.reply("▸ <b>Queue</b>\nStatus: ● Cleared\nAll pending tasks have been removed.")
