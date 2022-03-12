# -*- coding: utf-8 -*-
"""
Ontario Ministry of Education Memo Downloader

TODO: Add Markdown file for each Year folder with a list of the memos, hyperlinked to each document.

"""

#
# imports
#
from bs4 import BeautifulSoup 
import urllib.request
import urllib
import os
import csv

#
# global variable(s)
#
url = 'https://efis.fma.csc.gov.on.ca/faab/Memos.htm'

#
# Grab the memo page from the website
#
page = urllib.request.urlopen(url)
soup = BeautifulSoup(page, "html.parser")

#
# grab the links to each memo folder (B_Memos and SB_Memos)
# 
memo_category_list = []

print(f'Finding memo category links in {url}...')

for link in soup.findAll('a', href=True): # find all links
    if (link['href'].startswith('B_Memos')) or (link['href'].startswith('SB_Memos')):
        # print(link['href'])
        memo_category_list.append(link['href'])

print('Memo category links found...')

#
# visit each memo folder and download all the PDF files
# from each one
#
pdf_dict = {}
url_base = 'https://efis.fma.csc.gov.on.ca/faab/'

print('Getting memo links...')
for link in memo_category_list:
    page_url = url_base + link
    # beautiful soup stuff
    page = urllib.request.urlopen(page_url)
    soup = BeautifulSoup(page, "html.parser")
    print('Getting memo links from', link)
    for pdf_link in soup.findAll('a', href = True): # find all links
        url_url = pdf_link.get("href").replace(' ', '%20') # spaces in URLs (why?!!)
        url_text = pdf_link.text.strip() # just in case
        url_text = ' '.join(pdf_link.text.split()) # get rid of double spacing
        if len(url_text) < 2: # catch the URLs with no text
            url_text = url_url
        if 'pdf' in url_url: # only download PDFs
            pdf_url = url_base + '/' + url_url
            pdf_dict[pdf_url] = url_text

#
# read in existing memos
#
existing_memos = {}

csv_file = open('memos.csv')
csv_reader = csv.reader(csv_file, delimiter=',')
for row in csv_reader:
    url = row[0]
    title = row[1]
    existing_memos[url] = title
csv_file.close()

# set up save memos to memos.csv (opens in Excel or Google Sheets)
csv_file = open('memos.csv', mode='a', newline='')
memo_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
# memo_writer.writerow(['URL', 'Memo Name']) # only needed the first time program is run

# for the counter
num_pdfs = len(pdf_dict)
count = 1

# process each memo to save and make entry in CSV file
for k, v in pdf_dict.items():
    memo_folder = k.split('/')[-2] # e.g., B2012
    filename = k.split('/')[-1] # e.g., B1_EN_AODA.pdf
    # save directory
    save_dir = 'memos'
    save_path = os.path.join(save_dir, memo_folder)
    os.makedirs(save_path, exist_ok = True) 
    # filename
    path_with_filename = os.path.join(save_path, filename)
    # grab the file from online
    if k not in existing_memos: # add to CSV if not already there
        memo_writer.writerow([k, v]) # save to CSV
        print(f'{k} added to CSV')
    if not os.path.isfile(path_with_filename): # if it doesn't already exist
        try:
            urllib.request.urlretrieve(k, path_with_filename)
            print(f'{count}/{num_pdfs}')
        except:
            print(f'{count}/{num_pdfs} >>> Error {k} not downloaded')
    else:
        print(f'{count}/{num_pdfs} >>> Already exists {path_with_filename}')
    count += 1
    
csv_file.close()
