import datetime
from . import db

class UsersDB:
    def __init__(self):
        self.col = db.users

    def _new_user(self, u_id):
        return dict(
            u_id=u_id,
            join_date=datetime.date.today().isoformat(),
            extensions='MKV',
            hevc=False,
            aspect=False,
            cabac=False,
            reframe='pass',
            tune=True,
            frame='source',
            audio='aac',
            sample='source',
            bitrate='source',
            bits=False,
            channels='source',
            preset='vf',
            metadata=True,
            hardsub=False,
            watermark=False,
            subtitles=True,
            resolution='OG',
            upload_as_doc=False,
            crf=26,
            resize=False,
            rename_template='[HEVC] {filename}',
            watermark_text='@VideoEncoder',
            watermark_type='text',
            watermark_position='br',
            watermark_size='medium',
            watermark_image=None,
            custom_thumbnail=None,
            total_space_saved=0,
            encoded_count=0,
            premium=False
        )

    async def add_user(self, u_id):
        user = self._new_user(u_id)
        await self.col.insert_one(user)

    async def is_user_exist(self, u_id):
        user = await self.col.find_one({'u_id': int(u_id)})
        if not user:
            user = await self.col.find_one({'id': int(u_id)})
        return True if user else False

    async def get_user(self, u_id):
        try:
            uid = int(u_id)
        except (ValueError, TypeError):
            return self._new_user(u_id)

        user = await self.col.find_one({'u_id': uid})
        if not user:
            user = await self.col.find_one({'id': uid})
        if not user:
            new_user_data = self._new_user(uid)
            await self.col.insert_one(new_user_data)
            return new_user_data
        return user

    async def update_user(self, u_id, settings: dict):
        await self.col.update_one(
            {'$or': [{'u_id': int(u_id)}, {'id': int(u_id)}]},
            {'$set': settings}
        )

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, u_id):
        await self.col.delete_many({'$or': [{'u_id': int(u_id)}, {'id': int(u_id)}]})

users_db = UsersDB()
