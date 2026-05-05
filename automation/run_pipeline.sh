#!/bin/bash
# Kapadia Brokerage — Daily Automation Pipeline
# Runs every morning at 8am via cron

set -e
cd "$(dirname "$0")"

# Load env vars
source ~/.zshrc 2>/dev/null || true

echo "================================================"
echo "  Kapadia Brokerage — Daily Pipeline"
echo "  $(date)"
echo "================================================"

echo ""
echo "[1/3] Scraping new Gilroy homebuyers..."
python3 scraper.py

echo ""
echo "[2/3] Enrolling leads into Apollo sequence..."
python3 apollo_enroll.py

echo ""
echo "Pipeline complete. Leads enrolled in Apollo."
echo "Apollo handles all email sending automatically."
