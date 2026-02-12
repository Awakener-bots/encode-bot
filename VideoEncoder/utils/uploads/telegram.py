import os
import time
from ...core.cfg import cfg
from ...core.log import log
from ...db.users import users_db
from ..display_progress import progress_for_pyrogram
from ..encoding import get_duration, get_thumbnail, get_width_height

async def upload_to_tg(new_file, message, msg):
    c_time = time.time()
    filename = os.path.basename(new_file)
    u_id = message.from_user.id
    
    user_settings = await users_db.get_user(u_id)
    custom_thumb = user_settings.get('custom_thumbnail')
    
    if user_settings.get('upload_as_doc'):
        final_thumb = None
        if custom_thumb:
            from ... import app
            final_thumb = await app.download_media(custom_thumb, file_name=os.path.join(cfg.DOWNLOAD_DIR, f"thumb_{u_id}.jpg"))
            
        return await upload_doc(message, msg, c_time, filename, new_file, final_thumb)
    else:
        duration = get_duration(new_file)
        if custom_thumb:
            from ... import app
            final_thumb = await app.download_media(custom_thumb, file_name=os.path.join(cfg.DOWNLOAD_DIR, f"thumb_{u_id}.jpg"))
        else:
            thumb_time = duration / 4 if duration > 0 else 0
            final_thumb = get_thumbnail(new_file, cfg.DOWNLOAD_DIR, thumb_time)
            
        width, height = get_width_height(new_file)
        return await upload_video(message, msg, new_file, filename, c_time, final_thumb, duration, width, height)

async def upload_video(message, msg, new_file, filename, c_time, thumb, duration, width, height):
    from ... import app
    try:
        resp = await message.reply_video(
            new_file,
            supports_streaming=True,
            caption=f"▸ <b>{filename}</b>",
            thumb=thumb,
            duration=duration,
            width=width,
            height=height,
            progress=progress_for_pyrogram,
            progress_args=("▸ <b>Uploader</b>\nStatus: ● Uploading video...", msg, c_time)
        )
        
        if resp and cfg.LOG_CHANNEL:
            await resp.copy(cfg.LOG_CHANNEL)
            
        if thumb and os.path.exists(thumb):
            os.remove(thumb)
            
        return resp.link if resp else None
    except Exception as e:
        log.err("upload_video", error=str(e))
        raise e

async def upload_doc(message, msg, c_time, filename, new_file, thumb=None):
    from ... import app
    try:
        resp = await message.reply_document(
            new_file,
            caption=f"▸ <b>{filename}</b>",
            thumb=thumb,
            progress=progress_for_pyrogram,
            progress_args=("▸ <b>Uploader</b>\nStatus: ● Uploading file...", msg, c_time)
        )
        
        if thumb and os.path.exists(thumb):
            os.remove(thumb)
        
        if resp and cfg.LOG_CHANNEL:
            await resp.copy(cfg.LOG_CHANNEL)
            
        return resp.link if resp else None
    except Exception as e:
        log.err("upload_doc", error=str(e))
        raise e
