import os
import logging
from record_catalog.image_processor import ImageProcessor
from record_catalog.config_manager import ConfigManager
from PIL import Image

source_folder = (
    r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos"
)
ocr_folder = (
    r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos_ocr"
)

# Set up logging with level and format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

os.makedirs(ocr_folder, exist_ok=True)


def batch_resize_images(folder_path, ocr_output_folder, config=None):
    """
    Runs batch image preprocessing and resizing for OCR on all images in the given folder.
    Saves processed images to ocr_output_folder.

    Args:
        folder_path (str): Path to folder containing source images.
        ocr_output_folder (str): Path where preprocessed images are saved.

    Returns:
        list of str: Paths of processed images.
    """
    processor = ImageProcessor(config or {})  # Use config when provided
    processed_files = []

    original_sizes = []
    preprocessed_sizes = []
    filenames = []

    # Preprocessing step, save images to OCR folder
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            logging.debug(f"Skipping {filename}: Unsupported file type.")
            continue
        try:
            source_path = os.path.join(folder_path, filename)

            # Get original file size
            orig_size = os.path.getsize(source_path)

            # Preprocess and save
            preprocessed_path = processor.resize_image_for_ocr(
                source_path, ocr_output_folder
            )
            preproc_size = os.path.getsize(preprocessed_path)

            filenames.append(filename)
            original_sizes.append(orig_size)
            preprocessed_sizes.append(preproc_size)

            logging.info(
                f"Processed {filename}: Original={orig_size} bytes, Preprocessed={preproc_size} bytes"
            )

        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")
            continue

    # Print table of original vs preprocessed sizes
    logging.info("\n=== Original vs Preprocessed Image Sizes ===")
    logging.info(
        f"{'Filename':<25} {'Original Size (bytes)':>20} {'Preprocessed Size (bytes)':>25}"
    )
    logging.info("-" * 70)
    for f, o, p in zip(filenames, original_sizes, preprocessed_sizes):
        logging.info(f"{f:<25} {o:>20} {p:>25}")

    # Resize if necessary to meet Azure max byte limits
    for filename, preprocessed_size in zip(filenames, preprocessed_sizes):
        preprocessed_path = os.path.join(ocr_output_folder, filename)

        if preprocessed_size > processor.azure_max_image_bytes:
            try:
                with Image.open(preprocessed_path) as img:
                    scale = 0.95
                    size_bytes = preprocessed_size

                    while size_bytes > processor.azure_max_image_bytes:
                        new_width = int(img.width * scale)
                        new_height = int(img.height * scale)
                        img = img.resize((new_width, new_height), Image.LANCZOS)

                        img.save(
                            preprocessed_path,
                            format="JPEG",
                            quality=processor.jpeg_quality,
                        )
                        size_bytes = os.path.getsize(preprocessed_path)
                        logging.info(
                            f"Resized further: {filename}, size={size_bytes} bytes, dimensions=({new_width},{new_height})"
                        )
                        scale *= 0.95
            except Exception as e:
                logging.error(f"Error resizing {filename}: {e}")
                continue
        processed_files.append(preprocessed_path)

    logging.info(
        f"Batch preprocess and resizing complete, processed {len(processed_files)} images."
    )
    return processed_files


if __name__ == "__main__":
    logging.info("Starting batch image preprocessing and resizing pipeline...")
    config_path = r"C:\Users\ghendrick\PhotoProject\src\config.yaml"
    config = ConfigManager(config_path)
    processed = batch_resize_images(source_folder, ocr_folder, config)
    logging.info(f"Processed files: {processed}")
    logging.info("Pipeline complete.")
