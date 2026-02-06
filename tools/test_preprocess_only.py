import os
from pathlib import Path
import sys

# Adjust sys.path to include project root for imports
cwd = Path(__file__).parent.resolve()
project_root = cwd.parent.resolve()
sys.path.insert(0, str(project_root))

from PIL import Image
from record_catalog.config_manager import ConfigManager
from record_catalog.image_processor import ImageProcessor


def run_preprocess_test(input_folder: str, output_folder: str):
    if not os.path.exists(input_folder):
        print(f"Error: Input folder does not exist: {input_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    config = ConfigManager()  # Load config
    processor = ImageProcessor(config)

    processed_files = []

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    print(f"Found {len(files)} image files to preprocess.")

    for filename in files:
        source_path = os.path.join(input_folder, filename)
        with Image.open(source_path) as img:
            processed_img = processor.preprocess_image_for_ocr(img)

        # Save to output folder
        output_path = os.path.join(output_folder, filename)
        processed_img.save(output_path, format='PNG')
        print(f"Saved preprocessed image to: {output_path}")
        processed_files.append(output_path)

    print(f"Total preprocessed images saved: {len(processed_files)}")


if __name__ == '__main__':
    input_folder = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos"
    output_folder = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos_preprocessed"

    run_preprocess_test(input_folder, output_folder)
