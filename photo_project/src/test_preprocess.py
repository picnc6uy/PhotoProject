import os
from pathlib import Path
from record_catalog.image_processor import ImageProcessor
import yaml

# Load config from src/config.yaml
config_path = Path(__file__).parent / "config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize ImageProcessor
processor = ImageProcessor(config)

# Define input and output folders
input_folder = Path("dev_data/sample_images")  # Change this path as needed
desc_output_folder = Path("dev_data/desc_out")
ocr_output_folder = Path("dev_data/ocr_out")

# Create output folders if not exist
desc_output_folder.mkdir(parents=True, exist_ok=True)
ocr_output_folder.mkdir(parents=True, exist_ok=True)

print(f"Starting batch resize and preprocessing from {input_folder}")

# Run batch resize and preprocessing
resized_paths = processor.batch_resize_images(str(input_folder), str(desc_output_folder), str(ocr_output_folder))

print(f"Completed batch processing. Processed {len(resized_paths)} images.")

for desc_path, ocr_path in resized_paths:
    print(f"Description image saved: {desc_path}")
    print(f"OCR image saved: {ocr_path}")
