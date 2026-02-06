import os
import unittest
from pathlib import Path
import sys

# Add workspace src path for module imports
WORKSPACE_ROOT = Path(r"C:/Users/ghendrick/PhotoProject")
SRC_PATH = WORKSPACE_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from record_catalog.config_manager import ConfigManager
from record_catalog.image_processor import ImageProcessor

class TestImageProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Provide explicit path to config.yaml to ConfigManager
        config_path = WORKSPACE_ROOT / "src" / "config.yaml"
        cls.config = ConfigManager(config_path=str(config_path))
        # Instantiate ImageProcessor with config instance (expects one argument)
        cls.image_processor = ImageProcessor(cls.config)

    def test_batch_resize_images(self):
        # Input and OCR folders should be obtained by ImageProcessor from config internally
        input_folder = self.config.get("SOURCE_PHOTO_FOLDER", "dev_data/record_catalog/data/inbox_photos")
        ocr_folder = self.config.get("OCR_IMAGE_FOLDER", "dev_data/record_catalog/data/inbox_photos_ocr")

        if not input_folder or not os.path.isdir(input_folder):
            self.skipTest(f"Input folder not found: {input_folder}")

        if ocr_folder is None:
            self.skipTest("OCR folder path is None, cannot proceed with batch_resize_images")

        resized_images = self.image_processor.batch_resize_images(input_folder, ocr_folder)

        self.assertTrue(os.path.isdir(ocr_folder), f"OCR folder not found after processing: {ocr_folder}")
        self.assertTrue(len(resized_images) > 0, "No images were resized in batch_resize_images")

if __name__ == "__main__":
    unittest.main()
