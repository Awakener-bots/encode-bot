import asyncio
import os

from io import BytesIO, StringIO
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pySmartDL import SmartDL

def memory_file(name=None, contents=None, *, bytes=True):
    if isinstance(contents, str) and bytes:
        contents = contents.encode()
    file = BytesIO() if bytes else StringIO()
    if name:
        file.name = name
    if contents:
        file.write(contents)
        file.seek(0)
    return file

from ..core.cfg import cfg
from ..core.log import log
from ..db.status import status_db
from .display_progress import progress_for_url

start_but = InlineKeyboardMarkup([
    [InlineKeyboardButton("Settings", callback_data="OpenSettings"), InlineKeyboardButton("Help", callback_data="help_cmd")],
    [InlineKeyboardButton("Current Stats", callback_data="stats_cb")]
])

async def check_chat(message, chat):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None
    chat_type = message.chat.type
    
    get_sudo = (await status_db.get_sudo_users()).split()
    get_auth = (await status_db.get_auth_chats()).split()
    
    title = None
    
    if user_id in cfg.OWNER_ID:
        title = 'God'
    elif (user_id and user_id in cfg.SUDO_USERS) or chat_id in cfg.SUDO_USERS:
        title = 'Sudo'
    elif chat_id in cfg.EVERYONE_CHATS or (user_id and user_id in cfg.EVERYONE_CHATS):
        title = 'Auth'
    elif (user_id and str(user_id) in get_sudo) or str(chat_id) in get_sudo:
        title = 'Sudo'
    elif str(chat_id) in get_auth or (user_id and str(user_id) in get_auth):
        title = 'Auth'
        
    if title == 'God':
        return True
        
    if chat == 'Owner':
        return False
        
    if title == 'Sudo':
        return True
    
    if chat_type in ['group', 'supergroup']:
        if chat_id not in cfg.EVERYONE_CHATS and str(chat_id) not in get_auth:
            return False
        
    if chat == 'Both':
        if title == 'Auth':
            return True
        if await status_db.get_public_mode():
            return True
        
    log.wrn("access_denied", u_id=user_id, chat_id=chat_id, required=chat)
    return False


async def handle_url(url, filepath, msg):
    downloader = SmartDL(url, filepath, progress_bar=False)
    downloader.start(blocking=False)
    while not downloader.isFinished():
        await progress_for_url(downloader, msg)


from ..db.users import users_db
from .encoding import encode, extract_subs
from .uploads import upload_worker

async def handle_encode(filepath, message, msg, task_id=None, overrides=None):
    user_id = message.from_user.id if message.from_user else message.chat.id
    user_settings = await users_db.get_user(user_id)
    user_settings = user_settings or {}
    
    if overrides:
        user_settings = {**user_settings, **overrides}
    
    id_str = f" [ID: {task_id}]" if task_id else ""
    
    if user_settings.get('hardsub'):
        subs = await extract_subs(filepath, msg, message.from_user.id)
        if not subs:
            await msg.edit(f"▸ <b>Error</b>{id_str}\nStatus: ✗ Subtitle Extraction Failed")
            return None
            
    res = await encode(filepath, message, msg, task_id, overrides)
    if not res or not res[0]:
        await message.reply(f"▸ <b>Error</b>{id_str}\nStatus: ✗ Encoding Failed")
        return None
        
    new_file, orig_size, new_size = res
    saved = orig_size - new_size
    percent = round((saved / orig_size) * 100, 1) if orig_size > 0 else 0
    
    await users_db.update_user(message.from_user.id, {
        "total_space_saved": user_settings.get("total_space_saved", 0) + saved,
        "encoded_count": user_settings.get("encoded_count", 0) + 1
    })
    
    from .display_progress import humanbytes
    await msg.edit(
        f"▸ <b>Upload</b>{id_str}\n"
        f"Status: ● Uploading...\n"
        f"Saved: {humanbytes(saved)} ({percent}%)"
    )
    
    link = None
    try:
        link = await upload_worker(new_file, message, msg)
        
        await msg.edit(
            f"▸ <b>Complete</b>{id_str}\n"
            f"Status: ● Success\n\n"
            f"💾 <b>Stats:</b>\n"
            f"• Original: {humanbytes(orig_size)}\n"
            f"• Compressed: {humanbytes(new_size)}\n"
            f"• Savings: {humanbytes(saved)} ({percent}%)\n\n"
            f"🔗 <a href='{link}'>Download Link</a>",
            disable_web_page_preview=True
        )
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists(new_file):
            os.remove(new_file)
            
    return link


