import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..utils.helper import check_chat
from ..db.users import users_db
from ..core.cfg import cfg

POSITION_LABELS = {
    'tl': '↖️', 'tc': '⬆️', 'tr': '↗️',
    'ml': '⬅️', 'mc': '⏺️', 'mr': '➡️',
    'bl': '↙️', 'bc': '⬇️', 'br': '↘️'
}

SIZE_LABELS = {'small': '🔹', 'medium': '🔷', 'large': '🔶'}

@Client.on_message(filters.command('watermark'))
async def watermark_settings_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
    
    if message.chat.type != "private":
        bot_info = await app.get_me()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Open Settings in DM", url=f"https://t.me/{bot_info.username}?start=watermark")]
        ])
        await message.reply(
            "▸ <b>Watermark</b>\n"
            "Status: ● Private Only\n\n"
            "<blockquote>Settings can only be configured in private chat.\n"
            "Please DM me to manage your watermark preferences.</blockquote>",
            reply_markup=keyboard
        )
        return
    
    u_id = message.from_user.id
    user = await users_db.get_user(u_id)
    
    if not user:
        await users_db.add_user(u_id)
        user = await users_db.get_user(u_id)
    
    text, markup = get_watermark_panel(user)
    await message.reply(text, reply_markup=markup)

def get_watermark_panel(user):
    wm_enabled = "ON" if user.get('watermark', False) else "OFF"
    wm_type = user.get('watermark_type', 'text')
    wm_pos = user.get('watermark_position', 'br')
    wm_size = user.get('watermark_size', 'medium')
    wm_text = user.get('watermark_text', '@VideoEncoder')
    has_image = user.get('watermark_image') is not None
    
    type_label = "Text" if wm_type == 'text' else "Image"
    pos_label = POSITION_LABELS.get(wm_pos, '↘️')
    size_label = wm_size.capitalize()
    
    text = (
        f"▸ <b>Watermark</b>\n"
        f"Status: ● {wm_enabled}\n\n"
        f"<b>Type:</b> {type_label}\n"
        f"<b>Position:</b> {pos_label}\n"
        f"<b>Size:</b> {size_label}\n"
    )
    
    if wm_type == 'text':
        text += f"<b>Text:</b> <code>{wm_text}</code>\n"
    else:
        text += f"<b>Image:</b> {'Saved' if has_image else 'Not Set'}\n"
    
    text += (
        "\n<blockquote>Send a photo to set as image watermark.\n\n"
        "Note: Adding watermark may slightly increase file size.</blockquote>"
    )
    
    wm_status = "✅" if user.get('watermark', False) else "❌"
    keyboard = [
        [InlineKeyboardButton(f"Watermark: {wm_status}", callback_data="wm_toggle")],
        [
            InlineKeyboardButton(f"Type: {type_label}", callback_data="wm_type"),
            InlineKeyboardButton(f"Size: {size_label}", callback_data="wm_size")
        ],
        [InlineKeyboardButton("Position", callback_data="wm_position")],
        [InlineKeyboardButton("Set Text", callback_data="setWatermark")],
        [InlineKeyboardButton("« Back", callback_data="OpenSettings")]
    ]
    
    return text, InlineKeyboardMarkup(keyboard)

def get_position_grid(current_pos):
    positions = [
        ['tl', 'tc', 'tr'],
        ['ml', 'mc', 'mr'],
        ['bl', 'bc', 'br']
    ]
    
    keyboard = []
    for row in positions:
        btn_row = []
        for pos in row:
            label = "✅" if pos == current_pos else POSITION_LABELS[pos]
            btn_row.append(InlineKeyboardButton(label, callback_data=f"wm_pos_{pos}"))
        keyboard.append(btn_row)
    
    keyboard.append([InlineKeyboardButton("« Back", callback_data="wm_back")])
    
    return InlineKeyboardMarkup(keyboard)
