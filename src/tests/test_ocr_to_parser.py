import csv
from pathlib import Path

import pytest

from record_catalog.config_manager import ConfigManager
from record_catalog.parser import OCRParser


WORKSPACE_ROOT = Path(r"C:/Users/ghendrick/PhotoProject")


@pytest.fixture(scope="session")
def parser():
    config_path = WORKSPACE_ROOT / "src" / "config.yaml"
    config = ConfigManager(str(config_path))
    return OCRParser(config)


def test_parse_ocr_csv(parser):
    config_path = WORKSPACE_ROOT / "src" / "config.yaml"
    config = ConfigManager(str(config_path))
    ocr_csv_path = Path(
        config.get("OCR_PARSED_CSV", "dev_data/record_catalog/data/ocr_texts.csv")
    )

    if not ocr_csv_path.exists():
        pytest.skip(f"OCR CSV not found at {ocr_csv_path}, please run OCR test first.")

    with ocr_csv_path.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row.get("filename")
            ocr_text = row.get("ocr_text", "")
            parsed_metadata = parser.parse_text(ocr_text)

            assert isinstance(parsed_metadata, dict), f"Parsed result for {filename} is not a dict"
            assert "Catalog Number" in parsed_metadata, f"Catalog Number missing for {filename}"

            catalog_num = parsed_metadata.get("Catalog Number")
            if catalog_num is not None:
                assert isinstance(catalog_num, str), f"Catalog Number for {filename} is not a string"
                assert len(catalog_num) > 0, f"Catalog Number for {filename} is empty string"
