"""
Scrapes recent home sales in Gilroy, CA from Zillow's public data.
Outputs a CSV: name, address, sale_price, sale_date, zip
"""

import csv
import json
import time
import random
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

GILROY_ZIPS = ["95020", "95021", "95037", "95038", "95046", "95023", "95024"]

OUTPUT_FILE = "gilroy_homebuyers.csv"


def fetch_zillow_recently_sold(zip_code: str, page: int = 1) -> list[dict]:
    """Fetch recently sold homes in a zip code from Zillow's search API."""
    url = "https://www.zillow.com/search/GetSearchPageState.htm"
    params = {
        "searchQueryState": json.dumps({
            "pagination": {"currentPage": page},
            "isMapVisible": False,
            "filterState": {
                "rs": {"value": True},          # recently sold
                "fsba": {"value": False},
                "fsbo": {"value": False},
                "nc": {"value": False},
                "cmsn": {"value": False},
                "auc": {"value": False},
                "fore": {"value": False},
                "doz": {"value": "12"},         # sold in last 12 months
            },
            "isListVisible": True,
            "mapZoom": 13,
        }),
        "wants": '{"cat1":["listResults"],"cat2":["total"]}',
        "requestId": str(random.randint(1, 99)),
        "qs": f"{zip_code} Gilroy CA",
    }

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("cat1", {}).get("searchResults", {}).get("listResults", [])
        return results
    except Exception as e:
        print(f"  Error fetching page {page} for zip {zip_code}: {e}")
        return []


def parse_listing(listing: dict) -> dict | None:
    """Extract useful fields from a Zillow listing object."""
    try:
        address = listing.get("address", "")
        price = listing.get("price", "")
        sold_date = listing.get("brokerName", "") or listing.get("zestimate", "")

        # Zillow doesn't always return owner name — we get address + price
        return {
            "address": address,
            "sale_price": str(price).replace(",", "").replace("$", ""),
            "city": "Gilroy",
            "state": "CA",
            "zpid": listing.get("zpid", ""),
            "url": f"https://www.zillow.com{listing.get('detailUrl', '')}",
            "scraped_at": datetime.now().strftime("%Y-%m-%d"),
        }
    except Exception:
        return None


def scrape_gilroy(max_pages: int = 5) -> list[dict]:
    """Main scrape loop across all Gilroy zip codes."""
    all_results = []
    seen = set()

    for zip_code in GILROY_ZIPS:
        print(f"\nScraping zip {zip_code}...")
        for page in range(1, max_pages + 1):
            print(f"  Page {page}...")
            listings = fetch_zillow_recently_sold(zip_code, page)
            if not listings:
                print(f"  No more results for zip {zip_code}")
                break

            for listing in listings:
                zpid = listing.get("zpid")
                if zpid in seen:
                    continue
                seen.add(zpid)
                parsed = parse_listing(listing)
                if parsed:
                    all_results.append(parsed)

            time.sleep(random.uniform(2.5, 4.5))  # respectful delay

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
    print("Gilroy Homebuyer Scraper")
    print("=" * 40)
    results = scrape_gilroy(max_pages=5)
    save_csv(results, OUTPUT_FILE)
    print(f"\nDone. Run enrich.py next to find contact info.")
