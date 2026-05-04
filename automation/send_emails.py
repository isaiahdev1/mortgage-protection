"""
Reads personalized_leads.json and sends emails on a day 1 / 4 / 8 schedule.
Run this script daily — it figures out who gets what email today.

Setup:
  export GMAIL_APP_PASSWORD="your_16_char_app_password"

  Gmail App Password:
  myaccount.google.com → Security → 2-Step Verification → App Passwords
"""

import csv
import json
import os
import smtplib
import time
import random
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL = "kapadia.brokerage@gmail.com"
SENDER_NAME = "Isaac Kapadia"
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

INPUT_FILE = "personalized_leads.json"
LOG_FILE = "sent_log.csv"

DAILY_LIMIT = 40
DELAY_BETWEEN_EMAILS = (90, 180)

SIGNATURE = """
  <p style="font-size: 13px; color: #888888; line-height: 1.8; margin-top: 32px;">
    <strong>Isaac Kapadia</strong><br>
    Mortgage Protection Specialist · Kapadia Brokerage<br>
    <a href="https://kapadiabrokerage.com" style="color: #888888;">kapadiabrokerage.com</a><br>
    Bay Area, CA
  </p>
  <p style="font-size: 12px; color: #aaaaaa; line-height: 1.6; margin-top: 12px;">
    You received this because you recently purchased a home — a matter of public record.
    Reply STOP to unsubscribe.
  </p>
"""

