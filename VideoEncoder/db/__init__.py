import motor.motor_asyncio
from ..core.cfg import cfg
from ..core.log import log

class MongoManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(cfg.MONGO_URI)
            self.db = self.client[cfg.SESSION_NAME]
            log.inf("db", status="connected", scope="mongo")
        except Exception as e:
            log.err("db", status="failed", error=str(e))
            raise SystemExit("Fatal: Could not connect to MongoDB")

mongo = MongoManager()
db = mongo.db
