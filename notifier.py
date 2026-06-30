import asyncio

from telethon import TelegramClient, events

import config as cfg
import db
import push


async def seen(c, e):
    try:
        d = await c.get_dialog(e.chat_id)
        return getattr(d, "read_inbox_max_id", 0) >= e.id
    except Exception:
        return False


def link(a):
    x = getattr(a, "username", None)
    if x:
        return "tg://resolve?domain=" + x
    i = getattr(a, "id", None)
    if i:
        return "tg://user?id=" + str(i)
    return "tg://"


async def run(uid, u):
    c = TelegramClient(str(cfg.sessions / uid), u["api_id"], u["api_hash"])

    @c.on(events.NewMessage(incoming=True))
    async def h(e):
        if cfg.skip_own and e.out:
            return
        if e.chat_id in cfg.muted_chats:
            return
        fresh = db.user(uid) or u
        await asyncio.sleep(int(fresh.get("delay") or cfg.delay))
        if await seen(c, e):
            return
        a = await e.get_sender()
        n = getattr(a, "first_name", None) or getattr(a, "title", None) or "Unknown"
        x = getattr(a, "username", None)
        if x:
            n += f" (@{x})"
        push.send(uid, n, e.raw_text or "[media]", link(a))

    await c.start()
    print("on", u["phone"])
    await c.run_until_disconnected()


async def main():
    db.init()
    ts = {}
    while True:
        for u in db.users():
            if u["id"] not in ts:
                ts[u["id"]] = asyncio.create_task(run(u["id"], u))
        if not ts:
            print("no users")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
