from ...db.users import users_db
from ...db.status import status_db

class DBBridge:
    def __getattr__(self, name):
        if hasattr(users_db, name):
            return getattr(users_db, name)
        if hasattr(status_db, name):
            return getattr(status_db, name)
        raise AttributeError(f"DBBridge has no attribute {name}")
    
    async def get_sudo(self):
        return await status_db.get_sudo_users()
    
    async def get_chat(self):
        return await status_db.get_auth_chats()

db = DBBridge()
