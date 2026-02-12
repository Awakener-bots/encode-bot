import os
import time
import html
import asyncio
from ..core.log import log
from ..core.cfg import cfg
from ..utils.helper import handle_encode, handle_extract, get_zip_folder
from ..utils.display_progress import progress_for_pyrogram
from ..utils.direct_link_generator import direct_link_generator
from ..utils.fast_download import FastDownloader
from ..svcs.task_manager import task_manager
from urllib.parse import unquote_plus

async def start_encode_task(message, source_type, overrides=None):
    task_id = task_manager.generate_id()
    overrides = overrides or {}
    
    try:
        msg = await message.reply_text(f"▸ <b>Downloader</b> [ID: {task_id}]\nStatus: ● Processing...")
        
        if source_type == 'tg':
            filepath = await _download_tg(message, msg, task_id)
        elif source_type == 'url':
            filepath = await _download_url(message, msg, task_id, batch=False)
        elif source_type == 'batch':
            filepath = await _download_batch(message, msg, task_id)
        else:
            raise ValueError(f"Unknown source type: {source_type}")

        if not filepath:
            await msg.edit("▸ <b>Error</b>\nStatus: ✗ Failed\nReason: Download cancelled or file not found.")
            return

        await msg.edit(f"▸ <b>Encoder</b> [ID: {task_id}]\nStatus: ● Processing...")
        
        if os.path.isdir(filepath):
            await _handle_batch_list(message, msg, filepath, task_id, overrides)
        else:
            await handle_encode(filepath, message, msg, task_id, overrides)
            
    except asyncio.CancelledError:
        log.wrn("encode_task_cancelled", task_id=task_id)
    except Exception as e:
        log.err("encode_task", error=str(e), source=source_type, task_id=task_id)
        await message.reply(f"▸ <b>Error</b>\nStatus: ✗ Failed\nReason: {str(e)}")
    finally:
        task_manager.remove_task(task_id)

async def _download_tg(message, msg, task_id):
    start_time = time.time()
    
    user_id = message.from_user.id if message.from_user else None
    task_manager.register_download(task_id, None, None, message, user_id)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return await message.download(
                file_name=cfg.DOWNLOAD_DIR,
                progress=progress_for_pyrogram,
                progress_args=(f"▸ <b>Downloader</b> [ID: {task_id}]\nStatus: ● Downloading...", msg, start_time, task_id)
            )
        except asyncio.CancelledError:
            return None
        except TimeoutError:
            if attempt < max_retries - 1:
                await msg.edit(
                    f"▸ <b>Downloader</b> [ID: {task_id}]\n"
                    f"Status: ● Timeout - Retrying ({attempt + 2}/{max_retries})...\n"
                    f"<blockquote>Large file detected. Retrying download...</blockquote>"
                )
                await asyncio.sleep(5)
            else:
                log.err("download_timeout", task_id=task_id, attempts=max_retries)
                await msg.edit(
                    f"▸ <b>Downloader</b> [ID: {task_id}]\n"
                    f"Status: ✗ Failed\n"
                    f"<blockquote>Download timed out after {max_retries} attempts. Try again later.</blockquote>"
                )
                return None
        except Exception as e:
            log.err("download_error", task_id=task_id, error=str(e))
            await msg.edit(
                f"▸ <b>Downloader</b> [ID: {task_id}]\n"
                f"Status: ✗ Failed\n"
                f"<blockquote>Error: {str(e)[:100]}</blockquote>"
            )
            return None

async def _download_url(message, msg, task_id, batch):
    url_data = message.text.split(None, 1)[1].strip()
    url = url_data.split("|")[0].strip()
    
    custom_name = None
    if "|" in url_data and not batch:
        custom_name = url_data.split("|")[1].strip()
        
    custom_name = custom_name or unquote_plus(os.path.basename(url.split('?')[0]))
    direct = direct_link_generator(url)
    if direct:
        url = direct
        
    filepath = os.path.join(cfg.DOWNLOAD_DIR, custom_name)
    
    downloader = FastDownloader()
    user_id = message.from_user.id if message.from_user else None
    task_manager.register_download(task_id, None, downloader, message, user_id)
    
    result = await downloader.download(url, filepath, msg, task_id)
    return result

async def _download_batch(message, msg, task_id):
    if message.reply_to_message:
        filepath = await _download_tg_reply(message.reply_to_message, msg, task_id)
    else:
        filepath = await _download_url(message, msg, task_id, batch=True)
        
    if filepath and os.path.isfile(filepath):
        extract_path = await get_zip_folder(filepath)
        await handle_extract(filepath)
        return extract_path
    return filepath

async def _download_tg_reply(reply_msg, msg, task_id):
    start_time = time.time()
    user_id = reply_msg.from_user.id if reply_msg.from_user else None
    task_manager.register_download(task_id, None, None, reply_msg, user_id)
    
    return await reply_msg.download(
        file_name=cfg.DOWNLOAD_DIR,
        progress=progress_for_pyrogram,
        progress_args=(f"▸ <b>Downloader</b> [ID: {task_id}]\nStatus: ● Downloading...", msg, start_time, task_id)
    )

async def _handle_batch_list(message, msg, path, task_id, overrides=None):
    sent_files = []
    files = sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
    
    for i, filename in enumerate(files, 1):
        f_path = os.path.join(path, filename)
        status_msg = await message.reply(f"▸ <b>Encoder</b> [ID: {task_id}]\nStatus: ● Processing {i}/{len(files)}: {filename}")
        try:
            url = await handle_encode(f_path, message, status_msg, task_id, overrides)
            sent_files.append((filename, url))
        except Exception as e:
            await status_msg.edit(f"▸ <b>Error</b>\nStatus: ✗ Skipped {filename}\nReason: {str(e)}")
            
    text = "▸ <b>Batch Complete</b>\n\n"
    for name, link in sent_files:
        if link:
            text += f"- <a href='{link}'>{html.escape(name)}</a>\n"
        else:
            text += f"- {html.escape(name)} (Upload Failed)\n"
            
    await msg.edit(text, disable_web_page_preview=True)

def _cleanup_temp():
    for root, dirs, files in os.walk(cfg.DOWNLOAD_DIR):
        for f in files:
            try:
                os.remove(os.path.join(root, f))
            except:
                pass
    for root, dirs, files in os.walk(cfg.ENCODE_DIR):
        for f in files:
            try:
                os.remove(os.path.join(root, f))
            except:
                pass
