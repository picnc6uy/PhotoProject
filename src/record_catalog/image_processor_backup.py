import os
from PIL import Image

class ImageProcessor:
    """Handles image preprocessing, resizing and preparation for OCR."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.max_ocr_dim = config.get('MAX_OCR_DIMENSION', 4200)
        self.jpeg_quality = config.get('JPEG_QUALITY', 85)
        self.azure_max_image_bytes = 4000000  # 4 MB limit for Azure OCR

    def resize_and_save(self, image_path: str, target_folder: str, max_dimension: int) -> str:
        """Resize and save an image to the target folder ensuring Azure OCR size limits for OCR images."""
        filename = os.path.basename(image_path)
        target_path = os.path.join(target_folder, filename)
        with Image.open(image_path) as img:
            width, height = img.size
            max_side = max(width, height)
            if max_side > max_dimension:
                scale = max_dimension / max_side
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = img.resize((new_width, new_height), Image.LANCZOS)

            # First save
            img.save(target_path, format='JPEG', quality=self.jpeg_quality)
            size_bytes = os.path.getsize(target_path)

            # For OCR images, try to keep size under Azure 4MB limit
            if max_dimension == self.max_ocr_dim and size_bytes > self.azure_max_image_bytes:
                print(f"Resized image {filename} size {size_bytes} bytes exceeds Azure OCR max size, compressing or rescaling...")
                quality = self.jpeg_quality
                while size_bytes > self.azure_max_image_bytes and quality > 10:
                    quality -= 5
                    img.save(target_path, format='JPEG', quality=quality)
                    size_bytes = os.path.getsize(target_path)
                    print(f"Compressed to quality {quality}, new size {size_bytes} bytes")
                if size_bytes > self.azure_max_image_bytes:
                    # Further scale down if needed
                    scale_down_factor = 0.9
                    while size_bytes > self.azure_max_image_bytes and (img.width * scale_down_factor > 100 and img.height * scale_down_factor > 100):
                        new_w = int(img.width * scale_down_factor)
                        new_h = int(img.height * scale_down_factor)
                        img = img.resize((new_w, new_h), Image.LANCZOS)
                        img.save(target_path, format='JPEG', quality=quality)
                        size_bytes = os.path.getsize(target_path)
                        print(f"Rescaled image to {new_w}x{new_h}, size now {size_bytes} bytes")
                        scale_down_factor *= 0.9

            return target_path

    def resize_image_for_ocr(self, image_path: str, target_folder: str) -> str:
        return self.resize_and_save(image_path, target_folder, self.max_ocr_dim)

    def batch_resize_images(self, folder_path: str, ocr_folder: str) -> list[str]:
        """Process batch of images in given folder into OCR folder."""
        os.makedirs(ocr_folder, exist_ok=True)
        resized_paths = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                source_path = os.path.join(folder_path, filename)
                ocr_path = self.resize_image_for_ocr(source_path, ocr_folder)
                resized_paths.append(ocr_path)
        return resized_paths
