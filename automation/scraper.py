"""
Fetches recently sold homes in Gilroy and surrounding areas via Zillow API (RapidAPI).
Outputs a CSV: address, sale_price, city, state, zip, url, scraped_at
"""

import csv
import json
import os
import time
import requests
from datetime import datetime

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")

HEADERS = {
    "x-rapidapi-host": "zillow-com1.p.rapidapi.com",
    "x-rapidapi-key": RAPIDAPI_KEY,
}

TARGET_LOCATIONS = [
    ("Gilroy, CA", "Gilroy"),
    ("Morgan Hill, CA", "Morgan Hill"),
    ("San Martin, CA", "San Martin"),
    ("Hollister, CA", "Hollister"),
]

OUTPUT_FILE = "gilroy_homebuyers.csv"


def fetch_recently_sold(location: str) -> list[dict]:
    try:
        resp = requests.get(
            "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch",
            headers=HEADERS,
            params={
                "location": location,
                "status_type": "RecentlySold",
                "home_type": "Houses,Townhomes,Condos",
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("props", [])
    except Exception as e:
        print(f"  Error fetching {location}: {e}")
        return []


def parse_property(prop: dict, city: str) -> dict | None:
    try:
        address = prop.get("address", "")
        if not address:
            return None
        price = prop.get("price", "")
        detail_url = prop.get("detailUrl", "")
        zip_code = prop.get("zipCode", "")
        return {
            "address": address,
            "sale_price": str(price).replace(",", "").replace("$", ""),
            "city": city,
            "state": "CA",
            "zip": zip_code,
            "url": f"https://www.zillow.com{detail_url}" if detail_url else "",
            "scraped_at": datetime.now().strftime("%Y-%m-%d"),
        }
    except Exception:
        return None


def scrape_all() -> list[dict]:
    if not RAPIDAPI_KEY:
        print("ERROR: Set RAPIDAPI_KEY environment variable.")
        return []

    all_results = []
    seen = set()

    for location, city in TARGET_LOCATIONS:
        print(f"\nFetching recently sold in {city}...")
        props = fetch_recently_sold(location)
        print(f"  {len(props)} results")

        for prop in props:
            parsed = parse_property(prop, city)
            if parsed and parsed["address"] not in seen:
                seen.add(parsed["address"])
                all_results.append(parsed)

        time.sleep(1)

    return all_results


def save_csv(records: list[dict], filename: str):
    if not records:
        print("No records to save.")
        return
    fields = list(records[0].keys())
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    print(f"\nSaved {len(records)} records to {filename}")


if __name__ == "__main__":
    print("Zillow Recently Sold — Gilroy & Surrounding Areas")
    print("=" * 50)
    results = scrape_all()
    save_csv(results, OUTPUT_FILE)
    print(f"\nDone. {len(results)} homes found.")
