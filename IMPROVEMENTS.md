# NewsTailor — Improvement Notes

This document covers what was fixed, what can be improved next, and what to think about at scale.

---

## What was fixed in this pass

| # | File | Issue | Fix |
|---|------|--------|-----|
| 1 | `test.py` → `email_service.py` | Misleading module name | Renamed; both callers updated |
| 2 | `send_newsletters.py` | Delivered to ALL users including unsubscribed | Now filters `isSubscribed: True` |
| 3 | `send_newsletters.py` | `fetch_fresh_news()` called at import time | Moved inside `start_news_delivery()` |
| 4 | `fetch_news.py` | `fetch_fresh_news()` called at import time again (line 30) | Removed |
| 5 | `send_newsletters.py` | KeyError if user has a category absent from scored collection | `cached_news.get(cat, [])` with skip |
| 6 | `email_service.py` | New SMTP connection opened per email — expensive for bulk sends | `send_bulk_news_emails()` reuses one connection across all recipients |
| 7 | `email_service.py` | No retry on transient failures | Exponential backoff (2 s → 4 s → 8 s) with reconnect on dropped connection |
| 8 | `email_service.py` | `print()` used for errors | Replaced with `logging` throughout |
| 9 | `email_service.py` | Bare HTML fragments with no email structure | Proper `<!DOCTYPE html>` wrapper with inline CSS |
| 10 | `server.py` | OTP email send result ignored — OTP inserted even when email failed | Returns 500-style error if `send_otp_email` returns `False` |
| 11 | `server.py` | `email` parameter in `create_email_data` was unused | Removed |
| 12 | `server.py` | Unused `mailjet_rest` import | Removed |
| 13 | `fetch_news.py` | Unused `datetime`, `errors`, `refined_collection` imports | Removed |

---

## Gmail SMTP limits (personal account)

| Limit | Value |
|-------|-------|
| Emails per day | 500 |
| Recipients per message | 500 |
| Sending rate | ~20 emails/minute sustained |

At ~500 users you will hit the daily cap. The single-connection bulk sender buys you time, but Gmail is not a reliable transactional channel at scale.

---

## Short-term improvements (< 1 day each)

### 1. Rate limiting on `/register`
Right now anyone can hammer `/register` to burn your 500-email quota in minutes.
```python
# add slowapi or a simple in-memory token bucket
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
@app.post("/register")
@limiter.limit("5/minute")
def register_user(...):
```

### 2. OTP expiry enforcement
`verify-otp` checks the OTP value but never checks `expires_at`. Add:
```python
if existing_request["expires_at"] < datetime.now(timezone.utc):
    return {"message": "OTP expired"}
```

### 3. Enable Python logging in `main.py`
None of the `log.info/warning/error` calls in `email_service.py` will output anything until a handler is configured:
```python
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
```

### 4. Move the hardcoded JWT secret to `.env`
`SECRET_KEY` in `backend/server.py` is a literal string committed to git. Move it:
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
```

### 5. Sender name in From header
`email_service.py` already sets `"NewsTailor <you@gmail.com>"` — make sure `EMAIL` is set correctly in `.env`.

---

## Medium-term improvements

### Switch to a transactional email provider
When you exceed ~200 active users, replace Gmail SMTP with one of:

| Provider | Free tier | Why |
|----------|-----------|-----|
| **Resend** | 3 000/month | Already have an API key in `.env` |
| **SendGrid** | 100/day free, cheap paid | Industry standard, good deliverability |
| **AWS SES** | 62 000/month from EC2 | Cheapest at scale ($0.10 per 1 000) |

All three have Python SDKs and drop-in replacements for `send_otp_email` / `send_bulk_news_emails`.

### Async delivery with a task queue
`start_news_delivery()` currently runs synchronously inside `main.py`, blocking until every email is sent.

```
main.py
  run_pipeline()        # already slow
  start_news_delivery() # then this — potentially minutes
```

Replace with a task queue so delivery happens in the background:

```python
# Celery + Redis (or rq for something simpler)
from celery import Celery
app = Celery("newstailorer", broker="redis://localhost:6379/0")

@app.task
def deliver_newsletter():
    start_news_delivery()
```

Schedule it with Celery Beat on a cron instead of running `main.py` directly.

### Per-delivery status tracking
Add a `delivery_log` collection to MongoDB so you know who got what and when:
```python
{
  "email": "user@example.com",
  "sent_at": ISODate(...),
  "status": "sent" | "failed",
  "run_id": ObjectId(...)   # link to pipeline_info
}
```
This also lets you skip users who already received today's digest if the job crashes halfway.

---

## Long-term / scale improvements

### Move to an email template engine
The current inline f-string HTML is fragile. Use **Jinja2** templates:
```
delivery/
  templates/
    newsletter.html
    otp.html
```
```python
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader("delivery/templates"))
html = env.get_template("newsletter.html").render(user=user, articles=articles)
```

### Personalisation signals
The scoring in `score_math.py` is global. At scale, track per-user click/open data and weight scores per user (collaborative filtering or simple click-through rate per category).

### Unsubscribe link in every email
CAN-SPAM / GDPR require a one-click unsubscribe. Generate a signed token:
```python
import hmac, hashlib
token = hmac.new(SECRET_KEY.encode(), user_email.encode(), hashlib.sha256).hexdigest()
unsubscribe_url = f"https://yourdomain.com/unsubscribe?token={token}"
```
Add the URL to `_wrap_html()` in `email_service.py`.

### Move secrets out of `.env` into a secrets manager
For anything beyond a personal project: AWS Secrets Manager, HashiCorp Vault, or even GitHub Actions secrets for CI. The current `.env` contains live MongoDB credentials and a Gmail app password.
