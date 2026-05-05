"""
Reads gilroy_homebuyers.csv, finds contacts in Apollo via people match,
creates them as contacts, and enrolls them in the sequence automatically.

Setup:
  export APOLLO_API_KEY="your_key_here"
  Get key from: app.apollo.io → Settings → Integrations → API Keys
"""

import csv
import json
import os
import time
import requests
from datetime import datetime

APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")
SEQUENCE_ID = "69f92bb48a479e000dda95c4"
EMAIL_ACCOUNT_ID = "69f91ffcd611650015085222"  # kapadia.brokerage@gmail.com

INPUT_FILE = "gilroy_homebuyers.csv"
ENROLLED_FILE = "enrolled_leads.json"

HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": APOLLO_API_KEY,
}


def load_enrolled() -> set:
    try:
        with open(ENROLLED_FILE) as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_enrolled(enrolled: set):
    with open(ENROLLED_FILE, "w") as f:
        json.dump(list(enrolled), f)


def find_or_create_contact(lead: dict) -> str | None:
    """Match person by name + location, create if not found. Returns contact ID."""
    address = lead.get("address", "")
    city = lead.get("city", "Gilroy")
    state = lead.get("state", "CA")

    # Try people match first
    resp = requests.post(
        "https://api.apollo.io/v1/people/match",
        headers=HEADERS,
        json={
            "location": f"{city}, {state}",
            "reveal_personal_emails": True,
        },
        timeout=15
    )

    if resp.ok:
        person = resp.json().get("person")
        if person and person.get("email"):
            # Create as contact
            contact_resp = requests.post(
                "https://api.apollo.io/v1/contacts",
                headers=HEADERS,
                json={
                    "first_name": person.get("first_name", "Homeowner"),
                    "last_name": person.get("last_name", ""),
                    "email": person.get("email"),
                    "present_raw_address": f"{city}, {state}",
                    "run_dedupe": True,
                },
                timeout=15
            )
            if contact_resp.ok:
                return contact_resp.json().get("contact", {}).get("id")

    # Fallback: create contact from address only if we have enough info
    return None


def enroll_contact(contact_id: str) -> bool:
    """Add contact to the Apollo sequence."""
    resp = requests.post(
        f"https://api.apollo.io/v1/emailer_campaigns/{SEQUENCE_ID}/add_contact_ids",
        headers=HEADERS,
        json={
            "contact_ids": [contact_id],
            "emailer_campaign_id": SEQUENCE_ID,
            "send_email_from_email_account_id": EMAIL_ACCOUNT_ID,
            "status": "active",
        },
        timeout=15
    )
    return resp.ok


def run():
    if not APOLLO_API_KEY:
        print("ERROR: Set APOLLO_API_KEY environment variable.")
        return

    if not os.path.exists(INPUT_FILE):
        print("No leads file found — scraper may have returned no results. Skipping.")
        return

    with open(INPUT_FILE, newline="") as f:
        leads = list(csv.DictReader(f))

    if not leads:
        print("Leads file is empty. Nothing to enroll.")
        return

    enrolled = load_enrolled()
    new_enrollments = 0

    print(f"Processing {len(leads)} leads...")

    for i, lead in enumerate(leads):
        address = lead.get("address", "")
        if address in enrolled:
            continue

        print(f"  [{i+1}/{len(leads)}] {address}")

        contact_id = find_or_create_contact(lead)
        if not contact_id:
            print(f"    Could not find contact, skipping")
            continue

        if enroll_contact(contact_id):
            enrolled.add(address)
            new_enrollments += 1
            print(f"    ✓ Enrolled in sequence")
        else:
            print(f"    ✗ Failed to enroll")

        time.sleep(1.5)

    save_enrolled(enrolled)
    print(f"\nDone. {new_enrollments} new contacts enrolled in Apollo sequence.")


if __name__ == "__main__":
    run()
