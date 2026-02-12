import asyncio
import math
import time
from ..core.cfg import cfg

async def progress_for_pyrogram(current, total, ud_type, message, start, task_id=None):
    now = time.time()
    diff = now - start
    
    if task_id:
        from ..svcs.task_manager import task_manager
        task = task_manager.get_task(task_id)
        if task:
            if task.get("cancelled"):
                 raise asyncio.CancelledError("User cancelled task")
            if task.get("downloader") and task["downloader"].cancelled:
                raise asyncio.CancelledError("User cancelled task")

    if not round(diff % 5.00) or current == total:
        percentage = min(current * 100 / total, 100.0)
        speed = current / diff if diff > 0 else 0
        eta_sec = round((total - current) / speed) if speed > 0 else 0
        
        progress_bar = "".join(["█" for _ in range(int(percentage/10))]) + "".join(["░" for _ in range(10 - int(percentage/10))])
        
        cancel_text = f"\n<code>/cancel {task_id}</code> to stop" if task_id else ""
        
        text = (
            f"{ud_type}\n"
            f"Progress: [{progress_bar}] {round(percentage, 1)}%\n"
            f"Size: {humanbytes(current)} / {humanbytes(total)}\n"
            f"Speed: {humanbytes(speed)}/s | ETA: {TimeFormatter(eta_sec)}"
            f"{cancel_text}"
        )
        
        try:
            await message.edit(text)
        except:
            pass

async def progress_for_url(downloader, msg):
    total = downloader.filesize if downloader.filesize else 0
    current = downloader.get_dl_size()
    percentage = downloader.get_progress() * 100
    speed = downloader.get_speed()
    eta = downloader.get_eta()
    
    progress_bar = "".join(["█" for _ in range(int(percentage/10))]) + "".join(["░" for _ in range(10 - int(percentage/10))])
    
    text = (
        f"▸ <b>Downloader</b>\n"
        f"Status: ● Downloading...\n"
        f"Progress: [{progress_bar}] {round(percentage, 1)}%\n"
        f"Size: {humanbytes(current)} / {humanbytes(total)}\n"
        f"Speed: {humanbytes(speed)}/s | ETA: {TimeFormatter(eta)}"
    )
    
    try:
        await msg.edit_text(text)
    except:
        pass
    await asyncio.sleep(5)

def humanbytes(size):
    if not size: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{round(size, 2)} {unit}"
        size /= 1024.0
    return f"{round(size, 2)} PB"

def TimeFormatter(seconds: float) -> str:
    if not seconds or seconds < 0: return "..."
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ""
    if days: tmp += f"{days}d "
    if hours: tmp += f"{hours}h "
    if minutes: tmp += f"{minutes}m "
    if seconds: tmp += f"{seconds}s"
    return tmp.strip() or "0s"
