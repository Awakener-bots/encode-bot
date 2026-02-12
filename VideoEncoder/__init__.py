import os
from pyrogram import Client
from .core.cfg import cfg
from .core.log import log

for folder in [cfg.DOWNLOAD_DIR, cfg.ENCODE_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app = Client(
    cfg.SESSION_NAME,
    bot_token=cfg.BOT_TOKEN,
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    plugins={'root': os.path.join(__package__, 'plugins')},
    sleep_threshold=30
)

botStartTime = cfg.BOT_START_TIME
api_id = cfg.API_ID
api_hash = cfg.API_HASH
bot_token = cfg.BOT_TOKEN
database = cfg.MONGO_URI
session = cfg.SESSION_NAME
drive_dir = cfg.DRIVE_DIR
index = cfg.INDEX_URL
download_dir = cfg.DOWNLOAD_DIR
encode_dir = cfg.ENCODE_DIR
owner = cfg.OWNER_ID
sudo_users = cfg.SUDO_USERS
everyone = cfg.EVERYONE_CHATS
all = cfg.ALL_SUDOers
log_channel = cfg.LOG_CHANNEL
PROGRESS = cfg.PROGRESS
video_mimetype = cfg.VIDEO_MIMETYPES
LOGGER = log.logger
