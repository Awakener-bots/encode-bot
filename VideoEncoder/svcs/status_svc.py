from ..db.status import status_db
from ..core.log import log

async def add_auth_chat(chat_id):
    current = await status_db.get_auth_chats()
    if str(chat_id) in current.split():
        return False, "Already authorized."
    
    new_auth = f"{current} {chat_id}".strip()
    await status_db.set_auth_chats(new_auth)
    log.inf("auth_add", chat_id=chat_id)
    return True, f"Authorized chat {chat_id}"

async def remove_auth_chat(chat_id):
    current = await status_db.get_auth_chats()
    chats = current.split()
    if str(chat_id) not in chats:
        return False, "Chat not found in database."
        
    chats.remove(str(chat_id))
    await status_db.set_auth_chats(" ".join(chats))
    log.inf("auth_remove", chat_id=chat_id)
    return True, f"Removed chat {chat_id}"

async def add_sudo_user(u_id):
    current = await status_db.get_sudo_users()
    if str(u_id) in current.split():
        return False, "Already sudo."
        
    new_sudo = f"{current} {u_id}".strip()
    await status_db.set_sudo_users(new_sudo)
    log.inf("sudo_add", u_id=u_id)
    return True, f"Added sudo user {u_id}"

async def remove_sudo_user(u_id):
    current = await status_db.get_sudo_users()
    users = current.split()
    if str(u_id) not in users:
        return False, "User not found in database."
        
    users.remove(str(u_id))
    await status_db.set_sudo_users(" ".join(users))
    log.inf("sudo_remove", u_id=u_id)
    return True, f"Removed sudo user {u_id}"
