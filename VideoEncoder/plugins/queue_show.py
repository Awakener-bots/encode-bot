import html
from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..svcs.queue_svc import queue_svc
from ..svcs.task_manager import task_manager

def get_message_link(chat_id, msg_id):
    if str(chat_id).startswith('-100'):
        clean_id = str(chat_id)[4:]
        return f"https://t.me/c/{clean_id}/{msg_id}"
    elif chat_id < 0:
        return f"https://t.me/c/{str(chat_id)[1:]}/{msg_id}"
    else:
        return None

@Client.on_message(filters.command(['queue']))
async def queue_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
        
    length = queue_svc.get_length()
    active_tasks = task_manager.get_all_tasks()
    
    if length == 0 and not active_tasks:
        await message.reply("▸ <b>Queue</b>\nStatus: ● Empty\n\n<i>No active or pending tasks.</i>")
        return
    
    text = "▸ <b>Queue Status</b>\n\n"
    
    current = queue_svc.get_current_task_info()
    if current:
        link = get_message_link(current['chat_id'], current['msg_id'])
        name = html.escape(current['name'])
        
        if link:
            text += f"<b>⚡ Processing:</b>\n"
            text += f"├ <a href='{link}'>{name}</a>\n"
        else:
            text += f"<b>⚡ Processing:</b>\n"
            text += f"├ {name}\n"
        
        if current['u_id']:
            text += f"└ User: <code>{current['u_id']}</code>\n"
        text += "\n"
    
    if active_tasks:
        text += "<b>🔄 Active Tasks:</b>\n"
        for tid, task in active_tasks.items():
            task_type = "⬇️" if task.get("type") == "download" else "🔄"
            user_id = task.get("user_id", "Unknown")
            text += f"├ {task_type} <code>{tid}</code> (User: {user_id})\n"
        text += "\n"
    
    queue_info = queue_svc.get_queue_info()
    if queue_info:
        text += "<b>⏳ Waiting Queue:</b>\n"
        for i, item in enumerate(queue_info, start=1):
            link = get_message_link(item['chat_id'], item['msg_id'])
            name = html.escape(item['name'])
            
            if link:
                text += f"{i}. <a href='{link}'>{name}</a>"
            else:
                text += f"{i}. {name}"
            
            if item['u_id']:
                text += f" (<code>{item['u_id']}</code>)"
            text += "\n"
        text += "\n"
    
    total = length + len(active_tasks)
    text += f"<b>📊 Total:</b> {total} task(s)"
    
    await message.reply(text, disable_web_page_preview=True)
