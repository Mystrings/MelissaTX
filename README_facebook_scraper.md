# Facebook Group Selenium Scraper (best-effort)

This repository file contains a Selenium-based scraper to extract posts and comments from a Facebook Group and produce categorized recommendations.

Important notes:
- Facebook actively defends against automated scraping. Use this script only for groups you administrate or have permission to scrape and only for lawful/ethical uses.
- Preferred method: point the script at a `--profile-dir` that contains a logged-in Chrome/Chromium profile. This avoids putting credentials in scripts and reduces login friction.
- Headless mode may be detected by Facebook; non-headless is more reliable.

Quick start
1. Create a Python virtualenv and install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the scraper (recommended with profile reuse):

```bash
python3 facebook_selenium_scraper.py \
  --group-url "https://www.facebook.com/groups/WeAreMelissa" \
  --profile-dir "/home/you/.config/google-chrome" \
  --out melissa_selenium.json \
  --max-posts 200
```

If you don't provide `--profile-dir`, you may be prompted to log in when the browser opens (if not headless).

Options
- `--group-url` (required): full group URL.
- `--profile-dir`: Chrome user data dir path to reuse an existing logged-in session.
- `--headless`: run Chrome in headless mode (may be less reliable).
- `--max-posts`: maximum number of posts to collect.
- `--out`: output JSON filename.

Output
- JSON structure groups extracted items by category, e.g. `{"Plumber": [{...}], "Doctor": [{...}]}`.

If scraping fails or returns sparse results:
- Try increasing `--max-posts` and `--scroll-pause`.
- Use a logged-in profile via `--profile-dir`.
- Run without `--headless` so you can observe the browser and manually expand things if needed.

Alternatives
- Facebook Graph API (preferred if you have permission and an access token). See the Graph API script if available.
- Manual export or ask group members to submit recommendations in a form.
