from pyrogram import Client
from pyrogram.types import CallbackQuery, ForceReply
from .. import app
from ..svcs.settings_svc import settings_svc
from ..svcs.queue_svc import queue_svc
from ..core.log import log

@Client.on_callback_query()
async def main_callback_handler(bot: Client, cb: CallbackQuery):
    u_id = cb.from_user.id
    data = cb.data
    
    log.inf("callback", u_id=u_id, data=data)

    if data == "closeMeh":
        await cb.message.delete()
        return

    if data == "cancel_task":
        await queue_svc.cancel_current_task()
        await cb.answer("Task Cancelled", show_alert=True)
        return

    if data == "toggle_mode":
        from ..db.status import status_db
        current = await status_db.get_public_mode()
        await status_db.set_public_mode(not current)
        from .mode import mode_handler
        await cb.answer(f"Mode set to {'Private' if current else 'Public'}", show_alert=True)
        await mode_handler(bot, cb.message)
        return

    if data == "close_mode":
        await cb.message.delete()
        return

    if data == "help_cmd":
        from .start import help_handler
        await help_handler(bot, cb.message)
        await cb.answer()
        return

    if data == "stats_cb":
        from .start import stats_handler
        await stats_handler(bot, cb.message)
        await cb.answer()
        return

    if data == "OpenSettings":
        text, markup = await settings_svc.get_main_menu()
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "VideoSettings":
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "AudioSettings":
        text, markup = await settings_svc.get_audio_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "ExtraSettings":
        text, markup = await settings_svc.get_extra_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "ThumbSettings":
        text, markup = await settings_svc.get_thumb_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "triggerHevc":
        await settings_svc.toggle(u_id, 'hevc')
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "triggerBits":
        await settings_svc.toggle(u_id, 'bits')
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "triggertune":
        await settings_svc.toggle(u_id, 'tune')
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "triggerPreset":
        await settings_svc.toggle(u_id, 'preset', options=['uf', 'sf', 'vf', 'f', 'm', 's'])
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "triggerWatermark":
        await settings_svc.toggle(u_id, 'watermark')
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "triggerHardsub":
        await settings_svc.toggle(u_id, 'hardsub')
        text, markup = await settings_svc.get_extra_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "triggerSubtitles":
        await settings_svc.toggle(u_id, 'subtitles')
        text, markup = await settings_svc.get_extra_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "triggerUploadMode":
        await settings_svc.toggle(u_id, 'upload_as_doc')
        text, markup = await settings_svc.get_extra_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "setRename":
        await cb.message.reply_text(
            "▸ <b>Rename Policy</b>\n"
            "Reply to this message with your new filename template.\n"
            "Use <code>{filename}</code> for the original name.\n\n"
            "Example: <code>[HEVC] {filename}</code>",
            reply_markup=ForceReply(selective=True)
        )
        await cb.answer()

    elif data == "setWatermark":
        await cb.message.reply_text(
            "▸ <b>Watermark Text</b>\n"
            "Reply to this message with your target watermark text.",
            reply_markup=ForceReply(selective=True)
        )
        await cb.answer()

    elif data == "triggerextensions":
        await settings_svc.toggle(u_id, 'extensions', options=['MKV', 'MP4', 'AVI'])
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "triggerResolution":
        await settings_svc.toggle(u_id, 'resolution', options=['OG', '1080', '720', '480', '576'])
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "triggerCRF":
        await settings_svc.update_crf(u_id)
        text, markup = await settings_svc.get_video_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "triggerAudioCodec":
        await settings_svc.toggle(u_id, 'audio', options=['aac', 'ac3', 'opus', 'copy'])
        text, markup = await settings_svc.get_audio_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "triggerbitrate":
        await settings_svc.toggle(u_id, 'bitrate', options=['source', '320', '256', '192', '128'])
        text, markup = await settings_svc.get_audio_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "triggerAudioChannels":
        await settings_svc.toggle(u_id, 'channels', options=['source', '2.0', '5.1'])
        text, markup = await settings_svc.get_audio_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)

    elif data == "delThumb":
        from ..db.users import users_db
        await users_db.update_user(u_id, {'custom_thumbnail': None})
        text, markup = await settings_svc.get_thumb_settings(u_id)
        await cb.message.edit(text, reply_markup=markup)
        await cb.answer("Custom thumbnail deleted.", show_alert=True)

    elif data == "wm_toggle":
        await settings_svc.toggle(u_id, 'watermark')
        from .watermark import get_watermark_panel
        from ..db.users import users_db
        user = await users_db.get_user(u_id)
        text, markup = get_watermark_panel(user)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "wm_type":
        from ..db.users import users_db
        user = await users_db.get_user(u_id)
        current = user.get('watermark_type', 'text')
        new_type = 'image' if current == 'text' else 'text'
        await users_db.update_user(u_id, {'watermark_type': new_type})
        user = await users_db.get_user(u_id)
        from .watermark import get_watermark_panel
        text, markup = get_watermark_panel(user)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "wm_size":
        from ..db.users import users_db
        user = await users_db.get_user(u_id)
        sizes = ['small', 'medium', 'large']
        current = user.get('watermark_size', 'medium')
        idx = sizes.index(current) if current in sizes else 1
        new_size = sizes[(idx + 1) % len(sizes)]
        await users_db.update_user(u_id, {'watermark_size': new_size})
        user = await users_db.get_user(u_id)
        from .watermark import get_watermark_panel
        text, markup = get_watermark_panel(user)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "wm_position":
        from ..db.users import users_db
        from .watermark import get_position_grid
        user = await users_db.get_user(u_id)
        current_pos = user.get('watermark_position', 'br')
        markup = get_position_grid(current_pos)
        await cb.message.edit(
            "▸ <b>Watermark Position</b>\n\n"
            "Select where to place your watermark:",
            reply_markup=markup
        )
        
    elif data.startswith("wm_pos_"):
        pos = data.replace("wm_pos_", "")
        from ..db.users import users_db
        await users_db.update_user(u_id, {'watermark_position': pos})
        user = await users_db.get_user(u_id)
        from .watermark import get_watermark_panel
        text, markup = get_watermark_panel(user)
        await cb.message.edit(text, reply_markup=markup)
        
    elif data == "wm_back":
        from ..db.users import users_db
        from .watermark import get_watermark_panel
        user = await users_db.get_user(u_id)
        text, markup = get_watermark_panel(user)
        await cb.message.edit(text, reply_markup=markup)

    await cb.answer()
