import random
import string
from ..core.log import log

class TaskManager:
    
    def __init__(self):
        self._tasks = {}
        
    def generate_id(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    def register_download(self, task_id, process, downloader, message, user_id):
        self._tasks[task_id] = {
            "type": "download",
            "process": process,
            "downloader": downloader,
            "message": message,
            "user_id": user_id,
            "cancelled": False
        }
        log.inf("task_register", task_id=task_id, type="download", user_id=user_id)
        
    def register_encode(self, task_id, process, message, output_path=None):
        if task_id in self._tasks:
            self._tasks[task_id]["type"] = "encode"
            self._tasks[task_id]["process"] = process
            self._tasks[task_id]["output_path"] = output_path
        else:
            self._tasks[task_id] = {
                "type": "encode",
                "process": process,
                "message": message,
                "user_id": message.from_user.id if message.from_user else None,
                "output_path": output_path,
                "cancelled": False
            }
        log.inf("task_register", task_id=task_id, type="encode")
        
    def get_task(self, task_id):
        return self._tasks.get(task_id)
    
    def get_all_tasks(self):
        return dict(self._tasks)
    
    async def cancel_task(self, task_id, user_id=None):
        task = self._tasks.get(task_id)
        if not task:
            return False, "Task not found."
        
        if user_id and task.get("user_id") != user_id:
            from ..core.cfg import cfg
            if user_id not in cfg.OWNER_ID and user_id not in cfg.SUDO_USERS:
                return False, "You can only cancel your own tasks."
        
        task["cancelled"] = True
        
        if task.get("downloader"):
            task["downloader"].cancel()
            
        proc = task.get("process")
        if proc:
            try:
                proc.terminate()
            except:
                pass
        
        log.inf("task_cancel", task_id=task_id, by=user_id)
        return True, f"Task {task_id} cancelled."
    
    def remove_task(self, task_id):
        if task_id in self._tasks:
            del self._tasks[task_id]
            log.inf("task_remove", task_id=task_id)
    
    def get_user_tasks(self, user_id):
        return {tid: t for tid, t in self._tasks.items() if t.get("user_id") == user_id}

task_manager = TaskManager()
