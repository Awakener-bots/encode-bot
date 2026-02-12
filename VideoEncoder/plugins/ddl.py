from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..svcs.user_svc import add_user_if_new
from ..svcs.queue_svc import queue_svc
from ..svcs.encode_svc import start_encode_task

@Client.on_message(filters.command('ddl'))
async def ddl_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
        
    if len(message.text.split()) == 1:
        await message.reply_text("▸ <b>Usage</b>\n<code>/ddl [url] | [optional_filename]</code>")
        return
        
    await add_user_if_new(app, message)
    await queue_svc.add(message, 'url', start_encode_task)
