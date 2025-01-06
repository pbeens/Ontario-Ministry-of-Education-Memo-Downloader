"""
Ontario Ministry of Education Memo Downloader
"""

import re  # for extracting years from folder names
from bs4 import BeautifulSoup
import urllib.request
import urllib
import os
import csv

url = 'https://efis.fma.csc.gov.on.ca/faab/Memos.htm'

# Grab the memo page from the website
page = urllib.request.urlopen(url)
soup = BeautifulSoup(page, "html.parser")

# Grab the links to each memo folder (B_Memos and SB_Memos)
memo_category_list = []
print(f'Finding memo category links in {url}...')

for link in soup.findAll('a', href=True):
    if (link['href'].startswith('B_Memos')) or (link['href'].startswith('SB_Memos')):
        memo_category_list.append(link['href'])

print('Memo category links found...')

pdf_dict = {}
url_base = 'https://efis.fma.csc.gov.on.ca/faab/'

print('Getting memo links...')
for link in memo_category_list:
    page_url = url_base + link
    page = urllib.request.urlopen(page_url)
    soup = BeautifulSoup(page, "html.parser")
    print('Getting memo links from', link)
    for pdf_link in soup.findAll('a', href=True):
        url_url = pdf_link.get("href").replace(' ', '%20')  # handle spaces
        url_text = ' '.join(pdf_link.text.split())          # normalize spacing
        if len(url_text) < 2:  # catch the URLs with no text
            url_text = url_url
        if 'pdf' in url_url.lower():  # only PDF files
            pdf_url = url_base + '/' + url_url
            pdf_dict[pdf_url] = url_text

# Read in existing memos from CSV
existing_memos = {}
with open('memos.csv', 'r', encoding='cp1252') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        url = row[0]
        title = row[1]
        existing_memos[url] = title

# Prepare to append new rows to memos.csv
csv_file = open('memos.csv', mode='a', newline='', encoding='utf-8')
memo_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

# Dictionary to store memos grouped by year
# Key: year (e.g., "2012"), Value: list of tuples [(memo_title, filename), ...]
memos_by_year = {}

num_pdfs = len(pdf_dict)
count = 1

for k, v in pdf_dict.items():
    # example of k: https://efis.fma.csc.gov.on.ca/faab/B_Memos/B2012/B12_EN.pdf
    memo_folder = k.split('/')[-2]  # e.g., B2012
    filename = k.split('/')[-1]     # e.g., B12_EN.pdf

    # create memos/B2012 if it doesn't exist
    save_dir = 'memos'
    save_path = os.path.join(save_dir, memo_folder)
    os.makedirs(save_path, exist_ok=True)

    # local path with filename
    path_with_filename = os.path.join(save_path, filename)

    # write to CSV if this memo doesn't already exist
    if k not in existing_memos:
        memo_writer.writerow([k, v])
        print(f'{k} added to CSV')

    # download PDF if it doesn't already exist locally
    if not os.path.isfile(path_with_filename):
        try:
            urllib.request.urlretrieve(k, path_with_filename)
            print(f'{count}/{num_pdfs}')
        except:
            print(f'{count}/{num_pdfs} >>> Error {k} not downloaded')
    else:
        print(f'{count}/{num_pdfs} >>> Already exists {path_with_filename}')
    count += 1

    # Extract year (e.g., from "B2012" or "SB2013")
    # We'll look for a 4-digit year anywhere in the folder name
    match = re.search(r'(\d{4})', memo_folder)
    if match:
        year = match.group(1)
    else:
        # If no 4-digit year is found, you can decide how to handle it
        year = memo_folder  # fallback or custom handling

    # Collect memo info by year
    if year not in memos_by_year:
        memos_by_year[year] = []
    memos_by_year[year].append((v, filename))

csv_file.close()

# Create Markdown file in each year’s folder
for year, memo_list in memos_by_year.items():
    # For each year, we assume they are inside subfolders like memos/B2012, memos/SB2012, etc.
    # We can have multiple folders with the same year, so let's handle them carefully:
    # We could create only one .md file per exact subfolder, or unify all "2012" memos in one place.
    #
    # In this example, we unify them by year in a single folder. If you prefer per subfolder
    # (B2012, SB2012), adjust accordingly.
    
    # We'll assume the folder is in "memos" + "Byyyy" or "SByyyy"
    # So let's guess a path:
    folder_path = os.path.join('memos')  
    # to store them in a single year-labeled folder, you could do:
    # folder_path = os.path.join('memos', year)
    # but that might differ from how you've structured it above.
    #
    # Instead, we find all subfolders that match that year’s pattern:
    possible_folders = []
    for f in os.listdir(folder_path):
        # Check if f has the same 4-digit year
        if re.search(rf'{year}', f):
            possible_folders.append(f)

    # For each subfolder that corresponds to the year, write a README.md
    for f in possible_folders:
        subfolder_path = os.path.join(folder_path, f)
        md_path = os.path.join(subfolder_path, 'README.md')
        with open(md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# Memos for {f}\n\n")
            md_file.write("Below is a list of memos available in this folder:\n\n")
            for memo_title, memo_filename in memo_list:
                # Construct a relative link to the PDF in the same folder:
                link = f"./{memo_filename}"
                md_file.write(f"- [{memo_title}]({link})\n")
        print(f"Markdown file created at {md_path}")
