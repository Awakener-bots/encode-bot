import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, name="VideoEncoder", log_file="VideoEncoder/utils/extras/logs.txt"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%b-%y %H:%M:%S"
        )
        
        fh = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=20, encoding='utf-8')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)
        
        logging.getLogger("pyrogram").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("pymongo").setLevel(logging.ERROR)

    def dbg(self, action, **kwargs):
        self.logger.debug(self._format(action, **kwargs))

    def inf(self, action, **kwargs):
        self.logger.info(self._format(action, **kwargs))

    def wrn(self, action, **kwargs):
        self.logger.warning(self._format(action, **kwargs))

    def err(self, action, **kwargs):
        self.logger.error(self._format(action, **kwargs))

    def _format(self, action, **kwargs):
        parts = [f"[{action}]"]
        for k, v in kwargs.items():
            parts.append(f"| {k}={v}")
        return " ".join(parts)

log = Logger()
