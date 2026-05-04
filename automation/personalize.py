"""
Takes enriched_leads.csv, calls Claude API to generate 3 personalized
email openers per lead, saves to personalized_leads.json.

Setup:
  export ANTHROPIC_API_KEY="your_key_here"

Cost: ~$0.001 per lead (Haiku model) — essentially free.
"""

import csv
import json
import os
import time
from datetime import datetime
import anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
INPUT_FILE = "enriched_leads.csv"
OUTPUT_FILE = "personalized_leads.json"


def generate_emails(client: anthropic.Anthropic, lead: dict) -> dict:
    first = lead.get("first_name", "").strip() or "there"
    address = lead.get("address", "your home").strip()
    price = lead.get("sale_price", "")
    price_str = f"${int(price):,}" if price.isdigit() else "your home"
    scraped_at = lead.get("scraped_at", "recently")

    prompt = f"""You are writing cold outreach emails for Isaac Kapadia, a mortgage protection specialist at Kapadia Brokerage in the Bay Area.

Lead details:
- First name: {first}
- Address: {address}
- Purchase price: {price_str}
- Purchase date: {scraped_at}

Write 3 personalized email openers. Each is 2 sentences max. Warm, natural, not salesy.
Reference their specific address or price naturally — make it feel like Isaac actually looked them up.

Return ONLY valid JSON in this exact format:
{{
  "email1_opener": "...",
  "email2_opener": "...",
  "email3_opener": "..."
}}

email1_opener: Congratulate them on the specific purchase, reference address or price.
email2_opener: Reference how long ago they closed + the loan size they're carrying.
email3_opener: Short warm final note referencing their home one last time — feels like a friend."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def personalize_leads():
    if not ANTHROPIC_API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable.")
        return

    with open(INPUT_FILE, newline="") as f:
        leads = [r for r in csv.DictReader(f) if r.get("email")]

    # Load existing to avoid re-processing
    existing = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            existing = {r["email"]: r for r in json.load(f)}

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    results = list(existing.values())
    new_count = 0

    for i, lead in enumerate(leads):
        email = lead.get("email", "")
        if email in existing:
            continue

        print(f"  [{i+1}/{len(leads)}] Personalizing for {lead.get('first_name', '')} — {lead.get('address', '')}...")

        try:
            openers = generate_emails(client, lead)
            results.append({**lead, **openers, "personalized_at": datetime.now().isoformat()})
            new_count += 1
            print(f"    ✓ Done")
        except Exception as e:
            print(f"    ✗ Failed: {e}")

        time.sleep(0.3)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nPersonalized {new_count} new leads. Total: {len(results)} in {OUTPUT_FILE}")
    print("Run send_emails.py next.")


if __name__ == "__main__":
    personalize_leads()
