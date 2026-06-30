import base64
import json

import config as cfg
import db


def key():
    with open(cfg.vapid_pub, encoding="utf-8") as f:
        k = f.read().strip()
    p = "=" * ((4 - len(k) % 4) % 4)
    try:
        b = base64.urlsafe_b64decode(k + p)
    except Exception as e:
        raise RuntimeError("bad key") from e
    if len(b) != 65 or b[0] != 4:
        raise RuntimeError("bad key")
    return k


def add(uid, s):
    if not db.user(uid):
        return False
    db.sub(uid, s)
    return True


def send(uid, title, body, url="/"):
    from pywebpush import webpush

    msg = json.dumps({"title": title, "body": body, "url": url}, ensure_ascii=False)
    for x in db.subs(uid):
        s = json.loads(x["data"])
        try:
            webpush(
                subscription_info=s,
                data=msg,
                vapid_private_key=str(cfg.vapid_priv),
                vapid_claims={"sub": cfg.vapid_mail},
            )
        except Exception as e:
            print("push failed:", e)
            db.dead(x["endpoint"])
