import os
import asyncio
import time
from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..svcs.user_svc import add_user_if_new
from ..core.cfg import cfg
from ..core.log import log
from ..utils.display_progress import progress_for_pyrogram, humanbytes
from ..utils.encoding import get_duration

@Client.on_message(filters.command(['sample', 'preview']))
async def sample_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
    
    if not message.reply_to_message:
        await message.reply(
            "▸ <b>Sample</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>Reply to a video with this command to generate a preview sample.</blockquote>"
        )
        return
    
    reply = message.reply_to_message
    
    if not (reply.video or (reply.document and reply.document.mime_type and reply.document.mime_type.startswith('video/'))):
        await message.reply(
            "▸ <b>Sample</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>The replied message is not a video.</blockquote>"
        )
        return
    
    await add_user_if_new(app, message)
    
    duration = 30
    if len(message.command) > 1:
        try:
            duration = min(int(message.command[1]), 120)
        except:
            pass
    
    msg = await message.reply("▸ <b>Sample</b>\nStatus: ● Downloading video...")
    
    try:
        start_time = time.time()
        filepath = await reply.download(
            file_name=cfg.DOWNLOAD_DIR,
            progress=progress_for_pyrogram,
            progress_args=("▸ <b>Sample</b>\nStatus: ● Downloading...", msg, start_time)
        )
        
        if not filepath:
            await msg.edit("▸ <b>Sample</b>\nStatus: ✗ Download Failed")
            return
        
        await msg.edit("▸ <b>Sample</b>\nStatus: ● Generating preview...")
        
        video_duration = get_duration(filepath)
        if video_duration <= duration:
            start_time_sec = 0
            duration = video_duration
        else:
            start_time_sec = int(video_duration * 0.1)
        
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        output_path = os.path.join(cfg.ENCODE_DIR, f"sample_{name}{ext}")
        
        cmd = [
            'ffmpeg', '-y', '-ss', str(start_time_sec),
            '-i', filepath, '-t', str(duration),
            '-c', 'copy', '-avoid_negative_ts', '1',
            output_path
        ]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        
        if proc.returncode != 0 or not os.path.exists(output_path):
            await msg.edit("▸ <b>Sample</b>\nStatus: ✗ Failed to generate sample")
            return
        
        await msg.edit("▸ <b>Sample</b>\nStatus: ● Uploading preview...")
        
        sample_size = os.path.getsize(output_path)
        await reply.reply_video(
            output_path,
            caption=f"▸ <b>Sample Preview</b>\nDuration: {duration}s | Size: {humanbytes(sample_size)}",
            supports_streaming=True
        )
        
        await msg.delete()
        
    except Exception as e:
        log.err("sample_error", error=str(e))
        await msg.edit(f"▸ <b>Sample</b>\nStatus: ✗ Error\n{str(e)[:100]}")
    finally:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)
