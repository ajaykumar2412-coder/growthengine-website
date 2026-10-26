# WhatsApp Lead Reminders

Google Sheet row → this server → WhatsApp template messages on a schedule you define
(Meta Cloud API). Reminders stop automatically when the lead replies.
Python 3.9+, no dependencies.

## 1. Meta setup
1. developers.facebook.com → create an app (Business) → add **WhatsApp**.
2. API Setup: copy the **Phone number ID**. Create a **permanent token** with a System User
   (Business Settings → System users → generate a token with `whatsapp_business_messaging`).
3. WhatsApp Manager → **Message templates**: create one template per step (names must match
   `sequence.json`). Variables `{{1}}`, `{{2}}`… correspond to `params` in order.

## 2. Configure
```
cp .env.example .env      # fill values; keep DRY_RUN=1 for first test
```
Edit `sequence.json`. Each step has its own delay (minutes after the lead arrives), template,
language, and params. A param like `{service}` pulls that lead's **Service** column from the sheet
(headers are lowercased, spaces → `_`).

## 3. Run / deploy
```
python3 server.py
```
Deploy to any host with a public HTTPS URL (Railway, Render, a VPS). Keep `leads.db` on persistent disk.

## 4. Connect the Google Sheet
Sheet → Extensions → Apps Script → paste `google-sheet.gs`, set `SERVER_URL` (`https://…/lead`)
and `SECRET`, then run `setup()` once and approve the permissions. The sheet is checked every minute, and each new row
gets a **WA Status** cell. Clear that cell to resend a row.

## 5. Stop on reply (webhook)
App → WhatsApp → Configuration → Webhook: URL `https://…/webhook`, verify token = `WA_VERIFY_TOKEN`,
subscribe to **messages**.

## Check status
`curl https://…/leads -H "X-Secret: <LEAD_SECRET>"`
