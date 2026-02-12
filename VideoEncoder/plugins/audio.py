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

@Client.on_message(filters.command(['audio', 'mp3', 'extractaudio']))
async def audio_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
    
    if not message.reply_to_message:
        await message.reply(
            "▸ <b>Audio Extract</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>Reply to a video with this command.\n\n"
            "Usage: /audio [format]\n"
            "Formats: mp3 (default), aac, opus, flac</blockquote>"
        )
        return
    
    reply = message.reply_to_message
    
    if not (reply.video or (reply.document and reply.document.mime_type and reply.document.mime_type.startswith('video/'))):
        await message.reply(
            "▸ <b>Audio Extract</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>The replied message is not a video.</blockquote>"
        )
        return
    
    await add_user_if_new(app, message)
    
    audio_format = 'mp3'
    if len(message.command) > 1:
        fmt = message.command[1].lower()
        if fmt in ['mp3', 'aac', 'opus', 'flac', 'm4a']:
            audio_format = fmt
    
    format_map = {
        'mp3': {'codec': 'libmp3lame', 'ext': '.mp3', 'bitrate': '192k'},
        'aac': {'codec': 'aac', 'ext': '.m4a', 'bitrate': '192k'},
        'm4a': {'codec': 'aac', 'ext': '.m4a', 'bitrate': '192k'},
        'opus': {'codec': 'libopus', 'ext': '.opus', 'bitrate': '128k'},
        'flac': {'codec': 'flac', 'ext': '.flac', 'bitrate': None}
    }
    
    fmt_config = format_map.get(audio_format, format_map['mp3'])
    
    msg = await message.reply(f"▸ <b>Audio Extract</b>\nStatus: ● Downloading video...")
    
    filepath = None
    output_path = None
    
    try:
        start_time = time.time()
        filepath = await reply.download(
            file_name=cfg.DOWNLOAD_DIR,
            progress=progress_for_pyrogram,
            progress_args=("▸ <b>Audio</b>\nStatus: ● Downloading...", msg, start_time)
        )
        
        if not filepath:
            await msg.edit("▸ <b>Audio</b>\nStatus: ✗ Download Failed")
            return
        
        await msg.edit(f"▸ <b>Audio Extract</b>\nStatus: ● Extracting {audio_format.upper()}...")
        
        duration = get_duration(filepath)
        
        basename = os.path.basename(filepath)
        name, _ = os.path.splitext(basename)
        output_path = os.path.join(cfg.ENCODE_DIR, f"{name}{fmt_config['ext']}")
        
        cmd = [
            'ffmpeg', '-y', '-i', filepath,
            '-vn',
            '-c:a', fmt_config['codec']
        ]
        
        if fmt_config['bitrate']:
            cmd.extend(['-b:a', fmt_config['bitrate']])
        
        cmd.append(output_path)
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        
        if proc.returncode != 0 or not os.path.exists(output_path):
            await msg.edit("▸ <b>Audio</b>\nStatus: ✗ Failed to extract audio")
            return
        
        await msg.edit("▸ <b>Audio Extract</b>\nStatus: ● Uploading...")
        
        output_size = os.path.getsize(output_path)
        
        dur_min = int(duration // 60)
        dur_sec = int(duration % 60)
        
        await reply.reply_audio(
            output_path,
            caption=(
                f"▸ <b>Extracted Audio</b>\n"
                f"Format: {audio_format.upper()}\n"
                f"Duration: {dur_min}:{dur_sec:02d} | Size: {humanbytes(output_size)}"
            ),
            duration=int(duration),
            title=name
        )
        
        await msg.delete()
        
    except Exception as e:
        log.err("audio_extract_error", error=str(e))
        await msg.edit(f"▸ <b>Audio</b>\nStatus: ✗ Error\n{str(e)[:100]}")
    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)
