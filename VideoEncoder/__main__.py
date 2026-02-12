import dns.resolver
from pyrogram import idle
from . import app
from .core.cfg import cfg
from .core.log import log
import time
import http.client
import email.utils

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

def sync_bot_time():
    try:
        conn = http.client.HTTPConnection("google.com", timeout=5)
        conn.request("GET", "/")
        r = conn.getresponse()
        ts = r.getheader("date")
        if ts:
            remote_time = email.utils.mktime_tz(email.utils.parsedate_tz(ts))
            offset = int(remote_time - time.time())
            if abs(offset) > 2:
                log.inf("time_sync", offset=f"{offset}s", status="applied")
                return offset
    except Exception as e:
        log.err("time_sync_failed", error=str(e))
    return 0

async def main():
    try:
        try:
            await app.start()
        except Exception as e:
            if "[16]" in str(e):
                offset = sync_bot_time()
                if hasattr(app, "session") and app.session:
                    app.session.offset = offset
                    log.inf("time_correction", status="applied", offset=f"{offset}s")
                    await app.start()
                else:
                    raise e
            else:
                raise e
        
        log.inf("bot", status="started", username=(await app.get_me()).username)
        
        if cfg.LOG_CHANNEL:
            await app.send_message(
                cfg.LOG_CHANNEL, 
                f"▸ <b>VideoEncoder</b>\nStatus: ● Online\nBot: @{(await app.get_me()).username}"
            )
            
        await idle()
    except Exception as e:
        import traceback
        traceback.print_exc()
        log.logger.exception(f"bot_fatal: {str(e)}")
    finally:
        if app.is_connected:
            await app.stop()
        log.inf("bot", status="stopped")

if __name__ == "__main__":
    app.loop.run_until_complete(main())
