import asyncio
import os
import shutil
from collections import deque
from ..core.log import log

class QueueService:
    def __init__(self):
        self._queue = deque()
        self._processing = False
        self._current_task = None

    async def add(self, message, source_type, handler_func, overrides=None):
        self._queue.append((message, source_type, handler_func, overrides or {}))
        log.inf("queue_add", u_id=message.from_user.id if message.from_user else "unknown", pos=len(self._queue))
        
        if not self._processing:
            await self._process_next()
        else:
            await message.reply("▸ <b>Queue</b>\nStatus: ● Waiting\nYour task has been added to the queue.")

    async def _process_next(self):
        if not self._queue:
            self._processing = False
            self._current_task = None
            return

        self._processing = True
        message, source_type, handler_func, overrides = self._queue.popleft()
        self._current_task = {"msg": message, "proc": None, "path": None}
        
        try:
            log.inf("queue_process_start", u_id=message.from_user.id if message.from_user else "unknown")
            await handler_func(message, source_type, overrides)
        except asyncio.CancelledError:
            log.wrn("queue_process_cancelled", u_id=message.from_user.id if message.from_user else "unknown")
        except Exception as e:
            log.err("queue_process_failed", error=str(e))
            await message.reply("▸ <b>Error</b>\nStatus: ✗ Failed\nReason: An internal error occurred while processing your task.")
        finally:
            self._current_task = None
            await self._process_next()

    def set_current_proc(self, proc, path=None):
        if self._current_task:
            self._current_task["proc"] = proc
            self._current_task["path"] = path

    async def cancel_current_task(self):
        if not self._current_task:
            return False, "No task is currently running."
        
        proc = self._current_task.get("proc")
        msg = self._current_task.get("msg")
        path = self._current_task.get("path")
        
        if proc:
            try:
                proc.terminate()
            except:
                pass
        
        if path and os.path.exists(path):
            try:
                if os.path.isfile(path): os.remove(path)
                elif os.path.isdir(path): shutil.rmtree(path)
            except:
                pass
                
        await msg.reply("▸ <b>Queue</b>\nStatus: ● Cancelled\nThe current task has been terminated.")
        return True, "Task cancelled."

    def get_length(self):
        len_q = len(self._queue)
        return len_q + (1 if self._processing else 0)

    def get_queue_info(self):
        info = []
        for msg, st, _, _overrides in self._queue:
            name = "Unknown"
            if msg.video: 
                name = msg.video.file_name or "Video"
            elif msg.document: 
                name = msg.document.file_name or "Document"
            elif msg.text: 
                parts = msg.text.split("|")
                name = parts[-1].strip() if len(parts) > 1 else msg.text.split()[-1][:30]
            
            info.append({
                "name": name[:40],
                "type": st, 
                "u_id": msg.from_user.id if msg.from_user else None,
                "chat_id": msg.chat.id,
                "msg_id": msg.id
            })
        return info
    
    def get_current_task_info(self):
        if not self._current_task:
            return None
        
        msg = self._current_task.get("msg")
        if not msg:
            return None
            
        name = "Unknown"
        if msg.video: 
            name = msg.video.file_name or "Video"
        elif msg.document: 
            name = msg.document.file_name or "Document"
        elif msg.text:
            parts = msg.text.split("|")
            name = parts[-1].strip() if len(parts) > 1 else "URL Task"
            
        return {
            "name": name[:40],
            "u_id": msg.from_user.id if msg.from_user else None,
            "chat_id": msg.chat.id,
            "msg_id": msg.id
        }

    def clear_queue(self):
        self._queue.clear()
        log.inf("queue_clear")

queue_svc = QueueService()
