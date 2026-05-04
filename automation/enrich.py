"""
Takes gilroy_homebuyers.csv, looks up contact info via Apollo.io (free tier).
Outputs enriched_leads.csv with email + phone appended.

Setup:
  1. Sign up free at apollo.io
  2. Go to Settings → Integrations → API Keys → copy your key
  3. Set: export APOLLO_API_KEY="your_key_here"
"""

import csv
import os
import time
import requests

APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")
INPUT_FILE = "gilroy_homebuyers.csv"
OUTPUT_FILE = "enriched_leads.csv"

APOLLO_PEOPLE_SEARCH = "https://api.apollo.io/v1/mixed_people/search"
APOLLO_ENRICH = "https://api.apollo.io/v1/people/match"


def enrich_by_address(address: str, city: str = "Gilroy", state: str = "CA") -> dict:
    """Try to find a person from their property address via Apollo."""
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY,
    }
    payload = {
        "location_city_with_state_or_zip": f"{city}, {state}",
        "page": 1,
        "per_page": 3,
    }
    try:
        resp = requests.post(APOLLO_PEOPLE_SEARCH, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        people = data.get("people", [])
        if people:
            p = people[0]
            return {
                "first_name": p.get("first_name", ""),
                "last_name": p.get("last_name", ""),
                "email": p.get("email", ""),
                "phone": p.get("sanitized_phone", ""),
                "linkedin": p.get("linkedin_url", ""),
            }
    except Exception as e:
        print(f"  Apollo error for {address}: {e}")
    return {"first_name": "", "last_name": "", "email": "", "phone": "", "linkedin": ""}


def enrich_leads():
    if not APOLLO_API_KEY:
        print("ERROR: Set your APOLLO_API_KEY environment variable first.")
        print("  export APOLLO_API_KEY='your_key_here'")
        return

    with open(INPUT_FILE, newline="") as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    print(f"Enriching {len(leads)} leads from Apollo.io...")
    enriched = []

    for i, lead in enumerate(leads):
        print(f"  [{i+1}/{len(leads)}] {lead['address']}")
        contact = enrich_by_address(lead["address"], lead.get("city", "Gilroy"), lead.get("state", "CA"))
        enriched.append({**lead, **contact})
        time.sleep(1.2)  # stay within free tier rate limits

    # Write output
    if enriched:
        fields = list(enriched[0].keys())
        with open(OUTPUT_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(enriched)
        print(f"\nSaved {len(enriched)} enriched leads to {OUTPUT_FILE}")
        print("Run send_emails.py next.")
    else:
        print("No enriched leads to save.")


if __name__ == "__main__":
    enrich_leads()
