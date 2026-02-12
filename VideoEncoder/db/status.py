from . import db

class StatusDB:
    def __init__(self):
        self.col = db.status

    async def get_killed_status(self):
        status = await self.col.find_one({'id': 'killed'})
        if not status:
            await self.col.insert_one({'id': 'killed', 'status': False})
            return False
        return status.get('status', False)

    async def set_killed_status(self, status):
        await self.col.update_one({'id': 'killed'}, {'$set': {'status': status}}, upsert=True)

    async def get_auth_chats(self):
        status = await self.col.find_one({'id': 'auth'})
        return status.get('chat', '') if status else ''

    async def set_auth_chats(self, chats):
        await self.col.update_one({'id': 'auth'}, {'$set': {'chat': chats}}, upsert=True)

    async def get_sudo_users(self):
        status = await self.col.find_one({'id': 'sudo'})
        return status.get('sudo_', '') if status else ''

    async def set_sudo_users(self, users):
        await self.col.update_one({'id': 'sudo'}, {'$set': {'sudo_': users}}, upsert=True)

    async def get_public_mode(self):
        status = await self.col.find_one({'id': 'mode'})
        if not status:
            await self.col.insert_one({'id': 'mode', 'public': False})
            return False
        return status.get('public', False)

    async def set_public_mode(self, status: bool):
        await self.col.update_one({'id': 'mode'}, {'$set': {'public': status}}, upsert=True)

status_db = StatusDB()
