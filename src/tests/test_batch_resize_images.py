import os
from pathlib import Path

import pytest

from record_catalog.config_manager import ConfigManager
from batch_resize_images import batch_resize_images


WORKSPACE_ROOT = Path(r"C:/Users/ghendrick/PhotoProject")


@pytest.fixture(scope="session")
def config():
    config_path = WORKSPACE_ROOT / "src" / "config.yaml"
    return ConfigManager(str(config_path))


def test_batch_resize_creates_ocr_images(config, tmp_path):
    source_folder = Path(config.get("SOURCE_PHOTO_FOLDER"))
    if not source_folder.is_dir():
        pytest.skip(f"Source folder not found: {source_folder}")

    ocr_folder = tmp_path / "ocr_images"
    ocr_folder.mkdir(parents=True, exist_ok=True)

    processed_files = batch_resize_images(str(source_folder), str(ocr_folder), config)

    assert processed_files, "No images were processed."
    for filepath in processed_files:
        path = Path(filepath)
        assert path.exists()
        assert str(path).startswith(str(ocr_folder))
