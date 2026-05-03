import logging
import sys
from pathlib import Path
from typing import Optional

import pytest

from record_catalog.config_manager import ConfigManager
from record_catalog.ocr_service import OCRService

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}


def _select_test_image(ocr_folder: Path) -> Optional[Path]:
    for candidate in sorted(ocr_folder.iterdir()):
        if candidate.suffix.lower() in _IMAGE_EXTENSIONS and candidate.is_file():
            return candidate
    return None


def _run_azure_ocr_connection(config_path: Path, image_path: Path) -> str:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    logger = logging.getLogger("AzureConnectionTest")
    logger.info("Testing Azure OCR service connection using image: %s", image_path)

    config = ConfigManager(config_path=str(config_path))
    ocr_service = OCRService(config)

    ocr_result = ocr_service.process_image(str(image_path))
    if not isinstance(ocr_result, dict):
        raise ValueError("OCR service did not return a dict response.")

    text = ocr_service.get_text_with_confidence_filter(ocr_result, threshold=0.8)
    if not isinstance(text, str):
        raise ValueError("Filtered OCR text was not a string.")

    return text or ocr_result.get("text", "")


@pytest.mark.integration
def test_azure_ocr_connection(workspace_root, ocr_folder):
    config_path = Path(workspace_root) / "src" / "config.yaml"
    test_image = _select_test_image(Path(ocr_folder))
    if test_image is None:
        pytest.skip("No OCR images available for Azure OCR connection test.")

    try:
        text = _run_azure_ocr_connection(config_path, test_image)
    except Exception as exc:  # pragma: no cover - integration failure information
        pytest.fail(f"Azure OCR connection failed: {exc!r}")

    assert isinstance(text, str)


if __name__ == "__main__":
    workspace_root = Path(__file__).resolve().parents[2]
    ocr_folder = workspace_root / "dev_data" / "record_catalog" / "data" / "inbox_photos_ocr"
    config_path = workspace_root / "src" / "config.yaml"

    if not ocr_folder.exists():
        print(f"OCR folder does not exist: {ocr_folder}")
        sys.exit(0)

    image = _select_test_image(ocr_folder)
    if image is None:
        print("No OCR images available for manual Azure OCR test.")
        sys.exit(0)

    try:
        extracted_text = _run_azure_ocr_connection(config_path, image)
    except Exception as exc:
        print(f"Azure OCR connection failed: {exc}")
        sys.exit(1)

    if extracted_text:
        print("\n=== OCR Extraction Result ===")
        print(extracted_text)
    else:
        print("\nOCR Extraction completed, but no text was extracted.")
