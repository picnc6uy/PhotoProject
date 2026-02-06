import os
import shutil
import unittest
from pathlib import Path

from batch_resize_images import batch_resize_images, ocr_folder

class TestBatchResizeImages(unittest.TestCase):
    test_input_folder = Path(os.path.dirname(__file__)) / "test_images_input"

    @classmethod
    def setUpClass(cls):
        cls.test_input_folder.mkdir(exist_ok=True)
        # Create some dummy image files for testing
        for i in range(3):
            with open(cls.test_input_folder / f"test_image_{i}.jpg", "wb") as f:
                f.write(os.urandom(1024))  # 1KB random bytes as dummy

    @classmethod
    def tearDownClass(cls):
        # Cleanup input test images folder
        shutil.rmtree(cls.test_input_folder)

        # Cleanup OCR output folder
        if os.path.exists(ocr_folder):
            shutil.rmtree(ocr_folder)

    def test_batch_resize_creates_ocr_images(self):
        processed_files = batch_resize_images(str(self.test_input_folder))

        # Check files are created in OCR folder
        for filepath in processed_files:
            self.assertTrue(Path(filepath).exists())
            self.assertTrue(str(filepath).startswith(str(ocr_folder)))

        # Check that returned paths count matches number of input images
        self.assertEqual(len(processed_files), 3)

if __name__ == "__main__":
    unittest.main()
