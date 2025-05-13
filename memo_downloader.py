import re  # for collapsing duplicate slashes
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse, urljoin
import os
import csv

# Base URL for all memos
def normalize_url(raw_url: str, base: str = 'https://efis.fma.csc.gov.on.ca/faab/') -> str:
    """
    Normalize a raw memo URL by collapsing internal duplicate slashes and
    joining with the base to ensure a single canonical form.
    """
    # Parse the URL to extract path
    parsed = urlparse(raw_url)
    # Collapse any sequence of slashes into a single slash
    clean_path = re.sub(r'/+', '/', parsed.path)
    # Remove leading slash to make it relative for urljoin
    relative = clean_path.lstrip('/')
    # Join with base and return
    return urljoin(base, relative)

url_index = 'https://efis.fma.csc.gov.on.ca/faab/Memos.htm'
url_base = 'https://efis.fma.csc.gov.on.ca/faab/'

# 1. Scrape memo category links
print(f'Finding memo category links in {url_index}...')
page = urllib.request.urlopen(url_index)
soup = BeautifulSoup(page, 'html.parser')

memo_category_list = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if href.startswith('B_Memos') or href.startswith('SB_Memos'):
        memo_category_list.append(href)
print(f'  Found {len(memo_category_list)} categories.')

# 2. Scrape all PDF links into a dict: { normalized_pdf_url: title }
pdf_dict = {}
print('Getting memo links...')
for category in memo_category_list:
    page_url = urljoin(url_base, category)
    print('  Scraping category:', category)
    page = urllib.request.urlopen(page_url)
    soup = BeautifulSoup(page, 'html.parser')
    for a in soup.find_all('a', href=True):
        raw_href = a['href'].replace(' ', '%20')
        if 'pdf' not in raw_href.lower():
            continue
        title = ' '.join(a.get_text(strip=True).split())
        if not title:
            title = raw_href
        pdf_url = normalize_url(raw_href, base=url_base)
        pdf_dict[pdf_url] = title
print(f'  Found {len(pdf_dict)} PDF files.')

# 3. Load existing memos from CSV (normalize keys)
existing_memos = {}
with open('memos.csv', 'r', encoding='utf-8', errors='replace') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        if len(row) < 2:
            continue
        url, title = row[0], row[1]
        existing_memos[url] = title

print(f'Loaded {len(existing_memos)} existing memos from CSV.')

# 4. Prepare CSV writer for appending new entries
df_handle = open('memos.csv', 'a', newline='', encoding='utf-8')
writer = csv.writer(df_handle, quoting=csv.QUOTE_ALL)

# 5. Download and group memos by exact subfolder
memos_by_folder = {}
save_root = 'memos'
os.makedirs(save_root, exist_ok=True)

for count, (pdf_url, title) in enumerate(pdf_dict.items(), start=1):
    # Extract subfolder and filename
    parts = urlparse(pdf_url).path.split('/')
    memo_folder = parts[-2]
    filename = parts[-1]

    # Write to CSV if new
    if pdf_url not in existing_memos:
        writer.writerow([pdf_url, title])
        print(f'  [CSV] Added: {pdf_url}')

    # Ensure local folder exists
    folder_path = os.path.join(save_root, memo_folder)
    os.makedirs(folder_path, exist_ok=True)
    local_path = os.path.join(folder_path, filename)

    # Download PDF if missing
    if not os.path.isfile(local_path):
        try:
            urllib.request.urlretrieve(pdf_url, local_path)
            print(f'  [Download] {count}/{len(pdf_dict)}: {filename}')
        except Exception as e:
            print(f'  [Error] Failed to download {pdf_url}: {e}')
    else:
        print(f'  [Skip] Already exists: {filename}')

    # Group by exact folder
    memos_by_folder.setdefault(memo_folder, []).append((title, filename))

# Close CSV
df_handle.close()

# 6. Generate README.md per exact subfolder
print('Creating README.md files...')
for folder, items in memos_by_folder.items():
    readme_path = os.path.join(save_root, folder, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as md:
        md.write(f'# Memos in {folder}\n\n')
        md.write('Below is the list of memos in this folder:\n\n')
        for title, filename in items:
            md.write(f'- [{title}](./{filename})\n')
    print(f'  Created {readme_path}')

print('Done.')
