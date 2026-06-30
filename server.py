import asyncio

from flask import Flask, Response, jsonify, make_response, request, send_from_directory
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

import config as cfg
import db
import push

app = Flask(__name__, static_folder="static")


def uid():
    return request.cookies.get("u", "")


def sess(u):
    return str(cfg.sessions / u["id"])


async def ask(u):
    c = TelegramClient(sess(u), u["api_id"], u["api_hash"])
    await c.connect()
    r = await c.send_code_request(u["phone"])
    await c.disconnect()
    return r.phone_code_hash


async def sign(u, code=None, pwd=None):
    c = TelegramClient(sess(u), u["api_id"], u["api_hash"])
    await c.connect()
    try:
        if pwd:
            await c.sign_in(password=pwd)
        else:
            await c.sign_in(u["phone"], code, phone_code_hash=u["code_hash"])
    finally:
        await c.disconnect()


def go(x):
    return asyncio.run(x)


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")


@app.route("/sw.js")
def sw():
    return send_from_directory("static", "sw.js")


@app.route("/icon.png")
def icon():
    return send_from_directory("static", "icon.png")


@app.route("/vapid_public_key")
def vapid_key():
    return Response(push.key(), mimetype="text/plain")


@app.route("/me")
def me():
    u = db.user(uid())
    if not u:
        return jsonify({"ok": False})
    return jsonify({"ok": True, "phone": u["phone"], "ready": bool(u["ok"]), "delay": u["delay"]})


@app.route("/start", methods=["POST"])
def start():
    x = request.get_json() or {}
    if not x.get("api_id") or not x.get("api_hash") or not x.get("phone"):
        return jsonify({"ok": False, "err": "fill"}), 400
    i = db.new(x)
    u = db.user(i)
    h = go(ask(u))
    db.code(i, h)
    r = make_response(jsonify({"ok": True}))
    r.set_cookie("u", i, max_age=60 * 60 * 24 * 365, httponly=True, samesite="Lax")
    return r


@app.route("/code", methods=["POST"])
def code():
    u = db.user(uid())
    x = request.get_json() or {}
    if not u or not x.get("code"):
        return jsonify({"ok": False}), 400
    try:
        go(sign(u, code=x["code"]))
    except SessionPasswordNeededError:
        return jsonify({"ok": False, "pass": True})
    db.ok(u["id"])
    return jsonify({"ok": True})


@app.route("/pass", methods=["POST"])
def password():
    u = db.user(uid())
    x = request.get_json() or {}
    if not u or not x.get("password"):
        return jsonify({"ok": False}), 400
    go(sign(u, pwd=x["password"]))
    db.ok(u["id"])
    return jsonify({"ok": True})


@app.route("/subscribe", methods=["POST"])
def subscribe():
    if not push.add(uid(), request.get_json()):
        return jsonify({"ok": False}), 401
    return jsonify({"ok": True})


@app.route("/settings", methods=["POST"])
def settings():
    u = db.user(uid())
    if not u:
        return jsonify({"ok": False}), 401
    db.set(u["id"], request.get_json() or {})
    return jsonify({"ok": True})


@app.route("/test_push", methods=["POST"])
def test_push():
    u = db.user(uid())
    if not u:
        return jsonify({"ok": False}), 401
    push.send(u["id"], "WhiteNotifications", "test", "/")
    return jsonify({"ok": True})


@app.route("/out", methods=["POST"])
def out():
    r = make_response(jsonify({"ok": True}))
    r.delete_cookie("u")
    return r


if __name__ == "__main__":
    db.init()
    push.key()
    ssl = (cfg.cert_path, cfg.key_path) if cfg.cert_path and cfg.key_path else None
    app.run(host=cfg.host, port=cfg.port, ssl_context=ssl)
