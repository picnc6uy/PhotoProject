import os
from pathlib import Path
from record_catalog.config_manager import ConfigManager
from record_catalog.image_processor import ImageProcessor


def test_preprocess_ocr_images(input_folder, ocr_output_folder):
    config = ConfigManager()  # Load dynamic config
    processor = ImageProcessor(config)

    print(f"Debug: OCR image input folder: {input_folder}")
    if not os.path.exists(input_folder):
        print(f"Error: Input folder does not exist: {input_folder}")
        return []

    files = os.listdir(input_folder)
    if not files:
        print("Warning: Input folder is empty.")
    else:
        print(f"Found {len(files)} files in input folder.")
        for f in files:
            print(f" - {f}")

    # Preprocess OCR images
    results = []
    for filename in files:
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            source_path = os.path.join(input_folder, filename)
            ocr_path = processor.resize_image_for_ocr(source_path, ocr_output_folder)
            size_bytes = os.path.getsize(ocr_path)
            print(f"OCR image {filename} resized and saved to: {ocr_path} (size: {size_bytes} bytes)")
            results.append(ocr_path)
    return results


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

    preprocessed_files = test_preprocess_ocr_images(str(source_folder), str(ocr_output_folder))
    print(f"Total OCR images preprocessed: {len(preprocessed_files)}")

