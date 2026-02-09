import csv
import os
from pathlib import Path

from record_catalog.config_manager import ConfigManager
from record_catalog.enricher import MetadataEnricher


def main():
    workspace = Path(r"C:/Users/ghendrick/PhotoProject")
    config_path = workspace / "src" / "config.yaml"
    config = ConfigManager(str(config_path))
    enricher = MetadataEnricher(config)

    input_csv = Path(
        config.get(
            "ENRICHED_RESOLVED_CSV",
            "dev_data/record_catalog/data/outputs/enriched_resolved.csv",
        )
    )
    if not input_csv.exists():
        raise FileNotFoundError(f"Resolved CSV not found: {input_csv}")

    rows = []
    with input_csv.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)

    updated = 0
    for row in rows:
        if row.get("MusicBrainz_Release_Date") or row.get("MusicBrainz_Country"):
            continue
        title = row.get("Title Normalized") or row.get("Title")
        artist = row.get("Artist Normalized") or row.get("Artist")
        if not title or not artist:
            continue
        mb_data = enricher.query_musicbrainz(title, artist)
        if not mb_data:
            continue
        for key, value in mb_data.items():
            if value:
                key_name = f"MusicBrainz_{key.replace(' ', '_')}"
                row[key_name] = value
        updated += 1

    if not rows:
        print("No rows to update.")
        return

    fieldnames = set()
    for row in rows:
        fieldnames.update(row.keys())
    fieldnames = sorted(fieldnames)

    with input_csv.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {updated} rows in {input_csv}")


if __name__ == "__main__":
    os.environ.setdefault("PYTHONPATH", "src")
    main()
