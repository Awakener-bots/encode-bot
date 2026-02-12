from pyrogram import Client, filters
from ..utils.helper import check_chat, get_id
from ..svcs.status_svc import add_auth_chat

@Client.on_message(filters.command('addchat'))
async def add_chat_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    target_id = get_id(message)
    success, text = await add_auth_chat(target_id)
    
    status = "● Success" if success else "✗ Failed"
    await message.reply(f"▸ <b>Auth</b>\nStatus: {status}\n{text}")
