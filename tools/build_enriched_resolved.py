import os
from pathlib import Path

from record_catalog.resolved_builder import build_resolved_enriched
from record_catalog.config_manager import ConfigManager


def main():
    workspace = Path(r"C:/Users/ghendrick/PhotoProject")
    config_path = workspace / "src" / "config.yaml"
    config = ConfigManager(str(config_path))

    parsed_csv = Path(config.get("PARSED_METADATA_CSV", "dev_data/record_catalog/data/parsed_metadata.csv"))
    candidates_csv = Path(
        config.get(
            "ENRICHMENT_CANDIDATES_CSV",
            "dev_data/record_catalog/data/outputs/enrichment_candidates.csv",
        )
    )
    output_csv = Path(
        config.get(
            "ENRICHED_RESOLVED_CSV",
            "dev_data/record_catalog/data/outputs/enriched_resolved.csv",
        )
    )

    count = build_resolved_enriched(
        str(parsed_csv),
        str(candidates_csv),
        str(output_csv),
        str(config_path),
    )
    print(f"Wrote {count} resolved rows to {output_csv}")


if __name__ == "__main__":
    os.environ.setdefault("PYTHONPATH", "src")
    main()
