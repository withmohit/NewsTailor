import smtplib
import logging
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("char_16")

_RETRY_ATTEMPTS = 3
_RETRY_DELAYS = [2, 4, 8]  # seconds


def _build_message(to_email: str, subject: str, html: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"NewsTailor <{EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))
    return msg


def _wrap_html(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 24px auto; background: #fff; border-radius: 8px; padding: 32px; }}
    h1 {{ color: #1a1a1a; font-size: 22px; margin-bottom: 4px; }}
    h3 {{ color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 6px; margin-top: 28px; text-transform: capitalize; }}
    a {{ color: #0070f3; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    p {{ color: #555; line-height: 1.6; margin: 8px 0; }}
    .otp {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0070f3;
             background: #f0f7ff; border-radius: 6px; padding: 12px 24px;
             display: inline-block; margin: 16px 0; }}
    .footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid #eee;
               font-size: 12px; color: #999; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    {body}
    <div class="footer">
      You are receiving this because you subscribed to NewsTailor.<br>
      To unsubscribe, sign in and visit your account settings.
    </div>
  </div>
</body>
</html>"""


def _connect() -> smtplib.SMTP:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    return server


def send_otp_email(to_email: str, html: str) -> bool:
    msg = _build_message(to_email, "Your NewsTailor verification code", _wrap_html(html))
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            with _connect() as server:
                server.send_message(msg)
            log.info("OTP email sent to %s", to_email)
            return True
        except smtplib.SMTPAuthenticationError:
            log.error("Gmail authentication failed — check EMAIL and char_16 in .env")
            return False
        except Exception as e:
            delay = _RETRY_DELAYS[attempt] if attempt < len(_RETRY_DELAYS) else 8
            log.warning("OTP email attempt %d failed for %s: %s — retrying in %ds", attempt + 1, to_email, e, delay)
            time.sleep(delay)
    log.error("All retries exhausted for OTP email to %s", to_email)
    return False


def send_news_email(to_email: str, html: str) -> bool:
    """Send a single newsletter. Prefer send_bulk_news_emails for multiple recipients."""
    msg = _build_message(to_email, "Your NewsTailor digest", _wrap_html(html))
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            with _connect() as server:
                server.send_message(msg)
            log.info("News email sent to %s", to_email)
            return True
        except smtplib.SMTPAuthenticationError:
            log.error("Gmail authentication failed — check EMAIL and char_16 in .env")
            return False
        except Exception as e:
            delay = _RETRY_DELAYS[attempt] if attempt < len(_RETRY_DELAYS) else 8
            log.warning("News email attempt %d failed for %s: %s — retrying in %ds", attempt + 1, to_email, e, delay)
            time.sleep(delay)
    log.error("All retries exhausted for news email to %s", to_email)
    return False


def send_bulk_news_emails(recipients: list[tuple[str, str]]) -> dict[str, list]:
    """
    Send newsletter to many recipients over a single SMTP connection.

    recipients: list of (to_email, html_body) tuples
    Returns {"sent": [emails], "failed": [emails]}
    """
    results: dict[str, list] = {"sent": [], "failed": []}

    if not recipients:
        return results

    server = None

    def reconnect():
        nonlocal server
        if server:
            try:
                server.quit()
            except Exception:
                pass
        server = _connect()

    try:
        reconnect()
    except Exception as e:
        log.error("Cannot establish initial SMTP connection: %s", e)
        results["failed"] = [email for email, _ in recipients]
        return results

    for to_email, html in recipients:
        msg = _build_message(to_email, "Your NewsTailor digest", _wrap_html(html))
        sent = False
        for attempt in range(_RETRY_ATTEMPTS):
            try:
                server.send_message(msg)
                results["sent"].append(to_email)
                log.info("Sent digest to %s", to_email)
                sent = True
                break
            except smtplib.SMTPServerDisconnected:
                log.warning("Connection dropped, reconnecting (attempt %d)...", attempt + 1)
                try:
                    reconnect()
                except Exception as e:
                    log.error("Reconnect failed: %s", e)
                    break
            except smtplib.SMTPRecipientsRefused:
                log.warning("Recipient refused by server: %s", to_email)
                break
            except smtplib.SMTPException as e:
                log.warning("SMTP error for %s on attempt %d: %s", to_email, attempt + 1, e)
                break

        if not sent:
            results["failed"].append(to_email)

    try:
        server.quit()
    except Exception:
        pass

    log.info("Bulk send complete — sent: %d, failed: %d", len(results["sent"]), len(results["failed"]))
    return results
