import csv
import time
from pathlib import Path

from .config_manager import ConfigManager
from .enricher import MetadataEnricher


def _load_best_candidates(candidates_csv_path: str) -> dict:
    best_by_filename = {}
    with open(candidates_csv_path, "r", encoding="utf-8") as csvfile:
        for row in csv.DictReader(csvfile):
            if row.get("best_for_filename") != "yes":
                continue
            if not (row.get("decision") or "").startswith("best_guess"):
                continue
            filename = row.get("filename") or ""
            if filename:
                best_by_filename[filename] = row
    return best_by_filename


def build_resolved_enriched(
    parsed_csv_path: str,
    candidates_csv_path: str,
    output_csv_path: str,
    config_path: str,
):
    config = ConfigManager(config_path)
    enricher = MetadataEnricher(config)

    best_candidates = _load_best_candidates(candidates_csv_path)
    parsed_path = Path(parsed_csv_path)
    output_path = Path(output_csv_path)

    if not parsed_path.exists():
        raise FileNotFoundError(f"Parsed CSV not found: {parsed_path}")

    resolved_rows = []
    with parsed_path.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row.get("filename") or ""
            candidate = best_candidates.get(filename, {})
            resolved = dict(row)
            if candidate:
                resolved["Catalog Number Resolved"] = candidate.get("candidate_catalog")
                resolved["Catalog Confidence"] = candidate.get("decision")
                resolved["Catalog Score"] = candidate.get("score")
                resolved["Discogs_Title_Candidate"] = candidate.get("discogs_title")
                resolved["Discogs_Label_Candidate"] = candidate.get("discogs_label")
                resolved["Discogs_CatNo_Candidate"] = candidate.get("discogs_catno")
                resolved["Discogs_Year_Candidate"] = candidate.get("discogs_year")
                resolved["Catalog Number"] = candidate.get("candidate_catalog") or resolved.get("Catalog Number")

            enriched = enricher.enrich_metadata(resolved)
            resolved_rows.append(enriched)
            time.sleep(1)

    if not resolved_rows:
        return 0

    all_keys = set()
    for row in resolved_rows:
        all_keys.update(row.keys())
    fieldnames = sorted(all_keys)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in resolved_rows:
            writer.writerow(row)

    return len(resolved_rows)