async def handle_extract(archieve):
    path = os.getcwd()
    archieve = os.path.join(path, archieve)
    cmd = [f'./extract', archieve]
    rio = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await rio.communicate()
    os.remove(archieve)
    return path


async def get_zip_folder(orig_path: str):
    if orig_path.endswith(".tar.bz2"):
        return orig_path.rsplit(".tar.bz2", 1)[0]
    elif orig_path.endswith(".tar.gz"):
        return orig_path.rsplit(".tar.gz", 1)[0]
    elif orig_path.endswith(".bz2"):
        return orig_path.rsplit(".bz2", 1)[0]
    elif orig_path.endswith(".gz"):
        return orig_path.rsplit(".gz", 1)[0]
    elif orig_path.endswith(".tar.xz"):
        return orig_path.rsplit(".tar.xz", 1)[0]
    elif orig_path.endswith(".tar"):
        return orig_path.rsplit(".tar", 1)[0]
    elif orig_path.endswith(".tbz2"):
        return orig_path.rsplit("tbz2", 1)[0]
    elif orig_path.endswith(".tgz"):
        return orig_path.rsplit(".tgz", 1)[0]
    elif orig_path.endswith(".zip"):
        return orig_path.rsplit(".zip", 1)[0]
    elif orig_path.endswith(".7z"):
        return orig_path.rsplit(".7z", 1)[0]
    elif orig_path.endswith(".Z"):
        return orig_path.rsplit(".Z", 1)[0]
    elif orig_path.endswith(".rar"):
        return orig_path.rsplit(".rar", 1)[0]
    elif orig_path.endswith(".iso"):
        return orig_path.rsplit(".iso", 1)[0]
    elif orig_path.endswith(".wim"):
        return orig_path.rsplit(".wim", 1)[0]
    elif orig_path.endswith(".cab"):
        return orig_path.rsplit(".cab", 1)[0]
    elif orig_path.endswith(".apm"):
        return orig_path.rsplit(".apm", 1)[0]
    elif orig_path.endswith(".arj"):
        return orig_path.rsplit(".arj", 1)[0]
    elif orig_path.endswith(".chm"):
        return orig_path.rsplit(".chm", 1)[0]
    elif orig_path.endswith(".cpio"):
        return orig_path.rsplit(".cpio", 1)[0]
    elif orig_path.endswith(".cramfs"):
        return orig_path.rsplit(".cramfs", 1)[0]
    elif orig_path.endswith(".deb"):
        return orig_path.rsplit(".deb", 1)[0]
    elif orig_path.endswith(".dmg"):
        return orig_path.rsplit(".dmg", 1)[0]
    elif orig_path.endswith(".fat"):
        return orig_path.rsplit(".fat", 1)[0]
    elif orig_path.endswith(".hfs"):
        return orig_path.rsplit(".hfs", 1)[0]
    elif orig_path.endswith(".lzh"):
        return orig_path.rsplit(".lzh", 1)[0]
    elif orig_path.endswith(".lzma"):
        return orig_path.rsplit(".lzma", 1)[0]
    elif orig_path.endswith(".lzma2"):
        return orig_path.rsplit(".lzma2", 1)[0]
    elif orig_path.endswith(".mbr"):
        return orig_path.rsplit(".mbr", 1)[0]
    elif orig_path.endswith(".msi"):
        return orig_path.rsplit(".msi", 1)[0]
    elif orig_path.endswith(".mslz"):
        return orig_path.rsplit(".mslz", 1)[0]
    elif orig_path.endswith(".nsis"):
        return orig_path.rsplit(".nsis", 1)[0]
    elif orig_path.endswith(".ntfs"):
        return orig_path.rsplit(".ntfs", 1)[0]
    elif orig_path.endswith(".rpm"):
        return orig_path.rsplit(".rpm", 1)[0]
    elif orig_path.endswith(".squashfs"):
        return orig_path.rsplit(".squashfs", 1)[0]
    elif orig_path.endswith(".udf"):
        return orig_path.rsplit(".udf", 1)[0]
    elif orig_path.endswith(".vhd"):
        return orig_path.rsplit(".vhd", 1)[0]
    elif orig_path.endswith(".xar"):
        return orig_path.rsplit(".xar", 1)[0]
    else:
        raise IndexError("File format not supported for extraction!")

def get_id(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id if message.reply_to_message.from_user else message.reply_to_message.chat.id
    elif len(message.command) > 1:
        return message.text.split(None, 1)[1].strip()
    return message.chat.id
