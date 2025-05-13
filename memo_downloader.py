#!/usr/bin/env python3
"""
Ontario Ministry of Education Memo Downloader
"""

import re
import os
import csv
import urllib.request
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

INDEX_URL = 'https://efis.fma.csc.gov.on.ca/faab/Memos.htm'
URL_BASE  = 'https://efis.fma.csc.gov.on.ca/faab/'

def collapse(path):
    return re.sub(r'/+', '/', path)

def normalize_url(raw, base=URL_BASE):
    href = raw.replace(' ', '%20')
    path = urlparse(href).path
    clean = collapse(path)
    return urljoin(base, clean.lstrip('/'))

# 1) SCRAPE ALL PDF URLs + raw titles
print("⏳ Scraping memo categories…")
page = urllib.request.urlopen(INDEX_URL)
soup = BeautifulSoup(page, 'html.parser')

cats = [a['href'] for a in soup.find_all('a', href=True)
        if a['href'].startswith(('B_Memos','SB_Memos'))]

pdf_links = {}
for cat in cats:
    cat_url = normalize_url(cat)
    sub_page = urllib.request.urlopen(cat_url)
    sub_soup = BeautifulSoup(sub_page, 'html.parser')
    for a in sub_soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            full = normalize_url(href, base=cat_url)
            raw_text = ' '.join(a.text.split())
            pdf_links[full] = raw_text

print(f"✅ Found {len(pdf_links)} PDF links.\n")

# 2) LOAD YOUR EXISTING CSV MAPPING (filename → title)
csv_map = {}
if os.path.exists('memos.csv'):
    with open('memos.csv', newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for url, title in reader:
            if url.lower().startswith('url'):  # skip header row
                continue
            fn = os.path.basename(urlparse(url).path)
            csv_map[fn] = title

# 3) OPEN CSV FOR APPENDING NEW ENTRIES
out_csv = open('memos.csv', 'a', newline='', encoding='utf-8')
writer  = csv.writer(out_csv, quoting=csv.QUOTE_ALL)

# 4) DOWNLOAD & BUCKET BY SUBFOLDER, APPEND NEW TO CSV
by_folder = {}
total = len(pdf_links)
for i, (url, raw_title) in enumerate(pdf_links.items(), 1):
    fn = os.path.basename(urlparse(url).path)
    folder = os.path.basename(os.path.dirname(urlparse(url).path))
    local_dir = os.path.join('memos', folder)
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, fn)

    # Decide on the “official” title:
    if fn in csv_map:
        title = csv_map[fn]
    else:
        # if scraped text is too short (e.g. “r”), fall back to filename
        if len(raw_title) < 3:
            title = fn.replace('_', ' ').replace('.pdf','')
        else:
            title = raw_title
        # record the new URL+title in your CSV
        writer.writerow([url, title])
        print(f"[CSV+] {fn}")
        csv_map[fn] = title

    # download
    if not os.path.exists(local_path):
        try:
            urllib.request.urlretrieve(url, local_path)
            status = 'dl'
        except Exception as e:
            status = 'ERR'
        print(f"[{i}/{total}] {status:3} {folder}/{fn}")
    else:
        print(f"[{i}/{total}] ok  {folder}/{fn}")

    by_folder.setdefault(folder, []).append((fn, title))

out_csv.close()

# 5) REWRITE README.md PER EXACT SUBFOLDER
def natural_key(s):
    parts = re.split(r'(\d+)', s)
    return [int(p) if p.isdigit() else p.lower() for p in parts]

for folder, items in by_folder.items():
    items.sort(key=lambda ft: natural_key(ft[0]))
    readme = os.path.join('memos', folder, 'README.md')
    with open(readme, 'w', encoding='utf-8') as md:
        md.write(f"# Memos in {folder}\n\n")
        md.write("Available memos:\n\n")
        for fn, title in items:
            md.write(f"- [{title}](./{fn})\n")
    print(f"📝  Updated README for {folder}")
