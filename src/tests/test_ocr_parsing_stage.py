import os
import sys
import csv
import logging
from pathlib import Path

# Use workspace root as the base path for config and data
WORKSPACE_ROOT = Path(os.environ.get('WORKSPACE_ROOT', 'C:/Users/ghendrick/PhotoProject'))

sys.path.insert(0, str(WORKSPACE_ROOT / 'src'))

from record_catalog.config_manager import ConfigManager
from record_catalog.parser import OCRParser

class TestOCRParsingStage:
    def __init__(self):
        # Load config from workspace root
        config_path = WORKSPACE_ROOT / 'src' / 'config.yaml'
        self.config = ConfigManager(config_path=str(config_path))

        # Paths for input/output relative to workspace root
        self.ocr_csv_path = self.config.get('OCR_PARSED_CSV') or \
            str(WORKSPACE_ROOT / 'dev_data' / 'record_catalog' / 'data' / 'ocr_texts.csv')
        self.parsed_csv_path = str(WORKSPACE_ROOT / 'dev_data' / 'record_catalog' / 'data' / 'parsed_metadata.csv')

        self.parser = OCRParser(self.config)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s'
        )
        self.logger = logging.getLogger('OCRParsingTest')

    def run(self):
        if not os.path.exists(self.ocr_csv_path):
            self.logger.error(f'OCR CSV file not found at {self.ocr_csv_path}. Run OCR step first.')
            return

        parsed_metadata_list = []

        with open(self.ocr_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                filename = row.get('filename')
                ocr_text = row.get('ocr_text', '')
                if not ocr_text.strip():
                    self.logger.warning(f'No OCR text for {filename}, skipping parsing.')
                    continue

                parsed = self.parser.parse_text(ocr_text)

                # Add the original filename for reference
                parsed['filename'] = filename
                parsed_metadata_list.append(parsed)

        if parsed_metadata_list:
            # Collect all keys for CSV fieldnames
            keys = set()
            for data in parsed_metadata_list:
                keys.update(data.keys())
            fieldnames = sorted(keys)

            with open(self.parsed_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for data in parsed_metadata_list:
                    # Convert list values to comma-separated strings
                    row = {k: (', '.join(v) if isinstance(v, list) else v) for k, v in data.items()}
                    writer.writerow(row)

            self.logger.info(f'Parsed metadata saved to {self.parsed_csv_path}')
        else:
            self.logger.warning('No parsed metadata generated.')

if __name__ == '__main__':
    test = TestOCRParsingStage()
    test.run()
