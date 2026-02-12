from .telegram import upload_to_tg

async def upload_worker(new_file, message, msg):
    return await upload_to_tg(new_file, message, msg)
