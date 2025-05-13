import csv
import os
import re
from urllib.parse import urlparse, urljoin

def normalize_url(url, base='https://efis.fma.csc.gov.on.ca/faab/'):
    # Parse out the raw path, which may include double-slashes
    parsed = urlparse(url)
    # Collapse any sequence of slashes into one
    clean_path = re.sub(r'/+', '/', parsed.path)
    # Ensure we’re joining only the path portion
    return urljoin(base, clean_path.lstrip('/'))


def clean_csv(input_path='memos.csv', output_path=None, base_url='https://efis.fma.csc.gov.on.ca/faab/'):
    """
    Read all rows from input_path, normalize URLs, deduplicate by URL (keeping the first title),
    and write back a cleaned CSV. If output_path is None, overwrite input_path safely.
    """
    # Determine output file
    if output_path is None:
        temp_path = input_path + '.tmp'
    else:
        temp_path = output_path

    seen = set()
    cleaned_rows = []

    # Read and normalize
    with open(input_path, mode='r', newline='', encoding='utf-8', errors='replace') as infile:
        reader = csv.reader(infile)
        # Optionally preserve header row if present
        first_row = next(reader, None)
        if first_row and first_row[0].lower().startswith('url'):
            cleaned_rows.append(first_row)
        else:
            # No header; treat first row as data
            if first_row:
                reader = [first_row] + list(reader)
        
        for row in reader:
            if not row:
                continue
            url, title = row[0], row[1] if len(row) > 1 else ''
            norm = normalize_url(url, base_url)
            if norm not in seen:
                seen.add(norm)
                cleaned_rows.append([norm, title])

    # Write cleaned data
    with open(temp_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
        writer.writerows(cleaned_rows)

    # Replace original if needed
    if output_path is None:
        os.replace(temp_path, input_path)
        print(f"Cleaned CSV written back to {input_path}")
    else:
        print(f"Cleaned CSV written to {temp_path}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Clean memos.csv: normalize URLs and dedupe entries.')
    parser.add_argument('--input', '-i', default='memos.csv', help='Path to the input CSV file')
    parser.add_argument('--output', '-o', help='Path to write the cleaned CSV (defaults to overwrite)')
    parser.add_argument('--base', '-b', default='https://efis.fma.csc.gov.on.ca/faab/',
                        help='Base URL for normalization')
    args = parser.parse_args()
    clean_csv(input_path=args.input, output_path=args.output, base_url=args.base)
