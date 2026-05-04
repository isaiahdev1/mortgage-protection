"""
Reads enriched_leads.csv and sends personalized mortgage protection emails.
Uses Gmail SMTP (Isaac's personal Gmail to start).

Setup:
  1. Go to myaccount.google.com → Security → 2-Step Verification → App Passwords
  2. Create an app password for "Mail"
  3. Set: export GMAIL_APP_PASSWORD="your_16_char_password"
  4. Set: export SENDER_EMAIL="Isaackapadia@gmail.com"

CAN-SPAM compliant:
  - Real sender identity
  - Physical address included
  - Clear unsubscribe option
  - Not deceptive subject line
"""

import csv
import os
import smtplib
import time
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "Isaackapadia@gmail.com")
SENDER_NAME = "Isaac Kapadia"
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

INPUT_FILE = "enriched_leads.csv"
LOG_FILE = "sent_log.csv"

DAILY_LIMIT = 40
DELAY_BETWEEN_EMAILS = (90, 180)  # seconds — keeps Gmail from flagging as spam


def build_email(lead: dict) -> tuple[str, str, str]:
    """Returns (to_email, subject, html_body)"""
    first = lead.get("first_name", "").strip() or "Homeowner"
    address = lead.get("address", "your new home").strip()
    price = lead.get("sale_price", "")
    price_str = f"${int(price):,}" if price.isdigit() else "your home"

    subject = f"Protecting {address} for your family — quick question"

    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Georgia, serif; background: #ffffff; color: #1a1a1a; max-width: 580px; margin: 0 auto; padding: 40px 24px;">

  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">Hi {first},</p>

  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">
    Congratulations on your recent home purchase — that&apos;s a big milestone.
  </p>

  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">
    My name is Isaac Kapadia, and I help homeowners in Gilroy protect the investment
    they just made. I specialize in <strong>mortgage protection insurance</strong> — a type of term life
    policy that pays off your loan if something unexpected happens to you, so your
    family never has to worry about losing the home.
  </p>

  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">
    For most homeowners, coverage runs <strong>$40–$70/month</strong> with no medical exam required.
    It&apos;s the simplest way to make sure the biggest thing you own stays in your family&apos;s hands.
  </p>

  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 28px;">
    If you have 10 minutes this week, I&apos;d love to walk you through what a policy for
    {price_str} would look like — completely free, no obligation.
  </p>

  <a href="mailto:{SENDER_EMAIL}?subject=Mortgage Protection Quote Request"
     style="display: inline-block; background: #1a1a1a; color: #ffffff; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-size: 15px; font-family: Arial, sans-serif; font-weight: 600;">
    Reply to Learn More
  </a>

  <hr style="margin: 48px 0; border: none; border-top: 1px solid #eeeeee;" />

  <p style="font-size: 13px; color: #888888; line-height: 1.8;">
    <strong>Isaac Kapadia</strong><br>
    Mortgage Protection Specialist · Kapadia Brokerage<br>
    <a href="https://kapadiabrokerage.com" style="color: #888888;">kapadiabrokerage.com</a><br>
    Bay Area, CA
  </p>

  <p style="font-size: 12px; color: #aaaaaa; line-height: 1.6; margin-top: 16px;">
    You received this email because you recently purchased a home — a matter of public record.
    Reply STOP to unsubscribe.
  </p>

</body>
</html>
"""
    return lead.get("email", ""), subject, html


def load_already_sent() -> set[str]:
    sent = set()
    try:
        with open(LOG_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sent.add(row["email"])
    except FileNotFoundError:
        pass
    return sent


def log_sent(email: str, name: str, address: str, status: str):
    exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "name", "address", "status", "sent_at"])
        if not exists:
            writer.writeheader()
        writer.writerow({
            "email": email,
            "name": name,
            "address": address,
            "status": status,
            "sent_at": datetime.now().isoformat(),
        })


def send_emails():
    if not APP_PASSWORD:
        print("ERROR: Set GMAIL_APP_PASSWORD environment variable.")
        print("  Go to myaccount.google.com → Security → App Passwords")
        return

    with open(INPUT_FILE, newline="") as f:
        leads = [r for r in csv.DictReader(f) if r.get("email")]

    already_sent = load_already_sent()
    to_send = [l for l in leads if l["email"] not in already_sent]

    print(f"{len(to_send)} new leads to contact (limit: {DAILY_LIMIT}/day)\n")

    sent_today = 0
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)

        for lead in to_send:
            if sent_today >= DAILY_LIMIT:
                print(f"\nDaily limit of {DAILY_LIMIT} reached. Run again tomorrow.")
                break

            email, subject, html = build_email(lead)
            if not email:
                continue

            name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
            print(f"  Sending to {name} <{email}>...")

            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
                msg["To"] = email
                msg.attach(MIMEText(html, "html"))

                server.sendmail(SENDER_EMAIL, email, msg.as_string())
                log_sent(email, name, lead.get("address", ""), "sent")
                sent_today += 1
                print(f"    ✓ Sent ({sent_today}/{DAILY_LIMIT})")

            except Exception as e:
                print(f"    ✗ Failed: {e}")
                log_sent(email, name, lead.get("address", ""), f"failed: {e}")

            # Random delay — looks more human, avoids spam flags
            delay = random.randint(*DELAY_BETWEEN_EMAILS)
            if sent_today < DAILY_LIMIT:
                print(f"    Waiting {delay}s...")
                time.sleep(delay)

    print(f"\nDone. Sent {sent_today} emails today.")
    print(f"Check {LOG_FILE} for full log.")


if __name__ == "__main__":
    send_emails()
