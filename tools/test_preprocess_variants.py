import os
from pathlib import Path
import sys

# Adjust sys.path to include project root and src for imports
cwd = Path(__file__).parent.resolve()
project_root = cwd.parent.resolve()
src_root = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

from PIL import Image
from record_catalog.image_processor import ImageProcessor


def preprocess_images(input_folder: str, output_folder: str, config: dict, limit: int = 3):
    if not os.path.exists(input_folder):
        print(f"Error: Input folder does not exist: {input_folder}")
        return []

    os.makedirs(output_folder, exist_ok=True)

    processor = ImageProcessor(config)
    processed_files = []

    files = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
    ]
    files.sort()
    files = files[:limit]
    print(f"Found {len(files)} image files to preprocess.")

    for filename in files:
        source_path = os.path.join(input_folder, filename)
        with Image.open(source_path) as img:
            processed_img = processor.preprocess_image_for_ocr(img)

        output_path = os.path.join(output_folder, filename)
        processed_img.save(output_path, format="PNG")
        print(f"Saved preprocessed image to: {output_path}")
        processed_files.append(output_path)

    return processed_files


if __name__ == "__main__":
    input_folder = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos"
    base_output = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\outputs\preprocess_compare"

    baseline_output = os.path.join(base_output, "baseline")
    tuned_output = os.path.join(base_output, "tuned")

    # Baseline uses smooth mode for comparison
    print("Running smooth preprocessing...")
    smooth_config = {
        "PREPROCESS_MODE": "ocr_smooth",
        "CLAHE_CLIP_LIMIT": 3.0,
        "CLAHE_TILE_GRID_SIZE": (8, 8),
        "BILATERAL_D": 7,
        "BILATERAL_SIGMA_COLOR": 90,
        "BILATERAL_SIGMA_SPACE": 90,
        "ADAPTIVE_THRESH_BLOCK_SIZE": 21,
        "ADAPTIVE_THRESH_C": 5,
        "MORPH_KERNEL_SIZE": 3,
        "SHARPEN_RADIUS": 1.2,
        "SHARPEN_PERCENT": 130,
        "SHARPEN_THRESHOLD": 3,
    }
    preprocess_images(input_folder, baseline_output, config=smooth_config, limit=3)

    # Tuned parameters for smoother, higher-contrast output with background normalization
    tuned_config = {
        "PREPROCESS_MODE": "ocr_smooth_plus",
        "CLAHE_CLIP_LIMIT": 3.0,
        "CLAHE_TILE_GRID_SIZE": (8, 8),
        "BILATERAL_D": 7,
        "BILATERAL_SIGMA_COLOR": 90,
        "BILATERAL_SIGMA_SPACE": 90,
        "ADAPTIVE_THRESH_BLOCK_SIZE": 21,
        "ADAPTIVE_THRESH_C": 5,
        "MORPH_KERNEL_SIZE": 3,
        "SHARPEN_RADIUS": 1.2,
        "SHARPEN_PERCENT": 130,
        "SHARPEN_THRESHOLD": 3,
        "BACKGROUND_KERNEL_SIZE": 31,
        "GAMMA_CORRECTION": 1.1,
    }

    print("Running tuned preprocessing...")
    preprocess_images(input_folder, tuned_output, config=tuned_config, limit=3)

    print(f"Baseline outputs: {baseline_output}")
    print(f"Tuned outputs: {tuned_output}")
