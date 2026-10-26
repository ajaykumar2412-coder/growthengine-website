"""WhatsApp lead reminders: receives leads from Google Sheets and sends a
configurable sequence of WhatsApp template messages via the Meta Cloud API.

Standard library only (Python 3.9+). Run: python3 server.py
"""
import json
import os
import re
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))


def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_env(os.path.join(HERE, ".env"))

PORT = int(os.environ.get("PORT", "8080"))
LEAD_SECRET = os.environ.get("LEAD_SECRET", "")
WA_TOKEN = os.environ.get("WA_TOKEN", "")
WA_PHONE_NUMBER_ID = os.environ.get("WA_PHONE_NUMBER_ID", "")
WA_VERIFY_TOKEN = os.environ.get("WA_VERIFY_TOKEN", "")
WA_API_VERSION = os.environ.get("WA_API_VERSION", "v21.0")
DEFAULT_COUNTRY_CODE = os.environ.get("DEFAULT_COUNTRY_CODE", "91")
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"
DB_PATH = os.environ.get("DB_PATH", os.path.join(HERE, "leads.db"))
SEQUENCE_PATH = os.environ.get("SEQUENCE_PATH", os.path.join(HERE, "sequence.json"))
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "30"))

db_lock = threading.Lock()


def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


conn = db()
conn.executescript(
    """
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY,
        phone TEXT NOT NULL,
        data TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',  -- active | replied | stopped
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        lead_id INTEGER NOT NULL REFERENCES leads(id),
        step INTEGER NOT NULL,
        send_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',  -- pending | sent | failed | cancelled
        response TEXT
    );
    """
)


def now():
    return datetime.now(timezone.utc)


def load_sequence():
    with open(SEQUENCE_PATH) as f:
        return json.load(f)


def normalize_phone(raw):
    digits = re.sub(r"\D", "", str(raw or ""))
    digits = digits.lstrip("0")
    if len(digits) == 10:
        digits = DEFAULT_COUNTRY_CODE + digits
    return digits


def fill(text, lead):
    """Replace {column} placeholders with the lead's sheet values."""
    return re.sub(r"\{(\w+)\}", lambda m: str(lead.get(m.group(1), "")), text)


def add_lead(payload):
    lead = {str(k).strip().lower().replace(" ", "_"): v for k, v in payload.items()}
    phone = normalize_phone(lead.get("phone") or lead.get("whatsapp") or lead.get("mobile"))
    if len(phone) < 11:
        raise ValueError("missing or invalid phone")
    lead["phone"] = phone
    steps = load_sequence()["steps"]
    start = now()
    with db_lock:
        cur = conn.execute(
            "INSERT INTO leads (phone, data, created_at) VALUES (?, ?, ?)",
            (phone, json.dumps(lead), start.isoformat()),
        )
        lead_id = cur.lastrowid
        for i, step in enumerate(steps):
            send_at = start + timedelta(minutes=step.get("delay_minutes", 0))
            conn.execute(
                "INSERT INTO messages (lead_id, step, send_at) VALUES (?, ?, ?)",
                (lead_id, i, send_at.isoformat()),
            )
        conn.commit()
    return lead_id, len(steps)


