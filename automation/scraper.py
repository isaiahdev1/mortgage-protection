"""
Scrapes recent home sales in Gilroy and surrounding areas from Redfin.
Outputs a CSV: address, sale_price, city, state, zip, url, scraped_at
"""

import csv
import json
import time
import random
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.redfin.com/",
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

TARGET_ZIPS = [
    ("95020", "Gilroy"),
    ("95021", "Gilroy"),
    ("95037", "Morgan Hill"),
    ("95038", "Morgan Hill"),
    ("95046", "San Martin"),
    ("95023", "Hollister"),
    ("95024", "Hollister"),
]

OUTPUT_FILE = "gilroy_homebuyers.csv"


def get_region_id(zip_code: str) -> str | None:
    """Look up Redfin region ID for a zip code."""
    try:
        resp = requests.get(
            "https://www.redfin.com/stingray/api/search",
            headers=HEADERS,
            params={"location": zip_code, "start": 0, "count": 5, "v": 2},
            timeout=15,
        )
        resp.raise_for_status()
        # Redfin prepends "{}&&" to JSON responses
        text = resp.text.lstrip("{}&&").strip()
        data = json.loads(text)
        for item in data.get("payload", {}).get("sections", []):
            for row in item.get("rows", []):
                if row.get("type") == 2:  # type 2 = zip code
                    return str(row.get("id", {}).get("tableId", ""))
    except Exception as e:
        print(f"  Could not get region ID for {zip_code}: {e}")
    return None


def fetch_sold_homes(region_id: str, zip_code: str) -> list[dict]:
    """Fetch recently sold homes for a region from Redfin."""
    try:
        resp = requests.get(
            "https://www.redfin.com/stingray/api/gis",
            headers=HEADERS,
            params={
                "al": 1,
                "num_homes": 100,
                "ord": "days-on-redfin-asc",
                "page_number": 1,
                "region_id": region_id,
                "region_type": 2,
                "sold_within_days": 90,
                "status": 9,
                "uipt": "1,2,3,4,5,6,7,8",
                "v": 8,
            },
            timeout=20,
        )
        resp.raise_for_status()
        text = resp.text.lstrip("{}&&").strip()
        data = json.loads(text)
        return data.get("payload", {}).get("homes", [])
    except Exception as e:
        print(f"  Error fetching sold homes for region {region_id}: {e}")
        return []


def parse_home(home: dict, city: str, zip_code: str) -> dict | None:
    try:
        info = home.get("homeData", {})
        address_info = info.get("addressInfo", {})
        street = address_info.get("formattedStreetLine", "")
        if not street:
            return None
        price_info = info.get("priceInfo", {})
        price = price_info.get("amount", "")
        url_path = info.get("url", "")
        return {
            "address": street,
            "sale_price": str(price),
            "city": city,
            "state": "CA",
            "zip": zip_code,
            "url": f"https://www.redfin.com{url_path}" if url_path else "",
            "scraped_at": datetime.now().strftime("%Y-%m-%d"),
        }
    except Exception:
        return None


def scrape_all() -> list[dict]:
    all_results = []
    seen = set()

    for zip_code, city in TARGET_ZIPS:
        print(f"\nScraping {city} ({zip_code})...")

        region_id = get_region_id(zip_code)
        if not region_id:
            print(f"  Skipping — could not resolve region ID")
            continue

        print(f"  Region ID: {region_id}")
        homes = fetch_sold_homes(region_id, zip_code)
        print(f"  Found {len(homes)} listings")

        for home in homes:
            parsed = parse_home(home, city, zip_code)
            if parsed and parsed["address"] not in seen:
                seen.add(parsed["address"])
                all_results.append(parsed)

        time.sleep(random.uniform(3, 6))

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
    print("Homebuyer Scraper — Gilroy & Surrounding Areas")
    print("=" * 48)
    results = scrape_all()
    save_csv(results, OUTPUT_FILE)
    print(f"\nDone. {len(results)} homes scraped.")
