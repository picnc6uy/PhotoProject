import csv
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from record_catalog.config_manager import ConfigManager
from record_catalog.ocr_service import OCRService
from msrestazure.azure_exceptions import CloudError

OCR_CSV_OUTPUT_PATH = os.path.abspath('dev_data/record_catalog/data/ocr_texts.csv')


def test_ocr_on_folder(ocr_folder, delay_seconds=7, max_retries=3):
    config = ConfigManager()
    ocr_service = OCRService(config)

    results = []

    for filename in os.listdir(ocr_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            image_path = os.path.join(ocr_folder, filename)
            
            attempts = 0
            while attempts <= max_retries:
                try:
                    result = ocr_service.process_image(image_path)
                    break
                except CloudError as e:
                    if e.status_code == 429:
                        wait_time = delay_seconds * (2 ** attempts)
                        print(f"429 Too Many Requests received. Retry {attempts + 1}/{max_retries} after {wait_time} seconds.")
                        time.sleep(wait_time)
                        attempts += 1
                    else:
                        print(f"Azure CloudError for {filename}: {e}")
                        result = {}
                        break
            else:
                print(f"Max retries exceeded for {filename}, skipping.")
                continue

            text = result.get('text', '')
            if text.strip():
                print(f"OCR Text for {filename} (preview): {text[:100]}...")
                print(f"Character count for {filename}: {len(text)}")

            else:
                print(f"No OCR text extracted from {filename}")

            results.append({'filename': filename, 'ocr_text': text})

            time.sleep(delay_seconds)  # Delay between OCR requests

    with open(OCR_CSV_OUTPUT_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'ocr_text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\nProcessed {len(results)} images. OCR text saved to {OCR_CSV_OUTPUT_PATH}")


if __name__ == '__main__':
    ocr_folder = os.path.abspath('dev_data/record_catalog/data/inbox_photos_ocr')
    test_ocr_on_folder(ocr_folder)