def send_template(phone, step, lead):
    body = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": step["template"],
            "language": {"code": step.get("language", "en")},
        },
    }
    params = step.get("params", [])
    if params:
        body["template"]["components"] = [{
            "type": "body",
            "parameters": [{"type": "text", "text": fill(p, lead) or "-"} for p in params],
        }]
    if DRY_RUN:
        print("[dry-run] would send:", json.dumps(body))
        return True, "dry-run"
    req = urllib.request.Request(
        f"https://graph.facebook.com/{WA_API_VERSION}/{WA_PHONE_NUMBER_ID}/messages",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {WA_TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return True, resp.read().decode()
    except urllib.error.HTTPError as e:
        return False, e.read().decode()
    except Exception as e:  # network errors
        return False, str(e)


def process_due():
    steps = load_sequence()["steps"]
    with db_lock:
        due = conn.execute(
            """SELECT m.id, m.step, l.phone, l.data FROM messages m
               JOIN leads l ON l.id = m.lead_id
               WHERE m.status = 'pending' AND l.status = 'active' AND m.send_at <= ?
               ORDER BY m.send_at""",
            (now().isoformat(),),
        ).fetchall()
    for row in due:
        if row["step"] >= len(steps):
            status, info = "cancelled", "step removed from sequence"
        else:
            ok, info = send_template(row["phone"], steps[row["step"]], json.loads(row["data"]))
            status = "sent" if ok else "failed"
        print(f"message {row['id']} to {row['phone']} step {row['step']}: {status}")
        with db_lock:
            conn.execute("UPDATE messages SET status = ?, response = ? WHERE id = ?",
                         (status, info[:1000], row["id"]))
            conn.commit()


def handle_reply(phone):
    """Lead replied on WhatsApp: stop their remaining reminders."""
    if not load_sequence().get("stop_on_reply", True):
        return
    with db_lock:
        ids = [r["id"] for r in conn.execute(
            "SELECT id FROM leads WHERE phone = ? AND status = 'active'", (phone,))]
        for lead_id in ids:
            conn.execute("UPDATE leads SET status = 'replied' WHERE id = ?", (lead_id,))
            conn.execute("UPDATE messages SET status = 'cancelled' "
                         "WHERE lead_id = ? AND status = 'pending'", (lead_id,))
        conn.commit()
    if ids:
        print(f"{phone} replied; stopped reminders for leads {ids}")


def scheduler():
    while True:
        try:
            process_due()
        except Exception as e:
            print("scheduler error:", e)
        time.sleep(POLL_SECONDS)


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, payload):
        body = payload if isinstance(payload, str) else json.dumps(payload, indent=2)
        self.send_response(code)
        self.send_header("Content-Type", "text/plain" if isinstance(payload, str) else "application/json")
        self.end_headers()
        self.wfile.write(body.encode())

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def authorized(self):
        return LEAD_SECRET and self.headers.get("X-Secret") == LEAD_SECRET

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if url.path == "/webhook":  # Meta webhook verification
            if q.get("hub.verify_token", [""])[0] == WA_VERIFY_TOKEN and WA_VERIFY_TOKEN:
                return self.reply(200, q.get("hub.challenge", [""])[0])
            return self.reply(403, "forbidden")
        if url.path == "/leads":
            if not self.authorized():
                return self.reply(401, {"error": "unauthorized"})
            with db_lock:
                leads = [dict(r) for r in conn.execute(
                    "SELECT * FROM leads ORDER BY id DESC LIMIT 200")]
                for lead in leads:
                    lead["data"] = json.loads(lead["data"])
                    lead["messages"] = [dict(m) for m in conn.execute(
                        "SELECT step, send_at, status FROM messages WHERE lead_id = ? ORDER BY step",
                        (lead["id"],))]
            return self.reply(200, leads)
        if url.path == "/":
            return self.reply(200, "ok")
        self.reply(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/lead":
            if not self.authorized():
                return self.reply(401, {"error": "unauthorized"})
            try:
                lead_id, steps = add_lead(self.read_json())
            except ValueError as e:
                return self.reply(400, {"error": str(e)})
            return self.reply(200, {"lead_id": lead_id, "scheduled": steps})
        if path == "/webhook":  # incoming WhatsApp messages / statuses
            try:
                payload = self.read_json()
                for entry in payload.get("entry", []):
                    for change in entry.get("changes", []):
                        for msg in change.get("value", {}).get("messages", []):
                            handle_reply(normalize_phone(msg.get("from")))
            except Exception as e:
                print("webhook error:", e)
            return self.reply(200, {"ok": True})  # always 200 so Meta doesn't retry
        self.reply(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    if not LEAD_SECRET:
        raise SystemExit("Set LEAD_SECRET in .env")
    threading.Thread(target=scheduler, daemon=True).start()
    print(f"Listening on :{PORT} (dry run: {DRY_RUN})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
