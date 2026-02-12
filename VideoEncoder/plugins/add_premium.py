from pyrogram import Client, filters
from ..utils.helper import check_chat, get_id
from ..db.users import users_db
from ..core.log import log

@Client.on_message(filters.command('addpremium'))
async def add_premium_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    target_id = get_id(message)
    if not target_id:
        await message.reply("▸ <b>Premium</b>\nStatus: ✗ Failed\nReason: No user ID provided.")
        return
    
    try:
        target_id = int(target_id)
    except:
        await message.reply("▸ <b>Premium</b>\nStatus: ✗ Failed\nReason: Invalid user ID.")
        return
    
    if not await users_db.is_user_exist(target_id):
        await message.reply("▸ <b>Premium</b>\nStatus: ✗ Failed\nReason: User not found in database.")
        return
    
    user = await users_db.get_user(target_id)
    if user.get('premium', False):
        await message.reply(f"▸ <b>Premium</b>\nStatus: ✗ Failed\nReason: User {target_id} is already premium.")
        return
    
    await users_db.update_user(target_id, {'premium': True})
    log.inf("premium_add", u_id=target_id, by=message.from_user.id if message.from_user else "system")
    
    await message.reply(f"▸ <b>Premium</b>\nStatus: ● Success\nUser {target_id} is now a premium member! 👑")
