import json
import sqlite3
import time
from uuid import uuid4

import config as cfg


def con():
    cfg.data.mkdir(exist_ok=True)
    cfg.sessions.mkdir(exist_ok=True)
    c = sqlite3.connect(cfg.db)
    c.row_factory = sqlite3.Row
    return c


def init():
    with con() as c:
        c.execute(
            "create table if not exists users (id text primary key, phone text, api_id integer, api_hash text, code_hash text, ok integer default 0, delay integer default 3, ts integer)"
        )
        c.execute(
            "create table if not exists subs (id integer primary key autoincrement, user_id text, endpoint text unique, data text)"
        )
        cols = [x["name"] for x in c.execute("pragma table_info(users)").fetchall()]
        if "delay" not in cols:
            c.execute("alter table users add column delay integer default 3")


def one(q, a=()):
    init()
    with con() as c:
        r = c.execute(q, a).fetchone()
        return dict(r) if r else None


def all(q, a=()):
    init()
    with con() as c:
        return [dict(x) for x in c.execute(q, a).fetchall()]


def run(q, a=()):
    init()
    with con() as c:
        c.execute(q, a)


def new(d):
    uid = uuid4().hex
    run(
        "insert into users (id, phone, api_id, api_hash, ts) values (?, ?, ?, ?, ?)",
        (uid, d["phone"], int(d["api_id"]), d["api_hash"], int(time.time())),
    )
    return uid


def user(uid):
    if not uid:
        return None
    return one("select * from users where id = ?", (uid,))


def users():
    return all("select * from users where ok = 1")


def code(uid, h):
    run("update users set code_hash = ? where id = ?", (h, uid))


def ok(uid):
    run("update users set ok = 1 where id = ?", (uid,))


def set(uid, d):
    run("update users set delay = ? where id = ?", (int(d.get("delay") or 3), uid))


def sub(uid, s):
    run(
        "insert or replace into subs (user_id, endpoint, data) values (?, ?, ?)",
        (uid, s["endpoint"], json.dumps(s, ensure_ascii=False)),
    )


def subs(uid):
    return all("select * from subs where user_id = ?", (uid,))


def dead(endpoint):
    run("delete from subs where endpoint = ?", (endpoint,))
