from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def workspace_root() -> Path:
    """Return the repository workspace root."""
    return Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def input_folder(workspace_root: Path) -> str:
    """Default source image folder for OCR preprocessing tests."""
    folder = workspace_root / "dev_data" / "record_catalog" / "data" / "inbox_photos"
    if not folder.exists():
        pytest.skip("Source inbox_photos folder is not available in the workspace.")
    return str(folder)


@pytest.fixture(scope="session")
def ocr_output_folder(workspace_root: Path) -> str:
    """Destination folder for OCR-ready images, ensured to exist."""
    folder = workspace_root / "dev_data" / "record_catalog" / "data" / "inbox_photos_ocr"
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder)


@pytest.fixture(scope="session")
def ocr_folder(workspace_root: Path) -> str:
    """Folder containing images ready for OCR service integration tests."""
    folder = workspace_root / "dev_data" / "record_catalog" / "data" / "inbox_photos_ocr"
    if not folder.exists():
        pytest.skip("OCR inbox folder is not available in the workspace.")
    return str(folder)
