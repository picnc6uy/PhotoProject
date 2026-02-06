import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from record_catalog.config_manager import ConfigManager
from record_catalog.parser import OCRParser
from record_catalog.enricher import MetadataEnricher

# CSV file paths
OCR_CSV_PATH = os.path.abspath('dev_data/record_catalog/data/ocr_texts.csv')
ENRICHED_CSV_PATH = os.path.abspath('dev_data/record_catalog/data/enriched_metadata.csv')


def test_enrich_and_save(csv_path, enriched_csv_path):
    config = ConfigManager()
    parser = OCRParser(config)
    enricher = MetadataEnricher(config)

    enriched_data = []

    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row.get('filename')
            ocr_text = row['ocr_text']
            parsed = parser.parse_text(ocr_text)
            enriched = enricher.enrich_metadata(parsed)
            enriched['filename'] = filename
            enriched_data.append(enriched)

    if enriched_data:
        keys = set()
        for d in enriched_data:
            keys.update(d.keys())
        fieldnames = sorted(keys)

        with open(enriched_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in enriched_data:
                row = {k: (", ".join(v) if isinstance(v, list) else v) for k, v in data.items()}
                writer.writerow(row)

        print(f"Saved enriched metadata to {enriched_csv_path}")
    else:
        print("No enriched data to save.")


if __name__ == '__main__':
    if not os.path.exists(OCR_CSV_PATH):
        print(f"OCR CSV file {OCR_CSV_PATH} not found. Run OCR test first.")
    else:
        test_enrich_and_save(OCR_CSV_PATH, ENRICHED_CSV_PATH)
