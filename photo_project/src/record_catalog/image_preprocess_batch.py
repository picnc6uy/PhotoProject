import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from PIL import Image, ImageOps, ImageFilter
import cv2


class ImagePreprocessBatch:
    """Batch process images for OCR preprocessing, resizing, and saving."""

    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('ImagePreprocessBatch')
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Azure OCR constraints
        self.azure_max_dim = 4200
        self.azure_max_bytes = 4_000_000  # 4MB
        self.jpeg_quality = 85

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Apply grayscale, CLAHE, denoising, adaptive threshold, morphology close, sharpening."""
        # Convert to grayscale
        gray = ImageOps.grayscale(image)
        img_np = cv2.cvtColor(np.array(gray), cv2.COLOR_GRAY2BGR)
        img_gray_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)  # Just to be safe

        # CLAHE (local contrast)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(img_gray_np)

        # Bilateral filter denoise
        denoised = cv2.bilateralFilter(clahe_img, d=5, sigmaColor=75, sigmaSpace=75)

        # Adaptive threshold
        binarized = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15,
            10
        )

        # Morphological close
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        morph_close = cv2.morphologyEx(binarized, cv2.MORPH_CLOSE, kernel)

        # Convert back to PIL Image
        pil_img = Image.fromarray(morph_close)

        # Sharpen
        sharpened = pil_img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

        return sharpened

    def resize_image(self, image: Image.Image) -> Image.Image:
        """Resize image to Azure max dimension."""
        width, height = image.size
        max_side = max(width, height)
        if max_side > self.azure_max_dim:
            scale = self.azure_max_dim / max_side
            new_dims = (int(width * scale), int(height * scale))
            image = image.resize(new_dims, Image.LANCZOS)
        return image

    def save_image_with_compression(self, image: Image.Image, path: Path):
        """Save JPEG with compression, ensuring under Azure size limit."""
        quality = self.jpeg_quality
        image.save(path, format='JPEG', quality=quality)
        size = path.stat().st_size

        while size > self.azure_max_bytes and quality > 10:
            quality -= 5
            image.save(path, format='JPEG', quality=quality)
            size = path.stat().st_size
            self.logger.info(f"Compressed {path.name} to quality {quality}, size {size} bytes")

        while size > self.azure_max_bytes and \
                (image.width > 100 and image.height > 100):
            scale = 0.95
            new_w = int(image.width * scale)
            new_h = int(image.height * scale)
            image = image.resize((new_w, new_h), Image.LANCZOS)
            image.save(path, format='JPEG', quality=quality)
            size = path.stat().st_size
            self.logger.info(f"Resized {path.name} to {new_w}x{new_h}, size {size} bytes")

        return image, size

    def process_batch(self) -> List[Path]:
        """Process all images in input_dir and save to output_dir."""
        supported_exts = [".png", ".jpg", ".jpeg", ".bmp"]
        saved_paths = []

        for file_path in self.input_dir.iterdir():
            if file_path.suffix.lower() not in supported_exts:
                self.logger.info(f"Skipping unsupported file: {file_path.name}")
                continue

            try:
                self.logger.info(f"Processing {file_path.name}")
                with Image.open(file_path) as img:
                    preprocessed = self.preprocess_image(img)
                    resized = self.resize_image(preprocessed)

                    save_path = self.output_dir / file_path.name
                    processed_img, final_size = self.save_image_with_compression(resized, save_path)

                    self.logger.info(f"Saved {save_path} ({final_size} bytes)")
                    saved_paths.append(save_path)

            except Exception as e:
                self.logger.error(f"Error processing {file_path.name}: {e}")

        self.logger.info(f"Processed {len(saved_paths)} images.")
        return saved_paths


# If run as main, do an example batch process
if __name__ == "__main__":
    import numpy as np

    base_path = Path(r"C:\Users\ghendrick\PhotoProject")
    input_dir = base_path / "dev_data" / "record_catalog" / "data" / "inbox_photos"
    output_dir = base_path / "dev_data" / "record_catalog" / "data" / "inbox_photos_preprocessed"

    processor = ImagePreprocessBatch(str(input_dir), str(output_dir))
    processor.process_batch()
