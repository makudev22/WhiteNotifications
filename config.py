import os
from pathlib import Path

root = Path(__file__).resolve().parent
data = root / "data"
sessions = data / "sessions"
db = data / "app.db"

vapid_priv = root / "vapid_private.pem"
vapid_pub = root / "vapid_public.txt"
vapid_mail = os.getenv("VAPID_MAIL", "mailto:admin@example.com")

host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", "8443"))
cert_path = os.getenv("CERT_PATH", "")
key_path = os.getenv("KEY_PATH", "")

skip_own = True
muted_chats = []
delay = int(os.getenv("READ_DELAY", "3"))
