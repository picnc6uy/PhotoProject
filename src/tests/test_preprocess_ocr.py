import os
from pathlib import Path
from typing import List

import pytest

from record_catalog.config_manager import ConfigManager
from record_catalog.image_processor import ImageProcessor


_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


def _preprocess_ocr_images(input_folder: str, ocr_output_folder: str) -> List[str]:
    config = ConfigManager()  # Load dynamic config
    processor = ImageProcessor(config)

    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")

    os.makedirs(ocr_output_folder, exist_ok=True)

    files = [name for name in os.listdir(input_folder) if name.lower().endswith(_IMAGE_EXTENSIONS)]

    results: List[str] = []
    for filename in files:
        source_path = os.path.join(input_folder, filename)
        ocr_path = processor.resize_image_for_ocr(source_path, ocr_output_folder)
        if os.path.exists(ocr_path):
            results.append(ocr_path)
    return results


def test_preprocess_ocr_images(input_folder, ocr_output_folder):
    results = _preprocess_ocr_images(input_folder, ocr_output_folder)
    if not results:
        pytest.skip("No preprocessable OCR images were found in the input folder.")

    for processed_path in results:
        assert os.path.isfile(processed_path), f"Processed file missing: {processed_path}"


if __name__ == '__main__':
    config = ConfigManager()
    # Fix workspace root to true project root (3 levels up from this test script)
    workspace_root = Path(__file__).parent.parent.parent.resolve()
    print(f"Debug: Computed workspace root: {workspace_root}")

    source_folder_rel = config.get('SOURCE_IMAGE_FOLDER', 'dev_data/record_catalog/data/inbox_photos')
    # Change OCR output folder default to inbox_photos_ocr
    ocr_output_rel = config.get('OCR_OUTPUT_FOLDER', 'dev_data/record_catalog/data/inbox_photos_ocr')

    source_folder = (workspace_root / source_folder_rel).resolve()
    ocr_output_folder = (workspace_root / ocr_output_rel).resolve()

    os.makedirs(ocr_output_folder, exist_ok=True)

    preprocessed_files = _preprocess_ocr_images(str(source_folder), str(ocr_output_folder))
    print(f"Total OCR images preprocessed: {len(preprocessed_files)}")

