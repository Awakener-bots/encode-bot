from pyrogram import Client, filters
from ..db.users import users_db
from ..svcs.settings_svc import settings_svc
from ..utils.helper import check_chat

@Client.on_message(filters.reply & filters.private)
async def settings_input_handler(bot: Client, message):
    if not message.reply_to_message:
        return
        
    reply_text = message.reply_to_message.text
    user_input = message.text
    u_id = message.from_user.id
    
    if "Rename Policy" in reply_text:
        await users_db.update_user(u_id, {"rename_template": user_input})
        text, markup = await settings_svc.get_extra_settings(u_id)
        await message.reply(f"▸ <b>Rename Policy</b>\nStatus: ● Updated\nNew Template: <code>{user_input}</code>")
        await message.reply(text, reply_markup=markup)
        
    elif "Watermark Text" in reply_text:
        await users_db.update_user(u_id, {"watermark_text": user_input})
        text, markup = await settings_svc.get_extra_settings(u_id)
        await message.reply(f"▸ <b>Watermark Text</b>\nStatus: ● Updated\nNew Text: <code>{user_input}</code>")
        await message.reply(text, reply_markup=markup)

@Client.on_message(filters.photo & filters.private)
async def thumb_input_handler(bot: Client, message):
    if not await check_chat(message, chat='Both'):
        return
        
    u_id = message.from_user.id
    photo = message.photo
    file_id = photo.file_id
    
    await users_db.update_user(u_id, {"custom_thumbnail": file_id})
    text, markup = await settings_svc.get_thumb_settings(u_id)
    await message.reply("▸ <b>Thumbnail</b>\nStatus: ● Saved\nYour custom thumbnail has been updated!")
    await message.reply(text, reply_markup=markup)
