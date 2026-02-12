import os
import time
from dotenv import load_dotenv

for env_file in ['.env', 'config.env', 'VideoEncoder/config.env']:
    if os.path.exists(env_file):
        load_dotenv(env_file)

class Config:
    def __init__(self):
        self.BOT_START_TIME = time.time()
        
        self.API_ID = int(os.environ.get("API_ID", 0))
        self.API_HASH = os.environ.get("API_HASH", "")
        self.BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
        
        self.MONGO_URI = os.environ.get("MONGO_URI", "")
        self.SESSION_NAME = os.environ.get("SESSION_NAME", "VideoEncoder")
        
        self.DRIVE_DIR = os.environ.get("DRIVE_DIR", "")
        self.INDEX_URL = os.environ.get("INDEX_URL", "")
        
        self.DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "VideoEncoder/downloads/")
        self.ENCODE_DIR = os.environ.get("ENCODE_DIR", "VideoEncoder/encodes/")
        
        self.OWNER_ID = list(set(int(x) for x in os.environ.get("OWNER_ID", "").split()))
        self.SUDO_USERS = list(set(int(x) for x in os.environ.get("SUDO_USERS", "").split()))
        self.EVERYONE_CHATS = list(set(int(x) for x in os.environ.get("EVERYONE_CHATS", "").split()))
        self.ALL_SUDOers = self.EVERYONE_CHATS + self.SUDO_USERS + self.OWNER_ID
        
        try:
            self.LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
        except (ValueError, TypeError):
            self.LOG_CHANNEL = self.OWNER_ID[0] if self.OWNER_ID else 0
            
        self.VIDEO_MIMETYPES = [
            "video/x-flv", "video/mp4", "application/x-mpegURL", "video/MP2T",
            "video/3gpp", "video/quicktime", "video/x-msvideo", "video/x-ms-wmv",
            "video/x-matroska", "video/webm", "video/x-m4v", "video/mpeg"
        ]

        self.PROGRESS = """
• {0} of {1}
• Speed: {2}
• ETA: {3}
"""
        
cfg = Config()
