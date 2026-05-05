import os
from PIL import Image, ImageFilter, ImageOps
from PIL.Image import Resampling
import numpy as np
import cv2

try:
    resample_method = Resampling.LANCZOS
except AttributeError:
    resample_method = Image.LANCZOS

class ImageProcessor:
    """Handles image preprocessing, resizing and preparation for OCR.

    The `preprocess_image_for_ocr` method implements the validated modern preprocessing pipeline
    including grayscale, CLAHE (adaptive histogram equalization), bilateral denoising, and sharpening.
    Thresholding + morphological closing is available in binary mode. Smooth and smooth-plus modes
    are the current defaults and are controlled by PREPROCESS_MODE.
    """

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.max_ocr_dim = config.get('MAX_OCR_DIMENSION', 4200)
        self.jpeg_quality = config.get('JPEG_QUALITY', 85)
        self.azure_max_image_bytes = 4000000  # 4 MB limit for Azure OCR
        # Preprocessing tuning params (configurable)
        self.clahe_clip_limit = float(config.get('CLAHE_CLIP_LIMIT', 2.0))
        self.clahe_tile_grid_size = self._parse_int_pair(config.get('CLAHE_TILE_GRID_SIZE', (8, 8)))
        self.bilateral_d = int(config.get('BILATERAL_D', 5))
        self.bilateral_sigma_color = float(config.get('BILATERAL_SIGMA_COLOR', 75))
        self.bilateral_sigma_space = float(config.get('BILATERAL_SIGMA_SPACE', 75))
        self.adaptive_thresh_block_size = self._ensure_odd_int(config.get('ADAPTIVE_THRESH_BLOCK_SIZE', 15), minimum=3)
        self.adaptive_thresh_c = float(config.get('ADAPTIVE_THRESH_C', 10))
        self.morph_kernel_size = int(config.get('MORPH_KERNEL_SIZE', 3))
        self.sharpen_radius = float(config.get('SHARPEN_RADIUS', 1))
        self.sharpen_percent = int(config.get('SHARPEN_PERCENT', 150))
        self.sharpen_threshold = int(config.get('SHARPEN_THRESHOLD', 3))
        self.preprocess_mode = str(config.get('PREPROCESS_MODE', 'ocr_binary')).strip().lower()
        self.background_kernel_size = int(config.get('BACKGROUND_KERNEL_SIZE', 31))
        self.gamma_correction = float(config.get('GAMMA_CORRECTION', 1.0))
        self.auto_rotate = str(config.get('AUTO_ROTATE', 'false')).strip().lower() == 'true'
        self.auto_rotate_max_deg = float(config.get('AUTO_ROTATE_MAX_DEG', 45.0))

    def _parse_int_pair(self, value):
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return (int(value[0]), int(value[1]))
        if isinstance(value, str) and "," in value:
            parts = value.split(",", maxsplit=1)
            return (int(parts[0].strip()), int(parts[1].strip()))
        return (8, 8)

    def _ensure_odd_int(self, value, minimum=3):
        try:
            val = int(value)
        except (TypeError, ValueError):
            val = minimum
        if val < minimum:
            val = minimum
        if val % 2 == 0:
            val += 1
        return val

    def _apply_gamma(self, img_np, gamma: float):
        if gamma <= 0:
            return img_np
        inv_gamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
        return cv2.LUT(img_np, table)

    def _normalize_background(self, img_np, kernel_size: int):
        kernel_size = self._ensure_odd_int(kernel_size, minimum=3)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        background = cv2.morphologyEx(img_np, cv2.MORPH_OPEN, kernel)
        normalized = cv2.subtract(img_np, background)
        return cv2.normalize(normalized, None, 0, 255, cv2.NORM_MINMAX)

    def _auto_rotate_image(self, img_np):
        edges = cv2.Canny(img_np, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        if lines is None:
            return img_np

        angles = []
        for rho, theta in lines[:, 0]:
            angle = (theta * 180 / np.pi) - 90
            if abs(angle) <= self.auto_rotate_max_deg:
                angles.append(angle)

        if not angles:
            return img_np

        median_angle = float(np.median(angles))
        if abs(median_angle) < 1:
            return img_np

        (h, w) = img_np.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        return cv2.warpAffine(img_np, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    def preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        # Normalize orientation based on EXIF data when available
        image = ImageOps.exif_transpose(image)

        # Convert to grayscale
        gray = ImageOps.grayscale(image)

        # Convert to numpy array for OpenCV
        img_np = np.array(gray)

        # Apply CLAHE (local contrast enhancement)
        clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip_limit,
            tileGridSize=self.clahe_tile_grid_size
        )
        clahe_img = clahe.apply(img_np)

        # Denoise with mild bilateral filter (preserves edges better than median)
        denoised = cv2.bilateralFilter(
            clahe_img,
            d=self.bilateral_d,
            sigmaColor=self.bilateral_sigma_color,
            sigmaSpace=self.bilateral_sigma_space
        )

        if self.auto_rotate:
            denoised = self._auto_rotate_image(denoised)

        if self.preprocess_mode == "ocr_smooth_plus":
            bg_flat = self._normalize_background(denoised, self.background_kernel_size)
            gamma_adj = self._apply_gamma(bg_flat, self.gamma_correction)
            pil_img = Image.fromarray(gamma_adj)
        elif self.preprocess_mode == "ocr_smooth":
            # Keep grayscale detail, avoid binarization artifacts
            pil_img = Image.fromarray(denoised)
        else:
            # Adaptive thresholding for binarization
            binarized = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self.adaptive_thresh_block_size,
                self.adaptive_thresh_c
            )

            # Morphological close operation to close gaps between letters
            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE,
                (self.morph_kernel_size, self.morph_kernel_size)
            )
            morph_close = cv2.morphologyEx(binarized, cv2.MORPH_CLOSE, kernel)

            # Convert back to PIL Image
            pil_img = Image.fromarray(morph_close)

        # Sharpening filter
        sharpened = pil_img.filter(
            ImageFilter.UnsharpMask(
                radius=self.sharpen_radius,
                percent=self.sharpen_percent,
                threshold=self.sharpen_threshold
            )
        )

        return sharpened

    def resize_and_save(self, image_path: str, target_folder: str, max_dimension: int) -> str:
        filename = os.path.basename(image_path)
        target_path = os.path.join(target_folder, filename)
        with Image.open(image_path) as img:
            # Always preprocess with OCR steps now
            img = self.preprocess_image_for_ocr(img)

            width, height = img.size
            max_side = max(width, height)
            if max_side > max_dimension:
                scale = max_dimension / max_side
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = img.resize((new_width, new_height), resample_method)

            img.save(target_path, format='JPEG', quality=self.jpeg_quality)
            size_bytes = os.path.getsize(target_path)

            if size_bytes > self.azure_max_image_bytes:
                print(f"Resized image {filename} size {size_bytes} bytes exceeds Azure OCR max size, compressing or rescaling...")
                quality = self.jpeg_quality
                while size_bytes > self.azure_max_image_bytes and quality > 10:
                    quality -= 5
                    img.save(target_path, format='JPEG', quality=quality)
                    size_bytes = os.path.getsize(target_path)
                    print(f"Compressed to quality {quality}, new size {size_bytes} bytes")

                # If still too big, scale down iteratively until below safe limit
                safe_limit_bytes = int(self.azure_max_image_bytes * 0.95)  # Lower than 4MB
                scale_down_factor = 0.95
                while size_bytes > safe_limit_bytes and (img.width * scale_down_factor > 100 and img.height * scale_down_factor > 100):
                    new_w = int(img.width * scale_down_factor)
                    new_h = int(img.height * scale_down_factor)
                    img = img.resize((new_w, new_h), resample_method)
                    img.save(target_path, format='JPEG', quality=quality)
                    size_bytes = os.path.getsize(target_path)
                    print(f"Rescaled image to {new_w}x{new_h}, size now {size_bytes} bytes")
                    scale_down_factor *= 0.95

            return target_path

    def resize_image_for_ocr(self, image_path: str, target_folder: str) -> str:
        return self.resize_and_save(image_path, target_folder, self.max_ocr_dim)

    def batch_resize_images(self, folder_path: str, ocr_folder: str) -> list[str]:
        os.makedirs(ocr_folder, exist_ok=True)

        # Clean up existing files in OCR folder
        for existing_file in os.listdir(ocr_folder):
            existing_path = os.path.join(ocr_folder, existing_file)
            if os.path.isfile(existing_path):
                os.remove(existing_path)

        resized_paths = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                source_path = os.path.join(folder_path, filename)
                ocr_path = self.resize_image_for_ocr(source_path, ocr_folder)
                ocr_size = os.path.getsize(ocr_path)
                print(f"OCR image {filename} size: {ocr_size} bytes")
                resized_paths.append(ocr_path)
        return resized_paths
