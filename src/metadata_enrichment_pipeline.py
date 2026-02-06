import csv
import re
import requests
import time
import pandas as pd

# --- Config and API Credentials ---
DISCOGS_TOKEN = "<your-discogs-token>"  # optional for higher rate limits
MUSICBRAINZ_USER_AGENT = "YourAppName/1.0 (your-email@example.com)"

# Filepaths
OCR_CSV_PATH = r"dev_data\record_catalog\data\inbox_photos_desc\image_descriptions_ocr.csv"
PHOTO_CATALOG_CSV_PATH = r"dev_data\record_catalog\data\outputs\photo_catalog.csv"
PARSED_OCR_CSV_PATH = r"dev_data\record_catalog\data\outputs\parsed_ocr.csv"
FINAL_CATALOG_CSV_PATH = r"dev_data\record_catalog\data\outputs\final_catalog.csv"

# --- Helpers ---

def parse_ocr_text(ocr_text):
    # Simple heuristic parsing example to extract title, catalog number, label
    metadata = {
        "Title": None,
        "Label": None,
        "Catalog Number": None,
        "Artist": None,
        # extend as needed
    }

    if not ocr_text:
        return metadata

    # Naive pattern matching
    catalog_match = re.search(r'([A-Z0-9\-]{2,20})', ocr_text)
    if catalog_match:
        metadata['Catalog Number'] = catalog_match.group(1)

    # Try to extract label (example)
    label_match = re.search(r'(Columbia|RCA|Victor|Capitol|EMI|Angel)', ocr_text, re.I)
    if label_match:
        metadata['Label'] = label_match.group(0)

    # Title and artist heuristics could be enhanced here
    # For now placeholder
    metadata['Title'] = "Unknown Title"
    metadata['Artist'] = "Unknown Artist"

    return metadata

def query_discogs(label, catalog_number):
    if not label or not catalog_number:
        return {}
    # Basic example search Discogs database via Discogs API
    headers = {"User-Agent": MUSICBRAINZ_USER_AGENT}
    params = {"release_title": catalog_number, "per_page": 1, "page": 1}
    url = "https://api.discogs.com/database/search"
    # TODO: Add token auth if available
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        if data.get('results'):
            # Grabbing first result for example
            result = data['results'][0]
            return {
                "Release Year": result.get('year'),
                "Genres": ','.join(result.get('genre', [])),
                # Add more fields here
            }
    except Exception as e:
        print(f"Discogs API error: {e}")
    return {}

def query_musicbrainz(title, artist):
    if not title or not artist:
        return {}
    url = "https://musicbrainz.org/ws/2/release/"
    params = {
        "query": f'release:{title} AND artist:{artist}',
        "fmt": "json",
        "limit": 1
    }
    headers = {"User-Agent": MUSICBRAINZ_USER_AGENT}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        if 'releases' in data and data['releases']:
            release = data['releases'][0]
            return {
                "Release Date": release.get('date'),
                "Country": release.get('country'),
                # Add more fields as needed
            }
    except Exception as e:
        print(f"MusicBrainz API error: {e}")
    return {}

# --- Main Pipeline ---

def main():
    print("Loading OCR CSV...")
    ocr_df = pd.read_csv(OCR_CSV_PATH)
    print(f"{len(ocr_df)} OCR records loaded")

    parsed_data = []
    for idx, row in ocr_df.iterrows():
        file = row['filename']
        ocr_text = row['ocr_text']
        metadata = parse_ocr_text(ocr_text)
        metadata['filename'] = file
        parsed_data.append(metadata)
        if idx % 10 == 0:
            print(f"Parsed OCR record {idx}")

    parsed_df = pd.DataFrame(parsed_data)
    parsed_df.to_csv(PARSED_OCR_CSV_PATH, index=False)
    print(f"Parsed OCR data saved: {PARSED_OCR_CSV_PATH}")

    print("Enriching data with Discogs and MusicBrainz...")
    enriched = []
    for idx, row in parsed_df.iterrows():
        discogs_data = query_discogs(row['Label'], row['Catalog Number'])
        mb_data = query_musicbrainz(row['Title'], row['Artist'])
        enrich = {**row.to_dict(), **discogs_data, **mb_data}
        enriched.append(enrich)
        if idx % 10 == 0:
            print(f"Enriched record {idx}")
        time.sleep(1)  # Respect rate limits

    enriched_df = pd.DataFrame(enriched)

    print("Loading original photo catalog...")
    photo_cat_df = pd.read_csv(PHOTO_CATALOG_CSV_PATH)

    print("Merging enriched data with original catalog...")
    final_df = pd.merge(photo_cat_df, enriched_df, left_on='filename', right_on='filename', how='left')

    final_df.to_csv(FINAL_CATALOG_CSV_PATH, index=False)
    print(f"Final catalog saved: {FINAL_CATALOG_CSV_PATH}")

if __name__ == "__main__":
    main()