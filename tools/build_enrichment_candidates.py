import os
from pathlib import Path

from record_catalog.candidate_ranker import build_enrichment_candidates
from record_catalog.config_manager import ConfigManager


def main():
    workspace = Path(r"C:/Users/ghendrick/PhotoProject")
    config_path = workspace / "src" / "config.yaml"
    config = ConfigManager(str(config_path))

    parsed_csv = Path(config.get("PARSED_METADATA_CSV", "dev_data/record_catalog/data/parsed_metadata.csv"))
    suggestions_csv = Path(
        config.get(
            "REVIEW_SUGGESTIONS_CSV",
            "dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv",
        )
    )
    output_csv = Path(
        config.get(
            "ENRICHMENT_CANDIDATES_CSV",
            "dev_data/record_catalog/data/outputs/enrichment_candidates.csv",
        )
    )

    count = build_enrichment_candidates(
        str(parsed_csv),
        str(suggestions_csv),
        str(output_csv),
        discogs_token=config.get("DISCOGS_TOKEN", ""),
        user_agent=config.get("MUSICBRAINZ_USER_AGENT", "RecordCatalogApp/1.0"),
    )
    print(f"Wrote {count} candidate rows to {output_csv}")


if __name__ == "__main__":
    os.environ.setdefault("PYTHONPATH", "src")
    main()
