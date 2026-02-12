from pyrogram import Client, filters
from ..utils.helper import check_chat
from ..svcs.user_svc import add_user_if_new
from ..svcs.queue_svc import queue_svc
from ..svcs.encode_svc import start_encode_task
from ..core.cfg import cfg

@Client.on_message(filters.incoming & filters.private & (filters.video | filters.document))
async def encode_video_handler(app, message):
    if message.document:
        if message.document.mime_type not in cfg.VIDEO_MIMETYPES:
            return
    
    await add_user_if_new(app, message)
    
    invite_links = []
    for chat_id in cfg.EVERYONE_CHATS:
        try:
            chat = await app.get_chat(chat_id)
            if chat.invite_link:
                invite_links.append(f"• <a href='{chat.invite_link}'>{chat.title}</a>")
            elif chat.username:
                invite_links.append(f"• <a href='https://t.me/{chat.username}'>{chat.title}</a>")
        except:
            pass
    
    if invite_links:
        links_text = "\n".join(invite_links)
        await message.reply(
            "▸ <b>Encode</b>\n"
            "Status: ● Group Only\n\n"
            "<blockquote>⚠️ Encoding is only available in authorized groups.\n\n"
            f"Join our group to encode videos:\n{links_text}\n\n"
            "Use /settings to configure your encoding preferences here.</blockquote>",
            disable_web_page_preview=True
        )
    else:
        await message.reply(
            "▸ <b>Encode</b>\n"
            "Status: ● Group Only\n\n"
            "<blockquote>⚠️ Encoding is only available in authorized groups.\n\n"
            "Use /settings to configure your encoding preferences here.</blockquote>"
        )

@Client.on_message(filters.command(['420p', '480p', '720p', '1080p', 'enc']))
async def quick_encode_handler(app, message):
    if not await check_chat(message, chat='Both'):
        return
    
    if not message.reply_to_message:
        await message.reply(
            "▸ <b>Encode</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>Reply to a video with this command to encode it.</blockquote>"
        )
        return
    
    reply = message.reply_to_message
    
    if not (reply.video or (reply.document and reply.document.mime_type in cfg.VIDEO_MIMETYPES)):
        await message.reply(
            "▸ <b>Encode</b>\n"
            "Status: ✗ Failed\n\n"
            "<blockquote>The replied message is not a video.</blockquote>"
        )
        return
    
    await add_user_if_new(app, message)
    
    cmd = message.command[0].lower()
    
    overrides = {}
    if cmd in ['420p', '480p']:
        overrides['resolution'] = '480'
    elif cmd == '720p':
        overrides['resolution'] = '720'
    elif cmd == '1080p':
        overrides['resolution'] = '1080'
    
    if len(message.command) > 1:
        custom_name = message.text.split(None, 1)[1].strip()
        if custom_name:
            if "{filename}" in custom_name:
                overrides['rename_template'] = custom_name
            else:
                overrides['rename_template'] = custom_name + " {filename}"
    
    await queue_svc.add(reply, 'tg', start_encode_task, overrides)
    
    status_text = f"Resolution: {cmd.upper()}"
    if 'rename_template' in overrides:
        status_text += f"\nRename: {overrides['rename_template']}"
        
    if cmd == 'enc':
        rename_info = f"\nRename: {overrides['rename_template']}" if 'rename_template' in overrides else ""
        await message.reply(f"▸ <b>Encode</b>\nStatus: ● Queued\nUsing your saved settings.{rename_info}")
    else:
        await message.reply(f"▸ <b>Encode</b>\nStatus: ● Queued\n{status_text}")
