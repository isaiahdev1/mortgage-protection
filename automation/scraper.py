"""
Fetches recently sold homes in Gilroy, Morgan Hill, San Martin, and Hollister
via the Zillw Real Estate API (RapidAPI). One API call covers the full area.
Outputs: gilroy_homebuyers.csv
"""

import csv
import os
import requests
from datetime import datetime

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")
HOST = "zillw-real-estate-api.p.rapidapi.com"
HEADERS = {
    "Content-Type": "application/json",
    "x-rapidapi-host": HOST,
    "x-rapidapi-key": RAPIDAPI_KEY,
}

# Bounding box covering Gilroy, Morgan Hill, San Martin, Hollister
BOUNDS = {
    "north_latitude": 37.20,
    "south_latitude": 36.80,
    "east_longitude": -121.35,
    "west_longitude": -121.75,
    "max_results": 100,
}

OUTPUT_FILE = "gilroy_homebuyers.csv"


def fetch_sold_homes() -> list[dict]:
    resp = requests.post(
        f"https://{HOST}/search-homes-sold/index.php",
        headers=HEADERS,
        json=BOUNDS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("data", {}).get("json", {}).get("searchResults", [])


def parse_property(result: dict) -> dict | None:
    try:
        prop = result.get("property", {})
        addr = prop.get("address", {})
        street = addr.get("streetAddress", "")
        if not street:
            return None
        price_data = prop.get("price", {})
        price = price_data.get("value", "") if isinstance(price_data, dict) else price_data
        return {
            "address": street,
            "sale_price": str(price),
            "city": addr.get("city", ""),
            "state": addr.get("state", "CA"),
            "zip": addr.get("zipcode", ""),
            "last_sold_date": prop.get("lastSoldDate", ""),
            "beds": prop.get("bedrooms", ""),
            "baths": prop.get("bathrooms", ""),
            "url": f"https://www.zillow.com/homedetails/{prop.get('zpid', '')}_zpid/",
            "scraped_at": datetime.now().strftime("%Y-%m-%d"),
        }
    except Exception:
        return None


def save_csv(records: list[dict], filename: str):
    if not records:
        print("No records to save.")
        return
    fields = list(records[0].keys())
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {len(records)} records to {filename}")


def run():
    if not RAPIDAPI_KEY:
        print("ERROR: Set RAPIDAPI_KEY environment variable.")
        return

    print("Fetching recently sold homes (Gilroy, Morgan Hill, San Martin, Hollister)...")
    results = fetch_sold_homes()
    print(f"  {len(results)} listings returned")

    records = []
    seen = set()
    for r in results:
        parsed = parse_property(r)
        if parsed and parsed["address"] not in seen:
            seen.add(parsed["address"])
            records.append(parsed)

    save_csv(records, OUTPUT_FILE)
    print(f"Done. {len(records)} unique homes.")


if __name__ == "__main__":
    run()
