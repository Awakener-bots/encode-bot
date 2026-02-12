from pyrogram import Client, filters
from ..utils.helper import check_chat, get_id
from ..svcs.status_svc import add_sudo_user

@Client.on_message(filters.command('addsudo'))
async def add_sudo_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    target_id = get_id(message)
    success, text = await add_sudo_user(target_id)
    
    status = "● Success" if success else "✗ Failed"
    await message.reply(f"▸ <b>Sudo</b>\nStatus: {status}\n{text}")
