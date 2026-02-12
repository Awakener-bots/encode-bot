from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..svcs.user_svc import add_user_if_new
from ..svcs.queue_svc import queue_svc
from ..svcs.encode_svc import start_encode_task

@Client.on_message(filters.command('batch'))
async def batch_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
        
    if len(message.text.split()) == 1 and not message.reply_to_message:
        await message.reply_text("▸ <b>Usage</b>\n<code>/batch [url]</code> or reply to a zip file.")
        return
        
    await add_user_if_new(app, message)
    await queue_svc.add(message, 'batch', start_encode_task)
