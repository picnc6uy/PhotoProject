import os
from pathlib import Path
import sys
from PIL import Image

# Adjust sys.path to include project root for imports
cwd = Path(__file__).parent.resolve()
project_root = cwd.parent.resolve()
sys.path.insert(0, str(project_root))


def run_process_test(input_folder: str, output_folder: str):
    if not os.path.exists(input_folder):
        print(f"Error: Input folder does not exist: {input_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    processed_files = []

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    print(f"Found {len(files)} image files to process.")

    for filename in files:
        source_path = os.path.join(input_folder, filename)
        with Image.open(source_path) as img:
            # For the test, simply convert image to grayscale
            processed_img = img.convert('L')

        # Save to output folder
        output_path = os.path.join(output_folder, filename)
        processed_img.save(output_path, format='PNG')
        print(f"Saved processed image to: {output_path}")
        processed_files.append(output_path)

    print(f"Total processed images saved: {len(processed_files)}")


if __name__ == '__main__':
    base_path = Path(__file__).parent.parent.resolve()
    input_folder = base_path / "dev_data" / "record_catalog" / "data" / "inbox_photos"
    output_folder = base_path / "dev_data" / "record_catalog" / "data" / "inbox_photos_processed"

    run_process_test(str(input_folder), str(output_folder))
