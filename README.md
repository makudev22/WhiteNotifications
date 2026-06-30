# WhiteNotifications

Self-hosted Telegram web push bridge.

Users sign in with their own Telegram `api_id`, `api_hash`, phone number and login code. The app stores Telegram sessions locally and sends web push notifications to the user's browser.

## Requirements

- Linux server
- Python 3.10+
- HTTPS certificate
- Telegram API credentials from https://my.telegram.org

## Setup

```bash
git clone <repo-url>
cd WhiteNotifications
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python gen_vapid.py
```

Run with HTTPS:

```bash
CERT_PATH=/path/to/fullchain.pem KEY_PATH=/path/to/privkey.pem python server.py
```

Run the Telegram listener in another terminal:

```bash
python notifier.py
```

Open the site, enter `api_id`, `api_hash` and phone number, then enter the Telegram code. On iPhone, add the site to the Home Screen and enable notifications from the installed web app.

## Environment

```bash
HOST=0.0.0.0
PORT=8443
CERT_PATH=/path/to/fullchain.pem
KEY_PATH=/path/to/privkey.pem
VAPID_MAIL=mailto:admin@example.com
READ_DELAY=3
```

## Data

Runtime files are created in `data/`.

Do not commit:

- `data/`
- `*.session`
- `vapid_private.pem`
- `vapid_public.txt`
