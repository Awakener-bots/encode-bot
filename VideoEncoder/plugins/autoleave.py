from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from ..core.cfg import cfg
from ..core.log import log

@Client.on_chat_member_updated()
async def chat_member_handler(app: Client, update):
    me = await app.get_me()
    if update.new_chat_member is None or update.new_chat_member.user.id != me.id:
        return
    
    chat = update.chat
    chat_id = chat.id
    
    if chat.type == ChatType.PRIVATE:
        return
    
    new_status = update.new_chat_member.status
    old_status = update.old_chat_member.status if update.old_chat_member else None
    
    was_member = old_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    is_member = new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    
    if not was_member and is_member:
        log.inf("bot_added_to_chat", chat_id=chat_id, chat_title=chat.title)
        
        if chat_id in cfg.EVERYONE_CHATS:
            log.inf("bot_allowed_chat", chat_id=chat_id)
            await app.send_message(
                chat_id,
                "▸ <b>VideoEncoder</b>\n"
                "Status: ● Online\n\n"
                "<blockquote>I'm ready to encode videos in this group!\n"
                "Send /help to see available commands.</blockquote>"
            )
            return
        
        log.wrn("bot_unauthorized_chat", chat_id=chat_id, chat_title=chat.title)
        
        invite_links = []
        for allowed_chat_id in cfg.EVERYONE_CHATS:
            try:
                allowed_chat = await app.get_chat(allowed_chat_id)
                if allowed_chat.invite_link:
                    invite_links.append(f"• <a href='{allowed_chat.invite_link}'>{allowed_chat.title}</a>")
                elif allowed_chat.username:
                    invite_links.append(f"• <a href='https://t.me/{allowed_chat.username}'>{allowed_chat.title}</a>")
            except Exception as e:
                log.wrn("get_invite_link_failed", chat_id=allowed_chat_id, error=str(e))
        
        if invite_links:
            links_text = "\n".join(invite_links)
            leave_msg = (
                "▸ <b>VideoEncoder</b>\n"
                "Status: ● Unauthorized Group\n\n"
                "<blockquote>❌ I'm not allowed to work in this group.\n\n"
                "I only work in authorized groups. Please join:\n"
                f"{links_text}\n\n"
                "Leaving this group now...</blockquote>"
            )
        else:
            leave_msg = (
                "▸ <b>VideoEncoder</b>\n"
                "Status: ● Unauthorized Group\n\n"
                "<blockquote>❌ I'm not allowed to work in this group.\n\n"
                "I only work in authorized groups.\n"
                "Contact the bot owner for access.\n\n"
                "Leaving this group now...</blockquote>"
            )
        
        try:
            await app.send_message(chat_id, leave_msg, disable_web_page_preview=True)
        except Exception as e:
            log.err("leave_msg_failed", error=str(e))
        
        try:
            await app.leave_chat(chat_id)
            log.inf("bot_left_chat", chat_id=chat_id)
        except Exception as e:
            log.err("leave_chat_failed", chat_id=chat_id, error=str(e))


@Client.on_message(filters.new_chat_members)
async def new_member_handler(app: Client, message):
    me = await app.get_me()
    
    for member in message.new_chat_members:
        if member.id == me.id:
            chat_id = message.chat.id
            
            if chat_id in cfg.EVERYONE_CHATS:
                return
            
            log.wrn("bot_unauthorized_chat_fallback", chat_id=chat_id)
            
            invite_links = []
            for allowed_chat_id in cfg.EVERYONE_CHATS:
                try:
                    allowed_chat = await app.get_chat(allowed_chat_id)
                    if allowed_chat.invite_link:
                        invite_links.append(f"• <a href='{allowed_chat.invite_link}'>{allowed_chat.title}</a>")
                    elif allowed_chat.username:
                        invite_links.append(f"• <a href='https://t.me/{allowed_chat.username}'>{allowed_chat.title}</a>")
                except:
                    pass
            
            if invite_links:
                links_text = "\n".join(invite_links)
                leave_msg = (
                    "▸ <b>VideoEncoder</b>\n"
                    "Status: ● Unauthorized Group\n\n"
                    f"<blockquote>❌ I only work in authorized groups.\n\nJoin here:\n{links_text}</blockquote>"
                )
            else:
                leave_msg = (
                    "▸ <b>VideoEncoder</b>\n"
                    "Status: ● Unauthorized Group\n\n"
                    "<blockquote>❌ I only work in authorized groups.</blockquote>"
                )
            
            try:
                await message.reply(leave_msg, disable_web_page_preview=True)
                await app.leave_chat(chat_id)
            except:
                pass
            
            return
