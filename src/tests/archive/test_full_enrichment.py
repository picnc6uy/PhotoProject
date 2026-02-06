import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from record_catalog.config_manager import ConfigManager
from record_catalog.parser import OCRParser
from record_catalog.enricher import MetadataEnricher

OCR_CSV_PATH = r'C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\ocr_texts.csv'


def test_full_enrichment(csv_path):
    config = ConfigManager()
    parser = OCRParser(config)
    enricher = MetadataEnricher(config)

    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row['filename']
            ocr_text = row['ocr_text']
            print(f"Processing {filename}")

            parsed_metadata = parser.parse_text(ocr_text)
            enriched_metadata = enricher.enrich_metadata(parsed_metadata)

            print(f"Enriched metadata for {filename}:")
            print(enriched_metadata)
            print("-----")


if __name__ == '__main__':
    if not os.path.exists(OCR_CSV_PATH):
        print(f"OCR CSV not found at {OCR_CSV_PATH}, please run OCR test first.")
    else:
        test_full_enrichment(OCR_CSV_PATH)
