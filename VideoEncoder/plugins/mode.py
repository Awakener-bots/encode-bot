from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..utils.helper import check_chat
from ..db.status import status_db

@Client.on_message(filters.command("mode"))
async def mode_handler(bot: Client, message):
    if not await check_chat(message, chat='Sudo'):
        return
    
    is_public = await status_db.get_public_mode()
    mode_text = "Public" if is_public else "Private"
    
    text = (
        "▸ <b>Bot Mode Settings</b>\n"
        f"Current Mode: ● <b>{mode_text}</b>\n\n"
        "<blockquote>"
        "<b>Public:</b> Anyone can use the bot.\n"
        "<b>Private:</b> Only Sudo and Authorized chats can use the bot."
        "</blockquote>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Set {'Private' if is_public else 'Public'} Mode", callback_data="toggle_mode")],
        [InlineKeyboardButton("Close", callback_data="close_mode")]
    ])
    
    await message.reply(text, reply_markup=keyboard)
