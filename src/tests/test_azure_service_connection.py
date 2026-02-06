import sys
import os
import logging
from pathlib import Path

# Add workspace src path for imports
WORKSPACE_ROOT = Path(r"C:/Users/ghendrick/PhotoProject")
SRC_PATH = WORKSPACE_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from record_catalog.config_manager import ConfigManager
from record_catalog.ocr_service import OCRService

def test_azure_ocr_connection():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
    )
    logger = logging.getLogger("AzureConnectionTest")

    config_path = WORKSPACE_ROOT / "src" / "config.yaml"
    config = ConfigManager(config_path=str(config_path))

    ocr_images_folder = config.get("OCR_IMAGE_FOLDER")
    if not ocr_images_folder:
        logger.error("OCR_IMAGE_FOLDER not set in config")
        return ""

    test_image = "photo_0003.jpg"
    test_image_path = os.path.join(ocr_images_folder, test_image)

    if not os.path.isfile(test_image_path):
        logger.error(f"Test image does not exist: {test_image_path}")
        return ""

    logger.info(f"Testing Azure OCR service connection using image: {test_image_path}")

    try:
        ocr_service = OCRService(config)
        ocr_result = ocr_service.process_image(test_image_path)
        text = ocr_service.get_text_with_confidence_filter(ocr_result, threshold=0.8)
        logger.info("OCR Text extraction completed successfully.")
        print("\nFull OCR Text Output:\n")
        print(text)
        sys.stdout.flush()
        return text
    except Exception as e:
        logger.error(f"Exception during Azure OCR service test: {e}")
        return ""

if __name__ == "__main__":
    extracted_text = test_azure_ocr_connection()
    if extracted_text:
        print("\n=== OCR Extraction Result ===")
        print(extracted_text)
    else:
        print("\nOCR Extraction failed or no text extracted.")
