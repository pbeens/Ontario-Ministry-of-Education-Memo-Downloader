# Ontario-Ministry-of-Education-Memo-Downloader

Summary: Python utility to download all memos from the Ontario Ministry of Education website.

Why did I write this? Mostly because some governments come in and make history disappear, i.e., they delete old communications they want the public to forget. By writing this utility it makes it easy for others to download all the memos to their own computers for safe keeping.

## How it Works

This utility downloads all the memos from https://efis.fma.csc.gov.on.ca/faab/Memos.htm.
It first finds all the "B" and "SB" page links, then goes into these pages and finds all the memos (assumed to be PDFs) and downloads them into the `memos` folder. It also saves a list of all the memos in `memos.csv`. This file lists the URL (web address) and document name for each memo. It can be loaded into Excel or uploaded to Google Sheets for viewing.

To speed things up, the program skips any files that are already downloaded.

If you wish to try this program yourself, you'll first have to download Python from https://www.python.org/. Then click on the green Code button (assuming you are viewing this on GitHub) and then click `Download Zip`.

If you spot any mistakes or the program ever breaks, feel free to reach out to me via [Twitter](https://twitter.com/pbeens). I'd also love to hear if you find it useful!
