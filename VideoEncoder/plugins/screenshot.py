import os
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
from ..utils.helper import check_chat
from ..svcs.user_svc import add_user_if_new
from ..core.cfg import cfg
from ..core.log import log
from ..utils.display_progress import progress_for_pyrogram
from ..utils.encoding import get_duration

@Client.on_message(filters.command(['ss', 'screenshot', 'screenshots']))
async def screenshot_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
    
    if not message.reply_to_message:
        await message.reply(
            "▸ <b>Screenshots</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>Reply to a video with this command.\n"
            "Usage: /ss [count]\n"
            "Example: /ss 5</blockquote>"
        )
        return
    
    reply = message.reply_to_message
    
    if not (reply.video or (reply.document and reply.document.mime_type and reply.document.mime_type.startswith('video/'))):
        await message.reply(
            "▸ <b>Screenshots</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>The replied message is not a video.</blockquote>"
        )
        return
    
    await add_user_if_new(app, message)
    
    count = 5
    if len(message.command) > 1:
        try:
            count = min(max(int(message.command[1]), 1), 10)
        except:
            pass
    
    msg = await message.reply(f"▸ <b>Screenshots</b>\nStatus: ● Downloading video...")
    
    screenshots = []
    filepath = None
    
    try:
        start_time = time.time()
        filepath = await reply.download(
            file_name=cfg.DOWNLOAD_DIR,
            progress=progress_for_pyrogram,
            progress_args=("▸ <b>Screenshots</b>\nStatus: ● Downloading...", msg, start_time)
        )
        
        if not filepath:
            await msg.edit("▸ <b>Screenshots</b>\nStatus: ✗ Download Failed")
            return
        
        await msg.edit(f"▸ <b>Screenshots</b>\nStatus: ● Generating {count} screenshots...")
        
        duration = get_duration(filepath)
        if duration <= 0:
            await msg.edit("▸ <b>Screenshots</b>\nStatus: ✗ Could not read video duration")
            return
        
        start_offset = duration * 0.05
        end_offset = duration * 0.95
        interval = (end_offset - start_offset) / (count + 1)
        
        for i in range(1, count + 1):
            timestamp = start_offset + (interval * i)
            output_path = os.path.join(cfg.ENCODE_DIR, f"ss_{message.id}_{i}.jpg")
            
            cmd = [
                'ffmpeg', '-y', '-ss', str(timestamp),
                '-i', filepath, '-frames:v', '1',
                '-q:v', '2', output_path
            ]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                screenshots.append(output_path)
        
        if not screenshots:
            await msg.edit("▸ <b>Screenshots</b>\nStatus: ✗ Failed to generate screenshots")
            return
        
        await msg.edit(f"▸ <b>Screenshots</b>\nStatus: ● Uploading {len(screenshots)} screenshots...")
        
        media_group = [
            InputMediaPhoto(ss, caption=f"Screenshot {i+1}/{len(screenshots)}" if i == 0 else "")
            for i, ss in enumerate(screenshots)
        ]
        
        await reply.reply_media_group(media_group)
        await msg.delete()
        
    except Exception as e:
        log.err("screenshot_error", error=str(e))
        await msg.edit(f"▸ <b>Screenshots</b>\nStatus: ✗ Error\n{str(e)[:100]}")
    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        for ss in screenshots:
            if os.path.exists(ss):
                os.remove(ss)
