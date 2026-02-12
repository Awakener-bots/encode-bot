from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..utils.helper import check_chat
from ..svcs.settings_svc import settings_svc
from ..svcs.user_svc import add_user_if_new

async def dm_only_message(message, bot_username):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Open Settings in DM", url=f"https://t.me/{bot_username}?start=settings")]
    ])
    await message.reply(
        "▸ <b>Settings</b>\n"
        "Status: ● Private Only\n\n"
        "<blockquote>Settings can only be configured in private chat.\n"
        "Please DM me to manage your encoding preferences.</blockquote>",
        reply_markup=keyboard
    )

@Client.on_message(filters.command("settings"))
async def settings_command_handler(bot: Client, message):
    if message.chat.type != "private":
        bot_info = await bot.get_me()
        await dm_only_message(message, bot_info.username)
        return
        
    await add_user_if_new(bot, message)
    text, markup = await settings_svc.get_main_menu()
    await message.reply(text, reply_markup=markup)
