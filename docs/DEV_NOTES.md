# Project Progress and Backup Note
#
# Maintain version control (e.g., Git) and regular backups of:
# - MASTER_PROJECT_CONTEXT.md
# - ROADMAP.md
# - docs/DEV_NOTES.md
#
# This file is for current state, recent changes, and operational notes.

## Current State (Feb 6, 2026)
- Photo cataloging test passes and writes CSV to:
  - dev_data/record_catalog/data/outputs/photo_catalog.csv
- Preprocessing uses smooth mode by default (see src/config.yaml).
- OCR inbox populated with smooth output:
  - dev_data/record_catalog/data/inbox_photos_ocr
- OCR CSV generated and parsed metadata CSV produced:
  - dev_data/record_catalog/data/ocr_texts.csv
  - dev_data/record_catalog/data/parsed_metadata.csv
- Review suggestions CSV generated for potential OCR catalog conflicts:
  - dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv
- Enrichment candidate scoring CSV generated (Discogs-backed):
  - dev_data/record_catalog/data/outputs/enrichment_candidates.csv

## Preprocessing Summary
Implemented in src/record_catalog/image_processor.py:
- Grayscale, CLAHE, bilateral denoise.
- Smooth-plus mode adds background normalization and gamma correction.
- Binary OCR mode (threshold + morph close) remains available but is not default.

Config keys (src/config.yaml):
- PREPROCESS_MODE: ocr_smooth (active)
- CLAHE_CLIP_LIMIT, CLAHE_TILE_GRID_SIZE
- BILATERAL_D, BILATERAL_SIGMA_COLOR, BILATERAL_SIGMA_SPACE
- BACKGROUND_KERNEL_SIZE, GAMMA_CORRECTION
- SHARPEN_RADIUS, SHARPEN_PERCENT, SHARPEN_THRESHOLD
- AUTO_ROTATE: false (left off)

## Test Order (pipeline sequence)
1) Photo cataloging:
   - pytest -q src/test_photo_catalog.py
2) Image preprocessing:
   - pytest -q src/tests/test_batch_resize_images.py
3) OCR extraction:
   - pytest -q src/tests/test_ocr_service.py
4) Parsing:
   - pytest -q src/tests/test_ocr_to_parser.py
5) Enrichment:
   - pytest -q src/tests/test_enrich_consolidated.py

## Notes / Known Issues
- Roadmap checkboxes may be ahead of verified status; keep ROADMAP.md accurate.
- OCR/Parser/Enrichment stages require live API keys and incur cost.

## Repo Standards (Canonical Sources)
- Tests: `src/tests` is canonical; legacy tests live in `tests/`, `src/tests_backup/`, `src/tests/archive/` and are excluded by `pytest.ini`.
- Config: pipeline config is `src/config.yaml`. Root `config.yaml` is a Continue/IDE config (not used by the pipeline).
- Legacy materials are tracked under legacy/ (archived tests and sample artifacts).

## Verified Today (2026-02-06)
- Git repo initialized; core files committed; legacy materials moved to legacy/ and tracked.
- Photo cataloging completed and CSV generated:
  - dev_data/record_catalog/data/outputs/photo_catalog.csv
- Preprocessing completed (ocr_smooth mode) and OCR inbox repopulated:
  - dev_data/record_catalog/data/inbox_photos_ocr
- OCR completed with throttling; OCR CSV written:
  - dev_data/record_catalog/data/ocr_texts.csv
- Parsing completed; parsed metadata CSV written:
  - dev_data/record_catalog/data/parsed_metadata.csv
- Review suggestions generated for potential OCR catalog conflicts:
  - dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv
- Enrichment candidate ranking completed with Discogs lookups and fallback searches.
- Candidate scoring now includes field agreement penalties and side-pair reconciliation.

## Data Handling Scheme (Current)
Primary data flow and outputs:
1) Source photos -> photo catalog CSV:
   - dev_data/record_catalog/data/outputs/photo_catalog.csv
2) Preprocessed OCR images -> OCR inbox:
   - dev_data/record_catalog/data/inbox_photos_ocr
3) OCR raw outputs -> OCR CSV:
   - dev_data/record_catalog/data/ocr_texts.csv
4) Parsed metadata (raw + normalized fields) -> parsed CSV:
   - dev_data/record_catalog/data/parsed_metadata.csv
5) OCR conflict review suggestions -> review CSV:
   - dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv
6) Discogs candidate ranking (best-guess + evidence) -> candidate CSV:
   - dev_data/record_catalog/data/outputs/enrichment_candidates.csv
7) Enrichment output (resolved metadata + confidence) -> resolved CSV:
   - dev_data/record_catalog/data/outputs/enriched_resolved.csv
