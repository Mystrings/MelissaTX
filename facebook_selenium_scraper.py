#!/usr/bin/env python3
"""
facebook_selenium_scraper.py

Best-effort Selenium scraper to extract posts and comments from a Facebook Group.

Usage notes:
- Recommended: reuse an existing Chrome/Chromium profile using --profile-dir to avoid logging in via script.
- Headless mode may be detected by Facebook; prefer non-headless for reliability.

This script is best-effort. Facebook's DOM and anti-bot measures change often; adapt selectors if needed.
"""
import argparse
import json
import re
import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

KEYWORDS = {
    "Plumber": ["plumb", "plumber", "plumbing"],
    "Doctor": ["doctor", "dr.", "clinic", "physician", "pediatric", "gp "],
    "Grocery": ["grocery", "market", "supermarket"],
    "Cafe": ["cafe", "coffee", "espresso", "bakery"],
    "Home Services": ["contractor", "electrician", "handyman", "repair", "plumb"],
    "Education": ["tutor", "tutoring", "school", "instructor"],
    "Personal Care": ["barber", "salon", "hair", "spa"],
}

PHONE_RE = re.compile(r'(\+?\d[\d\-\s\(\)]{6,}\d)')
URL_RE = re.compile(r'(https?://[^\s]+)')


def categorize_text(text: str) -> str:
    t = (text or "").lower()
    for cat, kws in KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return cat
    return "Uncategorized"


def extract_entities(text: str):
    phones = PHONE_RE.findall(text or "")
    urls = URL_RE.findall(text or "")
    names = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})', text or "")
    name = names[0].strip() if names else ""
    return {"phones": phones, "urls": urls, "name_guess": name}


def setup_driver(profile_dir: str = None, headless: bool = False):
    options = webdriver.ChromeOptions()
    # use profile dir if provided (keeps login cookies)
    if profile_dir:
        options.add_argument(f"--user-data-dir={profile_dir}")
    if headless:
        # use headless mode and add flags that help Chrome run inside containers
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--single-process")
        options.add_argument("--no-zygote")
        options.add_argument("--disable-software-rasterizer")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1200, 900)
    return driver


def expand_comments_in_post(post):
    # try a few common buttons to reveal more comments
    btn_texts = [
        'View more comments',
        'View previous comments',
        'See more comments',
        'View more',
        'More comments',
    ]
    for txt in btn_texts:
        try:
            buttons = post.find_elements(By.XPATH, f".//div[normalize-space()='{txt}'] | .//span[normalize-space()='{txt}'] | .//a[normalize-space()='{txt}']")
            for b in buttons:
                try:
                    b.click()
                    time.sleep(0.3)
                except Exception:
                    pass
        except Exception:
            pass


def collect_posts(driver, max_posts=200, scroll_pause=1.0):
    posts = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0
    while len(posts) < max_posts and attempts < 60:
        articles = driver.find_elements(By.XPATH, "//div[@role='article']")
        for a in articles:
            try:
                pid = a.get_attribute('data-ft') or a.id or a.get_attribute('data-xt') or None
            except Exception:
                pid = None
            text = a.text or ""
            try:
                link_el = a.find_element(By.XPATH, ".//a[contains(@href,'/posts/') or contains(@href,'/permalink') or contains(@href,'/groups/')]")
                link = link_el.get_attribute('href')
            except Exception:
                link = ''
            posts.append({'id': pid, 'text': text, 'permalink': link})

        # dedupe by permalink+text
        seen = set()
        uniq = []
        for p in posts:
            key = (p.get('permalink') or '') + '||' + (p.get('text') or '')[:120]
            if key not in seen:
                seen.add(key)
                uniq.append(p)
        posts = uniq

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            attempts += 1
        else:
            attempts = 0
        last_height = new_height
    return posts[:max_posts]


def normalize_entry(source_type, text, permalink):
    ent = extract_entities(text or "")
    cat = categorize_text(text or "")
    return {"category": cat, "excerpt": (text or "")[:400], "phones": ent["phones"], "urls": ent["urls"], "name_guess": ent["name_guess"], "source": source_type, "permalink": permalink}


def main():
    p = argparse.ArgumentParser(description="Selenium Facebook Group scraper (best-effort)")
    p.add_argument('--group-url', required=True, help='Full group URL, e.g. https://www.facebook.com/groups/WeAreMelissa')
    p.add_argument('--profile-dir', help='Chrome user-data-dir to reuse an existing logged-in profile')
    p.add_argument('--headless', action='store_true')
    p.add_argument('--max-posts', type=int, default=200)
    p.add_argument('--scroll-pause', type=float, default=1.0)
    p.add_argument('--out', default='fb_selenium_recs.json')
    args = p.parse_args()

    driver = setup_driver(profile_dir=args.profile_dir, headless=args.headless)
    try:
        print('Loading group page...')
        driver.get(args.group_url)
        # allow page to load
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='article']")))
    except Exception as e:
        print('Initial load error:', e)

    print('Collecting posts (this may take a while)...')
    posts = collect_posts(driver, max_posts=args.max_posts, scroll_pause=args.scroll_pause)
    print(f'Collected {len(posts)} candidate posts')

    categorized = defaultdict(list)

    for i, p in enumerate(posts, start=1):
        text = p.get('text','')
        permalink = p.get('permalink','')
        entry = normalize_entry('post', text, permalink)
        categorized[entry['category']].append(entry)

    # Attempt to click comments for each article and extract comment text
    for article in driver.find_elements(By.XPATH, "//div[@role='article']")[:len(posts)]:
        try:
            expand_comments_in_post(article)
            time.sleep(0.2)
            # comments often are rendered as divs; collect any small snippets
            comment_divs = article.find_elements(By.XPATH, ".//div[contains(@aria-label,'Comment') or contains(@data-testid,'UFI2Comment') or .//span[contains(text(),'•')]]")
            for cd in comment_divs:
                try:
                    ctext = cd.text or ''
                    if not ctext.strip():
                        continue
                    cent = normalize_entry('comment', ctext, '')
                    categorized[cent['category']].append(cent)
                except Exception:
                    pass
        except Exception:
            pass

    out = {k: v for k, v in categorized.items()}
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Saved results to', args.out)
    driver.quit()


if __name__ == '__main__':
    main()
