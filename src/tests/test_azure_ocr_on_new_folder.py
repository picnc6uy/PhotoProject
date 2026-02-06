import os
import sys
import time
import logging
import csv
from pathlib import Path
from msrestazure.azure_exceptions import CloudError

# Add workspace src path for imports
WORKSPACE_ROOT = Path(r"C:/Users/ghendrick/PhotoProject")
SRC_PATH = WORKSPACE_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from record_catalog.config_manager import ConfigManager
from record_catalog.ocr_service import OCRService


def main():
    # Absolute path for the new folder
    ocr_images_folder = r"C:/Users/ghendrick/PhotoProject/dev_data/record_catalog/data/inbox_photos_processed"

    # Load config for Azure credentials and retry params
    config_path = WORKSPACE_ROOT / "src" / "config.yaml"
    config = ConfigManager(config_path=str(config_path))

    delay_seconds = 3  # Increased delay for rate limiting mitigation
    max_retries = config.get("MAX_OCR_RETRIES") or 10
    subscription_key = config.get("AZURE_COMPUTER_VISION_KEY")
    endpoint = config.get("AZURE_COMPUTER_VISION_ENDPOINT")
    if not subscription_key or not endpoint:
        print("Azure OCR credentials missing. Check config.yaml")
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    logger = logging.getLogger("AzureOCRNewFolderTest")

    if not os.path.isdir(ocr_images_folder):
        logger.error(f"OCR folder not found or invalid: {ocr_images_folder}")
        return

    ocr_service = OCRService(config)

    results = []

    for filename in os.listdir(ocr_images_folder):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            continue

        image_path = os.path.join(ocr_images_folder, filename)

        retries = 0
        while retries <= max_retries:
            try:
                ocr_result = ocr_service.process_image(image_path)
                break
            except CloudError as e:
                if e.status_code == 429:
                    wait_time = delay_seconds * (2**retries)
                    logger.warning(f"429 Too Many Requests. Retry {retries + 1}/{max_retries} after {wait_time}s.")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    logger.error(f"Azure CloudError for {filename}: {e}")
                    ocr_result = {}
                    break
        else:
            logger.error(f"Max retries exceeded for {filename}, skipping.")
            continue

        text = ""
        if ocr_result and "lines" in ocr_result:
            texts = []
            for line in ocr_result["lines"]:
                filtered_words = [
                    w["text"] for w in line.get("words", []) if w.get("confidence", 1) >= 0.8
                ]
                if filtered_words:
                    texts.append(" ".join(filtered_words))
            text = "\n".join(texts)

        print(f"-----\n{filename} OCR Text:\n{text}\n")

        results.append({"filename": filename, "ocr_text": text})

        time.sleep(delay_seconds)

    # Export OCR results to CSV
    output_csv_path = WORKSPACE_ROOT / "dev_data" / "record_catalog" / "data" / "ocr_results_export.csv"
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["filename", "ocr_text"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in results:  # Correct indentation here
            writer.writerow(row)

    logger.info(f"Processed {len(results)} images. OCR text saved to {output_csv_path}")

    print("\nCharacter Count Summary:\n")
    print(f"{'Filename':40} | {'Char Count':>10}")
    print("-" * 55)
    for row in results:
        char_count = len(row["ocr_text"])
        print(f"{row['filename'][:40]:40} | {char_count:10}")


if __name__ == "__main__":
    main()

