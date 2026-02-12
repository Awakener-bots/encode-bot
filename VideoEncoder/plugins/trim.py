import os
import asyncio
import time
import re
from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..svcs.user_svc import add_user_if_new
from ..core.cfg import cfg
from ..core.log import log
from ..utils.display_progress import progress_for_pyrogram, humanbytes
from ..utils.encoding import get_duration

def parse_time(time_str):
    time_str = time_str.strip()
    
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    else:
        return float(time_str)

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

@Client.on_message(filters.command(['trim', 'cut']))
async def trim_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
    
    if not message.reply_to_message:
        await message.reply(
            "▸ <b>Trim Video</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>Reply to a video with this command.\n\n"
            "Usage: /trim [start] [end]\n"
            "Examples:\n"
            "• /trim 00:01:00 00:05:00\n"
            "• /trim 1:30 5:00\n"
            "• /trim 90 300 (seconds)</blockquote>"
        )
        return
    
    reply = message.reply_to_message
    
    if not (reply.video or (reply.document and reply.document.mime_type and reply.document.mime_type.startswith('video/'))):
        await message.reply(
            "▸ <b>Trim Video</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>The replied message is not a video.</blockquote>"
        )
        return
    
    if len(message.command) < 3:
        await message.reply(
            "▸ <b>Trim Video</b>\n"
            "Status: ✗ Invalid Arguments\n\n"
            "<blockquote>Please provide start and end times.\n"
            "Example: /trim 00:01:00 00:05:00</blockquote>"
        )
        return
    
    try:
        start_time = parse_time(message.command[1])
        end_time = parse_time(message.command[2])
    except Exception as e:
        await message.reply(
            "▸ <b>Trim Video</b>\n"
            "Status: ✗ Invalid Time Format\n\n"
            "<blockquote>Use HH:MM:SS, MM:SS, or seconds.\n"
            "Example: /trim 1:30 5:00</blockquote>"
        )
        return
    
    if start_time >= end_time:
        await message.reply(
            "▸ <b>Trim Video</b>\n"
            "Status: ✗ Invalid Range\n\n"
            "<blockquote>Start time must be less than end time.</blockquote>"
        )
        return
    
    duration = end_time - start_time
    
    await add_user_if_new(app, message)
    
    msg = await message.reply(
        f"▸ <b>Trim Video</b>\n"
        f"Status: ● Downloading...\n"
        f"Range: {format_time(start_time)} → {format_time(end_time)}\n"
        f"Duration: {format_time(duration)}"
    )
    
    filepath = None
    output_path = None
    
    try:
        dl_start = time.time()
        filepath = await reply.download(
            file_name=cfg.DOWNLOAD_DIR,
            progress=progress_for_pyrogram,
            progress_args=("▸ <b>Trim</b>\nStatus: ● Downloading...", msg, dl_start)
        )
        
        if not filepath:
            await msg.edit("▸ <b>Trim</b>\nStatus: ✗ Download Failed")
            return
        
        video_duration = get_duration(filepath)
        if end_time > video_duration:
            await msg.edit(
                f"▸ <b>Trim</b>\nStatus: ✗ Invalid Range\n\n"
                f"<blockquote>End time ({format_time(end_time)}) exceeds video duration ({format_time(video_duration)}).</blockquote>"
            )
            return
        
        await msg.edit(
            f"▸ <b>Trim Video</b>\n"
            f"Status: ● Cutting video...\n"
            f"Range: {format_time(start_time)} → {format_time(end_time)}"
        )
        
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        output_path = os.path.join(cfg.ENCODE_DIR, f"trim_{name}{ext}")
        
        cmd = [
            'ffmpeg', '-y', '-ss', str(start_time),
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
            await msg.edit("▸ <b>Trim</b>\nStatus: ● Re-encoding (stream copy failed)...")
            
            cmd = [
                'ffmpeg', '-y', '-ss', str(start_time),
                '-i', filepath, '-t', str(duration),
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                output_path
            ]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            await msg.edit("▸ <b>Trim</b>\nStatus: ✗ Failed to trim video")
            return
        
        await msg.edit("▸ <b>Trim</b>\nStatus: ● Uploading...")
        
        output_size = os.path.getsize(output_path)
        await reply.reply_video(
            output_path,
            caption=(
                f"▸ <b>Trimmed Video</b>\n"
                f"Range: {format_time(start_time)} → {format_time(end_time)}\n"
                f"Duration: {format_time(duration)} | Size: {humanbytes(output_size)}"
            ),
            supports_streaming=True
        )
        
        await msg.delete()
        
    except Exception as e:
        log.err("trim_error", error=str(e))
        await msg.edit(f"▸ <b>Trim</b>\nStatus: ✗ Error\n{str(e)[:100]}")
    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)
