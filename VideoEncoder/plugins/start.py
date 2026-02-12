import os
import shutil
import time
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message
from ..core.cfg import cfg
from ..core.log import log
from ..db.users import users_db
from ..utils.display_progress import TimeFormatter, humanbytes
from ..utils.helper import check_chat, start_but
from ..svcs.user_svc import add_user_if_new
from ..svcs.settings_svc import settings_svc

def get_uptime():
    return TimeFormatter(time.time() - cfg.BOT_START_TIME)

@Client.on_message(filters.command('start'))
async def start_handler(app, message):
    await add_user_if_new(app, message)
    
    if len(message.command) > 1:
        deep_link = message.command[1].lower()
        u_id = message.from_user.id
        
        if deep_link == "settings":
            text, markup = await settings_svc.get_main_menu()
            await message.reply(text, reply_markup=markup)
            return
            
        elif deep_link == "watermark":
            from .watermark import get_watermark_panel
            user = await users_db.get_user(u_id)
            if not user:
                await users_db.add_user(u_id)
                user = await users_db.get_user(u_id)
            text, markup = get_watermark_panel(user)
            await message.reply(text, reply_markup=markup)
            return
            
        elif deep_link == "vset":
            text = await settings_svc.get_settings_summary(u_id)
            await message.reply(text)
            return
            
        elif deep_link == "reset":
            await users_db.delete_user(u_id)
            await users_db.add_user(u_id)
            await message.reply("▸ <b>Settings</b>\nStatus: ● Reset\nYour settings have been reset to default.")
            return
    photo_l = "https://i.ibb.co/0ypGsshD/photo-2026-01-21-13-58-58-7597814210529067032.jpg"
    mention = message.from_user.mention() if message.from_user else "User"
    text = (
        f"<b>VideoEncoder Bot</b>\n"
        f"Status: Online\n\n"
        f"<blockquote>"
        f"Hi {mention}, I help you compress and encode videos with custom settings.\n"
        f"Send me any video to get started."
        f"</blockquote>\n\n"
        f"‣ ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : <a href='https://t.me/Awakeners_Bots'>Awakeners Bots</a>"
    )
    await message.reply_photo(photo=photo_l, caption=text, reply_markup=start_but)

@Client.on_message(filters.command('help'))
async def help_handler(app, message):
    
    msg = (
        "▸ <b>Commands Directory</b>\n\n"
        "<blockquote>"
        "<b>Encoding (Group Only):</b>\n"
        "<code>/enc</code> - Encode with your settings\n"
        "<code>/480p [name]</code> - Quick 480p encode\n"
        "<code>/720p [name]</code> - Quick 720p encode\n"
        "<code>/1080p [name]</code> - Quick 1080p encode\n"
        "<code>/ddl [url] | [name]</code> - Download & encode\n"
        "<code>/batch [url]</code> - Batch process archive\n"
        "<code>/queue</code> - View task pipeline\n"
        "<code>/cancel [id]</code> - Cancel running task\n\n"
        "<b>Video Tools (Group Only):</b>\n"
        "<code>/sample [sec]</code> - Preview clip (30-120s)\n"
        "<code>/ss [count]</code> - Screenshots (1-10)\n"
        "<code>/trim [start] [end]</code> - Cut video\n"
        "<code>/audio [mp3/aac/opus]</code> - Extract audio\n\n"
        "<b>Settings (DM Only):</b>\n"
        "<code>/settings</code> - Control Panel\n"
        "<code>/watermark</code> - Watermark config\n"
        "<code>/vset</code> - View your profile\n"
        "<code>/reset</code> - Factory defaults\n\n"
        "<b>Admin Commands:</b>\n"
        "<code>/mode</code> - Public/Private toggle\n"
        "<code>/stats</code> - System info\n"
        "<code>/addsudo [id]</code> - Add sudo user\n"
        "<code>/rmsudo [id]</code> - Remove sudo\n"
        "<code>/addchat [id]</code> - Authorize chat\n"
        "<code>/rmchat [id]</code> - Remove chat\n"
        "<code>/logs</code> - View logs\n"
        "<code>/restart</code> - Reboot bot\n"
        "<code>/clean</code> - Purge temp files\n\n"
        "<b>Usage Examples:</b>\n"
        "<code>/480p [HEVC]</code> - Encode to 480p with prefix\n"
        "<code>/trim 1:30 5:00</code> - Cut from 1:30 to 5:00\n"
        "<code>/ss 5</code> - Take 5 screenshots\n"
        "<code>/audio aac</code> - Extract as AAC"
        "</blockquote>"
    )
    await message.reply(text=msg, reply_markup=start_but)

@Client.on_message(filters.command('stats'))
async def stats_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
        
    u_id = message.from_user.id
    user = await users_db.get_user(u_id)
    
    uptime = get_uptime()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    saved = user.get('total_space_saved', 0)
    count = user.get('encoded_count', 0)
    
    text = (
        f"▸ <b>System Stats</b>\n"
        f"Status: ● Healthy\n\n"
        f"• Uptime: {uptime}\n"
        f"• CPU Use: {cpu}%\n"
        f"• RAM Use: {ram}%\n"
        f"• Disk Use: {disk}%\n\n"
        f"▸ <b>Your Analytics</b>\n"
        f"• Total Encodes: {count}\n"
        f"• Total Space Saved: {humanbytes(saved)}"
    )
    await message.reply(text)

@Client.on_message(filters.command('restart'))
async def restart_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    await message.reply("▸ <b>System</b>\nStatus: ● Restarting...\nBot will be back in a few seconds.")
    log.inf("bot_restart", u_id=message.from_user.id if message.from_user else "system")
    
    import sys
    os.execl(sys.executable, sys.executable, "-m", "VideoEncoder")

@Client.on_message(filters.command('clean'))
async def clean_handler(app, message):
    if not await check_chat(message, chat='Sudo'):
        return
        
    count = 0
    for folder in [cfg.DOWNLOAD_DIR, cfg.ENCODE_DIR]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                path = os.path.join(folder, file)
                try:
                    if os.path.isfile(path) or os.path.islink(path):
                        os.unlink(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                    count += 1
                except:
                    pass
                    
    await message.reply(f"▸ <b>System</b>\nStatus: ● Cleaned\nRemoved {count} temporary files.")
