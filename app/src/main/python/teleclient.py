import asyncio, json, threading, os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Keep your existing API credentials here. Replace API_HASH yourself as planned.
api_id = 21882615
api_hash = "a55678cc05c1aad2fb0aaccbf9663241"
session_name = os.path.join(os.path.expanduser("~"), "tglite")

_loop = asyncio.new_event_loop()
_ready = threading.Event()
_client = None
_dialogs = {}
_need_password = False
_phone = None

def _run_loop():
    asyncio.set_event_loop(_loop)
    _ready.set()
    _loop.run_forever()

threading.Thread(target=_run_loop, daemon=True).start()
_ready.wait()

def _run(coro):
    return asyncio.run_coroutine_threadsafe(coro, _loop).result(timeout=60)

async def _ensure_client():
    global _client
    if _client is None:
        _client = TelegramClient(session_name, api_id, api_hash)
    if not _client.is_connected():
        await _client.connect()
    return _client

def _out(data):
    return json.dumps(data, ensure_ascii=False)

def init():
    async def work():
        c = await _ensure_client()
        if await c.is_user_authorized():
            return {"ok": True, "state": "authorized"}
        return {"ok": True, "state": "need_phone"}
    try:
        return _out(_run(work()))
    except Exception as e:
        return _out({"ok": False, "error": str(e)})

def send_code(phone):
    global _phone
    _phone = phone.strip()
    async def work():
        c = await _ensure_client()
        await c.send_code_request(_phone)
        return {"ok": True, "state": "need_code"}
    try:
        return _out(_run(work()))
    except Exception as e:
        return _out({"ok": False, "error": str(e)})

def sign_in(code):
    global _need_password
    async def work():
        c = await _ensure_client()
        try:
            await c.sign_in(phone=_phone, code=code.strip())
            return {"ok": True, "state": "authorized"}
        except SessionPasswordNeededError:
            return {"ok": True, "state": "need_password"}
    try:
        result = _run(work())
        return _out(result)
    except Exception as e:
        return _out({"ok": False, "error": str(e)})

def sign_in_password(password):
    async def work():
        c = await _ensure_client()
        await c.sign_in(password=password)
        return {"ok": True, "state": "authorized"}
    try:
        return _out(_run(work()))
    except Exception as e:
        return _out({"ok": False, "error": str(e)})

def _name(entity):
    username = getattr(entity, "username", None)
    if username:
        return "@" + username
    first = getattr(entity, "first_name", None) or ""
    last = getattr(entity, "last_name", None) or ""
    return (first + " " + last).strip() or getattr(entity, "title", None) or "Unknown"

def get_chats():
    async def work():
        global _dialogs
        c = await _ensure_client()
        if not await c.is_user_authorized():
            return {"ok": False, "state": "need_phone"}
        dialogs = await c.get_dialogs(limit=100)
        _dialogs = {str(d.id): d.entity for d in dialogs}
        result = []
        for d in dialogs:
            ent = d.entity
            kind = "channel" if getattr(ent, "broadcast", False) else (
                "group" if getattr(ent, "title", None) else "private")
            result.append({"id": str(d.id), "name": d.name, "kind": kind,
                           "unread": d.unread_count})
        return {"ok": True, "chats": result}
    try:
        return _out(_run(work()))
    except Exception as e:
        return _out({"ok": False, "error": str(e)})

def get_messages(chat_id):
    async def work():
        c = await _ensure_client()
        ent = _dialogs.get(str(chat_id))
        if ent is None:
            dialogs = await c.get_dialogs(limit=100)
            for d in dialogs:
                _dialogs[str(d.id)] = d.entity
            ent = _dialogs.get(str(chat_id))
        if ent is None:
            return {"ok": False, "error": "Chat not found; refresh the chat list"}
        msgs = await c.get_messages(ent, limit=60)
        result = []
        for m in reversed(msgs):
            if not m.message:
                continue
            try:
                sender = await m.get_sender()
                name = _name(sender)
            except Exception:
                name = "Unknown"
            result.append({"id": m.id, "sender": name, "text": m.message,
                           "out": bool(m.out), "date": m.date.isoformat() if m.date else ""})
        return {"ok": True, "messages": result}
    try:
        return _out(_run(work()))
    except Exception as e:
        return _out({"ok": False, "error": str(e)})

def send_message(chat_id, text):
    async def work():
        c = await _ensure_client()
        ent = _dialogs.get(str(chat_id))
        if ent is None:
            dialogs = await c.get_dialogs(limit=100)
            for d in dialogs:
                _dialogs[str(d.id)] = d.entity
            ent = _dialogs.get(str(chat_id))
        if ent is None:
            return {"ok": False, "error": "Chat not found"}
        await c.send_message(ent, text)
        return {"ok": True}
    try:
        return _out(_run(work()))
    except Exception as e:
        return _out({"ok": False, "error": str(e)})
