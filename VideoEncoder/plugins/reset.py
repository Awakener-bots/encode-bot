from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..utils.helper import check_chat
from ..db.users import users_db

@Client.on_message(filters.command("reset"))
async def reset_handler(bot: Client, message):
    if not await check_chat(message, chat='Both'):
        return
    
    if message.chat.type != "private":
        bot_info = await bot.get_me()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Reset Settings in DM", url=f"https://t.me/{bot_info.username}?start=reset")]
        ])
        await message.reply(
            "▸ <b>Reset</b>\n"
            "Status: ● Private Only\n\n"
            "<blockquote>Settings can only be reset in private chat.\n"
            "Please DM me to reset your encoding preferences.</blockquote>",
            reply_markup=keyboard
        )
        return
        
    u_id = message.from_user.id
    await users_db.delete_user(u_id)
    await users_db.add_user(u_id)
    
    await message.reply("▸ <b>Settings</b>\nStatus: ● Reset\nYour settings have been reset to default.")
