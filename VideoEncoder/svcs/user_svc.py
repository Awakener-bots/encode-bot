from ..db.users import users_db
from ..core.log import log
from ..core.cfg import cfg

async def add_user_if_new(bot, message):
    if not message.from_user:
        return
        
    u_id = message.from_user.id
    if not await users_db.is_user_exist(u_id):
        await users_db.add_user(u_id)
        log.inf("user_new", u_id=u_id, name=message.from_user.first_name)
        
        if cfg.LOG_CHANNEL:
            try:
                mention = f"<a href='tg://user?id={u_id}'>{message.from_user.first_name}</a>"
                text = f"▸ <b>New User</b>\nStatus: ● Active\nUser: {mention}\nBot: @{(await bot.get_me()).username}"
                await bot.send_message(cfg.LOG_CHANNEL, text)
            except Exception as e:
                log.err("log_channel_notify", error=str(e))
