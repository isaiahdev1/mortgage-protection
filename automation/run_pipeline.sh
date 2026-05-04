#!/bin/bash
# Full automation pipeline — run this once a day
# Usage: bash run_pipeline.sh

set -e
cd "$(dirname "$0")"

echo "================================================"
echo "  Kapadia Brokerage — Outreach Pipeline"
echo "  $(date)"
echo "================================================"

echo ""
echo "[1/4] Scraping new Gilroy homebuyers..."
python3 scraper.py

echo ""
echo "[2/4] Enriching leads with contact info..."
python3 enrich.py

echo ""
echo "[3/4] Personalizing emails with Claude AI..."
python3 personalize.py

echo ""
echo "[4/4] Sending emails..."
python3 send_emails.py

echo ""
echo "Pipeline complete. Check sent_log.csv for results."
