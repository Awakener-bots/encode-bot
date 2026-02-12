import ast
import html
import inspect
import sys
import traceback
from pyrogram import Client, filters
from ..utils.helper import check_chat, memory_file

@Client.on_message(filters.command('exec'))
async def exec_handler(client, message):
    if not await check_chat(message, chat='Sudo'):
        return

    code = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not code:
        await message.reply_text("▸ <b>Usage</b>\n<code>/exec [code]</code>")
        return

    tree = ast.parse(code)
    body = tree.body.copy()
    body.append(ast.Return(ast.Name('_ueri', ast.Load())))

    def _gf(body):
        func = ast.AsyncFunctionDef('ex', ast.arguments([], [ast.arg(i, None, None) for i in [
                                    'm', 'message', 'c', 'client', '_ueri']], None, [], [], None, []), body, [], None, None)
        ast.fix_missing_locations(func)
        mod = ast.parse('')
        mod.body = [func]
        fl = locals().copy()
        exec(compile(mod, '<ast>', 'exec'), globals(), fl)
        return fl['ex']

    try:
        exx = _gf(body)
    except:
        exx = _gf(tree.body)

    escaped_code = html.escape(code)
    reply = await message.reply_text(f"▸ <b>Exec</b>\nStatus: ● Executing...\n\n<code>{escaped_code}</code>")
    
    stdout, stderr = sys.stdout, sys.stderr
    wrapped_stdout = memory_file(bytes=False)
    wrapped_stderr = memory_file(bytes=False)
    sys.stdout, sys.stderr = wrapped_stdout, wrapped_stderr
    
    try:
        async_obj = exx(message, message, client, client, object())
        if inspect.isasyncgen(async_obj):
            returned = [i async for i in async_obj]
        else:
            returned = [await async_obj]
    except Exception:
        await message.reply_text(f"▸ <b>Error</b>\n<code>{traceback.format_exc()}</code>")
        return
    finally:
        sys.stdout, sys.stderr = stdout, stderr

    wrapped_stdout.seek(0)
    wrapped_stderr.seek(0)
    output = wrapped_stderr.read() + wrapped_stdout.read()
    output += "\n".join([str(i) for i in returned if i is not None])
    
    final_output = html.escape(output.strip()) or "undefined"
    await reply.edit_text(f"▸ <b>Exec</b>\nStatus: ● Executed\n\n<code>{final_output}</code>")
