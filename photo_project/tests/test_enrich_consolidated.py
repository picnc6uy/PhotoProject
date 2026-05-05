import csv
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from record_catalog.config_manager import ConfigManager
from record_catalog.enricher import MetadataEnricher


WORKSPACE_ROOT = Path(r"C:/Users/ghendrick/PhotoProject")


def test_enrich_and_save():
    config_path = WORKSPACE_ROOT / "src" / "config.yaml"
    config = ConfigManager(str(config_path))
    enricher = MetadataEnricher(config)

    parsed_csv_path = Path(
        config.get("PARSED_METADATA_CSV", "dev_data/record_catalog/data/parsed_metadata.csv")
    )
    if not parsed_csv_path.exists():
        pytest.skip(f"Parsed CSV file {parsed_csv_path} not found. Run parsing first.")

    outputs_dir = WORKSPACE_ROOT / "dev_data" / "record_catalog" / "data" / "outputs" / "tests"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    enriched_csv_path = outputs_dir / "enriched_metadata.csv"

    enriched_data = []

    with parsed_csv_path.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row.get("filename")
            enriched = enricher.enrich_metadata(row)
            enriched["filename"] = filename
            enriched_data.append(enriched)

    if not enriched_data:
        pytest.skip("No enriched data to save.")

    keys = set()
    for data in enriched_data:
        keys.update(data.keys())
    fieldnames = sorted(keys)

    with enriched_csv_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in enriched_data:
            row = {k: (", ".join(v) if isinstance(v, list) else v) for k, v in data.items()}
            writer.writerow(row)

    assert enriched_csv_path.exists()
