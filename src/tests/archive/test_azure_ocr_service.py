import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from record_catalog.config_manager import ConfigManager
from record_catalog.ocr_service import OCRService

# Use a sample test image path - adjust if you have a valid small image for quick OCR test
TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_image.jpg")


def test_azure_ocr_service():
    config = ConfigManager()
    ocr_service = OCRService(config)
    if not config.get("AZURE_COMPUTER_VISION_KEY") or not config.get("AZURE_COMPUTER_VISION_ENDPOINT"):
        print("Azure OCR keys are not set in environment or config. Test aborted.")
        return

    try:
        result = ocr_service.process_image(TEST_IMAGE_PATH)
        if result and 'text' in result:
            print(f"Azure OCR Service Test Passed: Extracted {len(result['text'])} characters.")
        else:
            print("Azure OCR Service Test Failed: No text extracted.")
    except Exception as e:
        print("Azure OCR Service Test Exception:", e)


if __name__ == "__main__":
    test_azure_ocr_service()
