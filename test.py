from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("char_16")

def send_otp_email(to_email: str, html):
    msg = MIMEMultipart("alternative")

    msg["Subject"] = "👋, From NewsTailor"
    msg["From"] = EMAIL
    msg["To"] = to_email  # single or comma-separated

    # Attach HTML
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
            print("Email sent successfully")

    except Exception as e:
        print("Error:", e)
        
def send_news_email(to_email, html):
    msg = MIMEMultipart("alternative")

    msg["Subject"] = "👋 NewsTailor First Email"
    msg["From"] = EMAIL
    msg["To"] = to_email  # single or comma-separated

    # Attach HTML
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
            print("Email sent successfully")

    except Exception as e:
        print("Error:", e)
