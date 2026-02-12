import asyncio
import json
import math
import os
import re
import subprocess
import time
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import ffmpeg

from ..core.cfg import cfg
from ..core.log import log
from ..db.users import users_db
from ..svcs.task_manager import task_manager
from .display_progress import TimeFormatter

def get_codec(filepath, channel='v:0'):
    try:
        output = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', channel,
                                          '-show_entries', 'stream=codec_name,codec_tag_string', '-of',
                                          'default=nokey=1:noprint_wrappers=1', filepath])
        return output.decode('utf-8').split()
    except Exception as e:
        log.err("codec_check", error=str(e), file=filepath)
        return []

async def extract_subs(filepath, msg, u_id):
    path, _ = os.path.splitext(filepath)
    check = get_codec(filepath, channel='s:0')
    if not check or check[0] == 'pgs':
        return None
        
    output = os.path.join(cfg.ENCODE_DIR, f"{msg.id}.ass")
    try:
        subprocess.call(['ffmpeg', '-y', '-i', filepath, '-map', 's:0', output])
        return output
    except Exception as e:
        log.err("sub_extract", error=str(e), file=filepath)
        return None

async def encode(filepath, message, msg, task_id=None, overrides=None):
    from ..svcs.queue_svc import queue_svc
    
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        log.err("encode_input_invalid", file=filepath)
        return None, 0, 0
    
    u_id = message.from_user.id if message.from_user else message.chat.id
    user_settings = await users_db.get_user(u_id)
    user_settings = user_settings or {}
    
    if overrides:
        user_settings = {**user_settings, **overrides}
        
    ex = user_settings.get('extensions', 'MKV')
    path, _ = os.path.splitext(filepath)
    orig_name = os.path.basename(path)
    
    template = user_settings.get('rename_template', '{filename}')
    new_name = template.replace('{filename}', orig_name)
    
    ext_map = {'MP4': '.mp4', 'AVI': '.avi', 'MKV': '.mkv'}
    output_filepath = os.path.join(cfg.ENCODE_DIR, new_name + ext_map.get(ex, '.mkv'))
    
    subtitles_path = os.path.join(cfg.ENCODE_DIR, f"{msg.id}.ass")
    progress_file = os.path.join(cfg.DOWNLOAD_DIR, f"progress_{msg.id}.txt")
    
    if os.path.exists(output_filepath):
        os.remove(output_filepath)

    async def run_ffmpeg(current_cmd, is_fallback=False):
        if os.path.exists(output_filepath):
            os.remove(output_filepath)
        if os.path.exists(progress_file):
            os.remove(progress_file)
            
        proc = await asyncio.create_subprocess_exec(*current_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        log.inf("ffmpeg_start", pid=proc.pid, file=orig_name, task_id=task_id, fallback=is_fallback)
        
        if task_id:
            task_manager.register_encode(task_id, proc, message, output_filepath)
        queue_svc.set_current_proc(proc, output_filepath)
        
        progress_task = asyncio.create_task(_handle_progress(proc, msg, message, filepath, progress_file, task_id))
        
        try:
            stdout, stderr = await proc.communicate()
        finally:
            progress_task.cancel()
            
        if os.path.exists(progress_file):
            os.remove(progress_file)
            
        return proc.returncode, stderr

    hw_encoder = await _detect_hw_encoder(user_settings.get('hevc', False))
    base_cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-progress', progress_file, '-y']
    
    if hw_encoder:
        base_cmd.extend(['-hwaccel', 'auto'])
    
    base_cmd.extend(['-i', filepath])
    
    v_codec_params = []
    selected_v_codec = hw_encoder if hw_encoder else ('libx265' if user_settings.get('hevc') else 'libx264')
    v_codec_params.extend(['-c:v', selected_v_codec])
    
    if hw_encoder:
        log.inf("using_hw_encoder", encoder=hw_encoder)
        
    if user_settings.get('bits'):
        v_codec_params.extend(['-pix_fmt', 'yuv420p10le'])
    else:
        v_codec_params.extend(['-pix_fmt', 'yuv420p'])
        
    crf = user_settings.get('crf', 22)
    
    res = user_settings.get('resolution', 'OG')
    if res != 'OG':
        if crf < 24:
            crf = 24
            
    if 'nvenc' in selected_v_codec:
        v_codec_params.extend(['-rc', 'vbr', '-cq', str(crf), '-qmin', str(crf), '-qmax', str(crf), '-b:v', '0'])
    elif 'qsv' in selected_v_codec:
        v_codec_params.extend(['-global_quality', str(crf)])
    else:
        v_codec_params.extend(['-crf', str(crf)])
    
    presets = {
        'uf': 'ultrafast', 'sf': 'superfast', 'vf': 'veryfast',
        'f': 'fast', 'm': 'medium', 's': 'slow'
    }
    
    chosen_preset = presets.get(user_settings.get('preset'), 'veryfast')
    codec_preset = _get_preset_for_codec(selected_v_codec, chosen_preset)
    v_codec_params.extend(['-preset', codec_preset])
    
    filters = []
    res = user_settings.get('resolution', 'OG')
    res_map = {'1080': '1920:1080', '720': '1280:720', '480': '852:480', '576': '768:576'}
    if res in res_map:
        filters.append(f"scale={res_map[res]}")
        
    if user_settings.get('watermark'):
        wm_type = user_settings.get('watermark_type', 'text')
        wm_position = user_settings.get('watermark_position', 'br')
        if wm_type == 'text':
            watermark_path = await _create_watermark(user_settings.get('watermark_text', '@VideoEncoder'), msg.id, wm_position)
            filters.append(f"subtitles='{watermark_path}'")
        elif wm_type == 'image' and user_settings.get('watermark_image'):
            wm_filter = await _get_image_watermark_filter(user_settings.get('watermark_image'), wm_position, user_settings.get('watermark_size', 'medium'), msg.id)
            if wm_filter:
                base_cmd.extend(wm_filter['input'])
                filters.append(wm_filter['filter'])
        
    if user_settings.get('hardsub') and os.path.exists(subtitles_path):
        filters.append(f"subtitles='{subtitles_path}'")
        
    if filters:
        v_codec_params.extend(['-vf', ','.join(filters)])
        
    a_codec_params = []
    a_codec = user_settings.get('audio', 'aac')
    if a_codec == 'copy':
        a_codec_params.extend(['-c:a', 'copy'])
    else:
        ac_map = {'aac': 'aac', 'ac3': 'ac3', 'opus': 'libopus', 'vorbis': 'libvorbis'}
        a_codec_params.extend(['-c:a', ac_map.get(a_codec, 'aac')])
        channels = user_settings.get('channels', 'source')
        if channels != 'source':
            a_codec_params.extend(['-ac', channels.split('.')[0]])
        bitrate = user_settings.get('bitrate', 'source')
        if bitrate != 'source':
            a_codec_params.extend(['-b:a', f"{bitrate}k"])
            
    final_params = ['-map', '0:v?', '-map', '0:a?', '-map_metadata', '0', '-threads', '0', output_filepath]
    
    full_cmd = base_cmd + v_codec_params + a_codec_params + final_params
    
    returncode, stderr = await run_ffmpeg(full_cmd)
    
    if task_id:
        task = task_manager.get_task(task_id)
        if not task or task.get("cancelled"):
            return None, 0, 0
        
    if returncode != 0:
        log.wrn("encode_fail_attempting_fallback", error=stderr.decode().strip() if stderr else "Unknown", file=orig_name)
        
        sw_codec = 'libx265' if user_settings.get('hevc') else 'libx264'
        
        fallback_v_params = ['-c:v', sw_codec]
        
        if user_settings.get('bits'):
            fallback_v_params.extend(['-pix_fmt', 'yuv420p10le'])
        else:
            fallback_v_params.extend(['-pix_fmt', 'yuv420p'])
            
        fallback_v_params.extend(['-crf', str(user_settings.get('crf', 22))])
        fallback_v_params.extend(['-preset', _get_preset_for_codec(sw_codec, chosen_preset)])
        
        if filters:
            fallback_v_params.extend(['-vf', ','.join(filters)])
            
        clean_base_cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-progress', progress_file, '-y', '-i', filepath]
        
        full_cmd = clean_base_cmd + fallback_v_params + a_codec_params + final_params
        returncode, stderr = await run_ffmpeg(full_cmd, is_fallback=True)

    if task_id:
        task = task_manager.get_task(task_id)
        if not task or task.get("cancelled"):
            return None, 0, 0
        
    if returncode != 0:
        err_msg = stderr.decode().strip() if stderr else "Process interrupted"
        log.err("ffmpeg_fail", code=returncode, error=err_msg, file=orig_name)
        if os.path.exists(output_filepath):
            os.remove(output_filepath)
        return None, 0, 0

    if os.path.exists(output_filepath) and os.path.getsize(output_filepath) > 0:
        orig_size = os.path.getsize(filepath)
        new_size = os.path.getsize(output_filepath)
        return output_filepath, orig_size, new_size
        
    log.err("encode_output_empty", file=orig_name)
    if os.path.exists(output_filepath):
        os.remove(output_filepath)
    return None, 0, 0

_HW_CACHE = {}

async def _detect_hw_encoder(hevc=False):
    cache_key = f"hevc_{hevc}"
    if cache_key in _HW_CACHE:
        return _HW_CACHE[cache_key]
        
    encoders_to_try = [
        ('hevc_nvenc' if hevc else 'h264_nvenc'),
        ('hevc_qsv' if hevc else 'h264_qsv'),
        ('hevc_amf' if hevc else 'h264_amf')
    ]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            'ffmpeg', '-hide_banner', '-encoders',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        available_in_ffmpeg = stdout.decode()
    except:
        return None

    for encoder in encoders_to_try:
        if encoder in available_in_ffmpeg:
            try:
                test_cmd = [
                    'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=64x64:d=0.1', 
                    '-c:v', encoder, '-frames:v', '1', '-f', 'null', '-'
                ]
                test_proc = await asyncio.create_subprocess_exec(
                    *test_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                _, stderr = await test_proc.communicate()
                
                if test_proc.returncode == 0:
                    _HW_CACHE[cache_key] = encoder
                    return encoder
                else:
                    err_hint = stderr.decode().strip().split('\n')[0][:100]
                    log.wrn("hw_init_fail", encoder=encoder, error=err_hint)
            except:
                pass
    
    _HW_CACHE[cache_key] = None
    return None

def _get_preset_for_codec(codec, preset):
    if codec in ['libx264', 'libx265']:
        return preset
        
    if 'nvenc' in codec:
        nv_map = {
            'ultrafast': 'p1',
            'superfast': 'p1',
            'veryfast': 'p2',
            'fast': 'p3',
            'medium': 'p4',
            'slow': 'p6',
            'slower': 'p7'
        }
        return nv_map.get(preset, 'p4')
        
    if 'qsv' in codec:
         qsv_map = {
            'ultrafast': 'veryfast',
            'superfast': 'veryfast',
            'veryfast': 'veryfast',
            'fast': 'fast',
            'medium': 'medium',
            'slow': 'slow',
            'slower': 'veryslow'
        }
         return qsv_map.get(preset, 'medium')
         
    if 'amf' in codec:
        return 'speed' if preset in ['ultrafast', 'superfast', 'veryfast'] else 'quality'

    return preset

async def _create_watermark(text, msg_id, position='br'):
    path = os.path.join(cfg.ENCODE_DIR, f"wm_{msg_id}.ass")
    
    alignment_map = {
        'tl': 7, 'tc': 8, 'tr': 9,
        'ml': 4, 'mc': 5, 'mr': 6,
        'bl': 1, 'bc': 2, 'br': 3
    }
    alignment = alignment_map.get(position, 3)
    
    content = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default, Arial, 28, &H88FFFFFF, 1, 1, 2, 1, {alignment}, 20, 20, 20, 1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        f"Dialogue: 0,0:00:00.00,9:59:59.99,Default,,0,0,0,,{text}"
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

async def _get_image_watermark_filter(file_id, position, size, msg_id):
    from .. import app
    
    wm_path = os.path.join(cfg.ENCODE_DIR, f"wm_img_{msg_id}.png")
    
    try:
        await app.download_media(file_id, file_name=wm_path)
    except Exception as e:
        log.err("watermark_download", error=str(e))
        return None
    
    if not os.path.exists(wm_path):
        return None
    
    size_map = {
        'small': 'iw/8',
        'medium': 'iw/5',
        'large': 'iw/3'
    }
    scale = size_map.get(size, 'iw/5')
    
    position_map = {
        'tl': '20:20',
        'tc': '(main_w-overlay_w)/2:20',
        'tr': 'main_w-overlay_w-20:20',
        'ml': '20:(main_h-overlay_h)/2',
        'mc': '(main_w-overlay_w)/2:(main_h-overlay_h)/2',
        'mr': 'main_w-overlay_w-20:(main_h-overlay_h)/2',
        'bl': '20:main_h-overlay_h-20',
        'bc': '(main_w-overlay_w)/2:main_h-overlay_h-20',
        'br': 'main_w-overlay_w-20:main_h-overlay_h-20'
    }
    pos = position_map.get(position, position_map['br'])
    
    filter_str = f"[1:v]scale={scale}:-1,format=rgba,colorchannelmixer=aa=0.7[wm];[0:v][wm]overlay={pos}"
    
    return {
        'input': ['-i', wm_path],
        'filter': filter_str
    }

async def _handle_progress(proc, msg, message, filepath, progress_file, task_id=None):
    start_time = time.time()
    total_time, _ = await _media_info(filepath)
    id_str = f" [ID: {task_id}]" if task_id else ""
    cancel_str = f"\n<code>/cancel {task_id}</code> to stop" if task_id else ""
    
    while proc.returncode is None:
        if task_id:
            task = task_manager.get_task(task_id)
            if not task or task.get("cancelled"):
                break
                
        await asyncio.sleep(5)
        if not os.path.exists(progress_file):
            continue
            
        try:
            with open(progress_file, 'r') as f:
                content = f.read()
                time_match = re.search(r"out_time_ms=(\d+)", content)
                speed_match = re.search(r"speed=(\d+\.?\d*)", content)
                
                if time_match and speed_match and total_time:
                    elapsed = int(time_match.group(1)) / 1000000
                    speed = float(speed_match.group(1)) or 1.0
                    percent = min(round((elapsed / total_time) * 100, 1), 100.0)
                    
                    eta_sec = (total_time - elapsed) / speed
                    eta = TimeFormatter(eta_sec) if eta_sec > 0 else "N/A"
                    
                    progress_bar = "".join(["█" for _ in range(int(percent/10))]) + "".join(["░" for _ in range(10 - int(percent/10))])
                    
                    text = (
                        f"▸ <b>Encoder</b>{id_str}\n"
                        f"Status: ● Encoding {percent}%\n"
                        f"Progress: [{progress_bar}]\n"
                        f"Speed: {speed}x | ETA: {eta}{cancel_str}"
                    )
                    
                    try:
                        await msg.edit(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel Encoding", callback_data="cancel_task")]]))
                    except:
                        pass
        except:
            pass
            
async def _media_info(filepath):
    try:
        result = subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration,bit_rate', 
            '-of', 'default=noprint_wrappers=1:nokey=1', filepath
        ]).decode().split()
        return float(result[0]) if result else 0, result[1] if len(result) > 1 else None
    except:
        return 0, None

def get_duration(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata and metadata.has("duration"):
        return metadata.get('duration').seconds
    else:
        return 0

def get_width_height(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata and metadata.has("width") and metadata.has("height"):
        return metadata.get("width"), metadata.get("height")
    else:
        return (1280, 720)

def get_thumbnail(in_filename, path, ttl):
    out_filename = os.path.join(path, str(time.time()) + ".jpg")
    try:
        (
            ffmpeg
            .input(in_filename, ss=ttl)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return out_filename
    except Exception as e:
        log.wrn("thumb_fail", error=str(e))
        return None
