import csv
import os
import sys
import time
import unittest
from pathlib import Path
import logging
from msrestazure.azure_exceptions import CloudError

# Add workspace src path for imports
WORKSPACE_ROOT = Path(r"C:/Users/ghendrick/PhotoProject")
SRC_PATH = WORKSPACE_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from record_catalog.config_manager import ConfigManager
from record_catalog.ocr_service import OCRService

class TestAzureOCRService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config_path = WORKSPACE_ROOT / "src" / "config.yaml"
        cls.config = ConfigManager(config_path=str(config_path))

        cls.ocr_images_folder = cls.config.get("OCR_IMAGE_FOLDER")
        if cls.ocr_images_folder is None:
            cls.ocr_images_folder = "dev_data/record_catalog/data/inbox_photos_ocr"
        cls.ocr_images_folder = str(cls.ocr_images_folder)

        outputs_folder = cls.config.get("OUTPUTS_FOLDER")
        if outputs_folder is None:
            outputs_folder = "dev_data/record_catalog/data/outputs"
        outputs_folder = str(outputs_folder)
        os.makedirs(outputs_folder, exist_ok=True)

        default_output_csv = os.path.join(outputs_folder, "ocr_texts.csv")
        cls.output_csv_path = cls.config.get("OCR_PARSED_CSV")
        if cls.output_csv_path is None:
            cls.output_csv_path = default_output_csv
        cls.output_csv_path = str(cls.output_csv_path)

        delay_seconds = cls.config.get("OCR_RETRY_DELAY")
        if delay_seconds is None:
            delay_seconds = 7
        cls.delay_seconds = int(delay_seconds)

        max_retries = cls.config.get("MAX_OCR_RETRIES")
        if max_retries is None:
            max_retries = 3
        cls.max_retries = int(max_retries)

        subscription_key = cls.config.get("AZURE_COMPUTER_VISION_KEY")
        endpoint = cls.config.get("AZURE_COMPUTER_VISION_ENDPOINT")
        if not subscription_key or not endpoint:
            raise ValueError("Azure OCR credentials missing.")

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
            force=True,
        )
        cls.logger = logging.getLogger("AzureOCRTest")

    def test_azure_ocr_service_on_folder(self):
        ocr_service = OCRService(self.config)

        if self.ocr_images_folder is None or not os.path.isdir(self.ocr_images_folder):
            self.logger.error(f"OCR folder not found or invalid: {self.ocr_images_folder}")
            self.skipTest(f"OCR folder not found or invalid: {self.ocr_images_folder}")

        results = []

        for filename in os.listdir(self.ocr_images_folder):
            if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                continue

            image_path = os.path.join(self.ocr_images_folder, filename)

            retries = 0
            while retries <= self.max_retries:
                try:
                    ocr_result = ocr_service.process_image(image_path)
                    break
                except CloudError as e:
                    if e.status_code == 429:
                        wait_time = self.delay_seconds * (2 ** retries)
                        self.logger.warning(f"429 Too Many Requests received. Retry {retries + 1}/{self.max_retries} after {wait_time} seconds.")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        self.logger.error(f"Azure CloudError for {filename}: {e}")
                        ocr_result = {}
                        break
            else:
                self.logger.error(f"Max retries exceeded for {filename}, skipping.")
                continue

            text = ''
            if ocr_result and 'lines' in ocr_result:
                texts = []
                for line in ocr_result['lines']:
                    filtered_words = [w['text'] for w in line.get('words', []) if w.get('confidence', 1) >= 0.8]
                    if filtered_words:
                        texts.append(' '.join(filtered_words))
                text = '\n'.join(texts)

            results.append({'filename': filename, 'ocr_text': text})
            time.sleep(self.delay_seconds)

        output_csv_path = self.output_csv_path
        with open(str(output_csv_path), 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['filename', 'ocr_text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)

        self.logger.info(f"Processed {len(results)} images. OCR text saved to {output_csv_path}")

        print("\nCharacter Count Summary:", flush=True)
        print(f{"{'Filename':40} | {'Char Count':>10}"}, flush=True)
        print("-" * 55, flush=True)
        for row in results:
            char_count = len(row['ocr_text'])
            print(f{"{row['filename'][:40]:40} | {char_count:10}"}, flush=True)

if __name__ == '__main__':
    unittest.main()
