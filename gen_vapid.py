import base64
from py_vapid import Vapid
import config as cfg

v = Vapid()
v.generate_keys()
v.save_key(cfg.vapid_priv)

enc = __import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding"]).Encoding
fmt = __import__("cryptography.hazmat.primitives.serialization", fromlist=["PublicFormat"]).PublicFormat

raw = v.public_key.public_bytes(encoding=enc.X962, format=fmt.UncompressedPoint)
pub = base64.urlsafe_b64encode(raw).decode().rstrip("=")

with open(cfg.vapid_pub, "w", encoding="utf-8") as f:
    f.write(pub)

print(pub)
