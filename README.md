# Ontario-Ministry-of-Education-Memo-Downloader

Python utility to download all memos from the Ontario Ministry of Education website.

Why did I write this utility? Mostly because some governments come in and make history disappear. By writing this utility it makes it easy for others to download all the memos to their own computers for safe keeping. 

## How it Works

This utility downloads all the memos (assumed to be in PDF format) from https://efis.fma.csc.gov.on.ca/faab/Memos.htm.
It first finds all the "B" and "SB" page links, then goes into these pages and finds all the PDFs and downloads them.

It also saves a list of all the memos in `memos.csv`. This file lists the URL (web address) and document name for each memo. It can be loaded into Excel or uploaded to Google Sheets for viewing.

The program skips any files that are already downloaded.
