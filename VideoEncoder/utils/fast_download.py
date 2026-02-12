import asyncio
import os
import aiohttp
import time
from ..core.cfg import cfg
from ..core.log import log

class FastDownloader:
    
    def __init__(self):
        self.process = None
        self.cancelled = False
        self.task_id = None
        
    async def check_aria2c(self):
        try:
            proc = await asyncio.create_subprocess_exec(
                'aria2c', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return proc.returncode == 0
        except:
            return False
    
    async def download(self, url, filepath, msg, task_id):
        self.task_id = task_id
        self.cancelled = False
        
        if await self.check_aria2c():
            return await self._download_aria2c(url, filepath, msg)
        else:
            return await self._download_aiohttp(url, filepath, msg)
    
    async def _download_aria2c(self, url, filepath, msg):
        dirname = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        
        cmd = [
            'aria2c',
            '-x', '16',
            '-s', '16',
            '-k', '1M',
            '--file-allocation=none',
            '--summary-interval=1',
            '-d', dirname,
            '-o', filename,
            '--allow-overwrite=true',
            url
        ]
        
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        log.inf("aria2c_start", task_id=self.task_id, url=url[:50])
        
        start_time = time.time()
        last_update = 0
        
        while True:
            from ..svcs.task_manager import task_manager
            task = task_manager.get_task(self.task_id)
            if self.cancelled or (task and task.get("cancelled")):
                self.process.terminate()
                return None
                
            line = await self.process.stdout.readline()
            if not line:
                break
                
            line = line.decode('utf-8', errors='ignore').strip()
            
            if '[#' in line and ']' in line:
                current_time = time.time()
                if current_time - last_update >= 2:
                    try:
                        progress_text = self._parse_aria2c_progress(line)
                        await msg.edit(
                            f"▸ <b>Downloader</b> [ID: {self.task_id}]\n"
                            f"Status: ● Downloading (aria2c)\n"
                            f"{progress_text}\n"
                            f"<code>/cancel {self.task_id}</code> to stop"
                        )
                        last_update = current_time
                    except:
                        pass
        
        await self.process.wait()
        
        if self.process.returncode == 0 and os.path.exists(filepath):
            elapsed = time.time() - start_time
            log.inf("aria2c_complete", task_id=self.task_id, time=f"{elapsed:.1f}s")
            return filepath
        return None
    
    def _parse_aria2c_progress(self, line):
        try:
            parts = line.split()
            for part in parts:
                if 'MiB' in part or 'KiB' in part or 'GiB' in part:
                    if '/' in part:
                        return f"Progress: {part}"
                if 'DL:' in part:
                    return f"Speed: {part.replace('DL:', '')}"
            return line
        except:
            return ""
    
    async def _download_aiohttp(self, url, filepath, msg):
        try:
            timeout = aiohttp.ClientTimeout(total=3600)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    start_time = time.time()
                    last_update = 0
                    
                    with open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(1024 * 1024):
                            from ..svcs.task_manager import task_manager
                            task = task_manager.get_task(self.task_id)
                            if self.cancelled or (task and task.get("cancelled")):
                                return None
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            current_time = time.time()
                            if current_time - last_update >= 2:
                                percent = (downloaded / total_size * 100) if total_size else 0
                                speed = downloaded / (current_time - start_time) / 1024 / 1024
                                
                                await msg.edit(
                                    f"▸ <b>Downloader</b> [ID: {self.task_id}]\n"
                                    f"Status: ● Downloading\n"
                                    f"Progress: {percent:.1f}% | Speed: {speed:.1f} MB/s\n"
                                    f"<code>/cancel {self.task_id}</code> to stop"
                                )
                                last_update = current_time
                    
                    return filepath
        except Exception as e:
            log.err("aiohttp_download", error=str(e))
            return None
    
    def cancel(self):
        self.cancelled = True
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
