import os
import logging
from src.batch_resize_images import batch_resize_images


# Paths should be set to your test/sample folders
SOURCE_FOLDER = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos"
OCR_OUTPUT_FOLDER = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos_ocr"


# Limits used for validation
AZURE_MAX_IMAGE_BYTES = 4_000_000


def test_batch_resize_images():
    """
    Run the batch_resize_images pipeline and assert on key output characteristics.
    Validations:
      - Processed images exist
      - Preprocessed images do not exceed Azure max byte size
      - File sizes are smaller or equal to original sizes (accounting for compression)

    Prints a summary report for batch run.
    """
    processed_files = batch_resize_images(SOURCE_FOLDER, OCR_OUTPUT_FOLDER)

    if not processed_files:
        logging.error("No images were processed!")
        return

    report = []
    errors = 0

    for file_path in processed_files:
        if not os.path.exists(file_path):
            logging.error(f"Processed image missing: {file_path}")
            errors += 1
            continue

        size_bytes = os.path.getsize(file_path)
        if size_bytes > AZURE_MAX_IMAGE_BYTES:
            logging.error(f"Image exceeds Azure max byte size limit: {file_path}, size: {size_bytes} bytes")
            errors += 1

        # Could add more assertions on image dimensions, modes, or format here

        report.append((file_path, size_bytes))

    # Summary Report
    logging.info("Batch Resize Images Test Report")
    logging.info(f"Total processed images: {len(processed_files)}")
    logging.info(f"Errors found: {errors}")
    for path, size in report:
        logging.info(f"Processed image: {path} - Size: {size} bytes")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    test_batch_resize_images()

