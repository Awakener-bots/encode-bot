from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..utils.helper import check_chat, get_id
from ..svcs.settings_svc import settings_svc

@Client.on_message(filters.command("vset"))
async def vset_handler(bot: Client, message):
    
    if message.chat.type != "private":
        bot_info = await bot.get_me()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("View Settings in DM", url=f"https://t.me/{bot_info.username}?start=vset")]
        ])
        await message.reply(
            "▸ <b>Settings</b>\n"
            "Status: ● Private Only\n\n"
            "<blockquote>Settings can only be viewed in private chat.\n"
            "Please DM me to view your encoding profile.</blockquote>",
            reply_markup=keyboard
        )
        return
        
    target_id = get_id(message)
    text = await settings_svc.get_settings_summary(target_id)
    await message.reply(text)
