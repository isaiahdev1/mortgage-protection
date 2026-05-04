#!/bin/bash
# Full automation pipeline — run this once a day (or set a cron job)
# Usage: bash run_pipeline.sh

set -e

cd "$(dirname "$0")"

echo "================================================"
echo "  Mortgage Protection Outreach Pipeline"
echo "  $(date)"
echo "================================================"

# Step 1: Scrape new Gilroy home sales
echo ""
echo "[1/3] Scraping new Gilroy homebuyers..."
python3 scraper.py

# Step 2: Enrich with contact info
echo ""
echo "[2/3] Enriching leads with contact info..."
python3 enrich.py

# Step 3: Send emails
echo ""
echo "[3/3] Sending outreach emails..."
python3 send_emails.py

echo ""
echo "Pipeline complete. Check sent_log.csv for results."