def wrap_html(body_content: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<body style="font-family: Georgia, serif; background: #ffffff; color: #1a1a1a; max-width: 580px; margin: 0 auto; padding: 40px 24px;">
{body_content}
{SIGNATURE}
</body>
</html>"""


def build_email_1(lead: dict) -> tuple[str, str]:
    first = lead.get("first_name", "").strip() or "there"
    opener = lead.get("email1_opener", f"Congratulations on your recent home purchase, {first}.")
    price = lead.get("sale_price", "")
    price_str = f"${int(price):,}" if price.isdigit() else "your home"

    subject = f"Protecting your new home — quick question"
    body = wrap_html(f"""
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">Hi {first},</p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">{opener}</p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">
    My name is Isaac Kapadia. I'm a mortgage protection specialist with Kapadia Brokerage,
    and I work with new homeowners across the Bay Area to make sure the home they just bought
    stays in their family's hands no matter what.
  </p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">
    Mortgage protection is term life insurance tied to your loan — if something happens to you,
    the policy pays off the balance so your family never loses the house. Most homeowners pay
    <strong>$40–$70/month</strong>, and no medical exam is required.
  </p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 28px;">
    If you have 10 minutes this week, I'd love to show you what coverage would look like
    for {price_str} — completely free, no obligation.
  </p>
  <a href="mailto:{SENDER_EMAIL}?subject=Mortgage Protection Quote"
     style="display: inline-block; background: #1a1a1a; color: #ffffff; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-size: 15px; font-family: Arial, sans-serif; font-weight: 600;">
    Reply to Learn More
  </a>
""")
    return subject, body


def build_email_2(lead: dict) -> tuple[str, str]:
    first = lead.get("first_name", "").strip() or "there"
    opener = lead.get("email2_opener", f"Just following up on my last note, {first}.")

    subject = f"Re: Protecting your new home"
    body = wrap_html(f"""
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">Hi {first},</p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">{opener}</p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">
    Most people who lose their home to foreclosure after a death didn't plan to —
    they just never got around to the protection. At $50/month, mortgage protection is
    the most affordable thing a new homeowner can do.
  </p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 28px;">
    I can put together a personalized quote in under 10 minutes. Worth a quick conversation?
  </p>
  <a href="mailto:{SENDER_EMAIL}?subject=Mortgage Protection Quote"
     style="display: inline-block; background: #1a1a1a; color: #ffffff; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-size: 15px; font-family: Arial, sans-serif; font-weight: 600;">
    Let's Talk
  </a>
""")
    return subject, body


def build_email_3(lead: dict) -> tuple[str, str]:
    first = lead.get("first_name", "").strip() or "there"
    opener = lead.get("email3_opener", f"I'll keep this short, {first}.")

    subject = f"Last note from me, {first}"
    body = wrap_html(f"""
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">Hi {first},</p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px;">{opener}</p>
  <p style="font-size: 16px; line-height: 1.7; margin-bottom: 28px;">
    If protecting your home ever becomes a priority, I'm here.
    One conversation, no pressure.
  </p>
  <p style="font-size: 16px; line-height: 1.7;">
    Wishing you and your family all the best in the new place.
  </p>
""")
    return subject, body


EMAIL_BUILDERS = {
    1: build_email_1,
    2: build_email_2,
    3: build_email_3,
}
SEND_DAYS = {1: 0, 2: 3, 3: 7}  # days after first contact


def load_log() -> dict:
    """Returns {email: {email_1_sent: date, email_2_sent: date, email_3_sent: date}}"""
    log = {}
    try:
        with open(LOG_FILE, newline="") as f:
            for row in csv.DictReader(f):
                e = row["email"]
                if e not in log:
                    log[e] = {}
                log[e][f"email_{row['email_num']}_sent"] = row["sent_at"]
    except FileNotFoundError:
        pass
    return log


def log_sent(email: str, name: str, address: str, email_num: int, status: str):
    exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "name", "address", "email_num", "status", "sent_at"])
        if not exists:
            writer.writeheader()
        writer.writerow({
            "email": email,
            "name": name,
            "address": address,
            "email_num": email_num,
            "status": status,
            "sent_at": datetime.now().isoformat(),
        })


def get_due_emails(leads: list[dict], log: dict) -> list[tuple[dict, int]]:
    """Return list of (lead, email_num) that are due to send today."""
    due = []
    today = datetime.now().date()

    for lead in leads:
        email = lead.get("email", "")
        if not email:
            continue
        lead_log = log.get(email, {})

        for num in [1, 2, 3]:
            key = f"email_{num}_sent"
            if key in lead_log:
                continue  # already sent

            if num == 1:
                due.append((lead, 1))
                break

            prev_key = f"email_{num - 1}_sent"
            if prev_key not in lead_log:
                break  # previous not sent yet

            prev_date = datetime.fromisoformat(lead_log[prev_key]).date()
            days_needed = SEND_DAYS[num] - SEND_DAYS[num - 1]
            if (today - prev_date).days >= days_needed:
                due.append((lead, num))
            break

    return due


def send_emails():
    if not APP_PASSWORD:
        print("ERROR: Set GMAIL_APP_PASSWORD environment variable.")
        print("  myaccount.google.com → Security → App Passwords")
        return

    with open(INPUT_FILE) as f:
        leads = json.load(f)

    log = load_log()
    due = get_due_emails(leads, log)

    print(f"{len(due)} emails due today (limit: {DAILY_LIMIT})\n")

    sent_today = 0
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)

        for lead, email_num in due:
            if sent_today >= DAILY_LIMIT:
                print(f"\nDaily limit reached. Run again tomorrow.")
                break

            to_email = lead.get("email", "")
            name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
            subject, html = EMAIL_BUILDERS[email_num](lead)

            print(f"  Email {email_num} → {name} <{to_email}>")

            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
                msg["To"] = to_email
                msg.attach(MIMEText(html, "html"))

                server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
                log_sent(to_email, name, lead.get("address", ""), email_num, "sent")
                sent_today += 1
                print(f"    ✓ Sent ({sent_today}/{DAILY_LIMIT})")

            except Exception as e:
                print(f"    ✗ Failed: {e}")
                log_sent(to_email, name, lead.get("address", ""), email_num, f"failed: {e}")

            delay = random.randint(*DELAY_BETWEEN_EMAILS)
            if sent_today < DAILY_LIMIT:
                print(f"    Waiting {delay}s...")
                time.sleep(delay)

    print(f"\nDone. Sent {sent_today} emails today. Check {LOG_FILE} for full log.")


if __name__ == "__main__":
    send_emails()
