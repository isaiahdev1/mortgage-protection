# Mortgage Protection Outreach Automation

## One-time setup

### 1. Install Python dependencies
```bash
pip3 install requests
```

### 2. Apollo.io (free contact enrichment)
1. Sign up at [apollo.io](https://app.apollo.io/#/sign-up) — free
2. Settings → Integrations → API Keys → Create Key
3. Run: `export APOLLO_API_KEY="your_key_here"`

### 3. Gmail App Password
1. Go to [myaccount.google.com](https://myaccount.google.com) → Security
2. Enable 2-Step Verification if not already on
3. App Passwords → Create → name it "Mortgage Outreach"
4. Copy the 16-character password
5. Run: `export GMAIL_APP_PASSWORD="your_16_char_password"`

## Running the pipeline

```bash
cd automation/
bash run_pipeline.sh
```

This runs all 3 steps:
1. **scraper.py** — finds recently sold homes in Gilroy (zip 95020, 95021)
2. **enrich.py** — looks up email/phone via Apollo.io free tier
3. **send_emails.py** — sends 40 personalized emails/day via Gmail

## Automate daily with cron (optional)

Run at 9am every weekday:
```bash
crontab -e
# Add this line:
0 9 * * 1-5 cd /path/to/automation && bash run_pipeline.sh >> pipeline.log 2>&1
```

## Output files
- `gilroy_homebuyers.csv` — scraped addresses
- `enriched_leads.csv` — with email/phone appended
- `sent_log.csv` — every email sent, status, timestamp
