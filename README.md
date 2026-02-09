# PhotoProject

AI-assisted photo cataloging pipeline for record labels. Processes images into OCR-ready inputs and structured metadata.

## Quick start
1) Place source photos in:
   - dev_data/record_catalog/data/inbox_photos
2) Run photo cataloging:
   - pytest -q src/test_photo_catalog.py
3) Run preprocessing:
   - pytest -q src/tests/test_batch_resize_images.py
4) Run OCR (uses live API keys):
   - pytest -q src/tests/test_ocr_service.py
5) Run parsing:
   - pytest -q src/tests/test_ocr_to_parser.py
6) Run enrichment:
   - pytest -q src/tests/test_enrich_consolidated.py

## Outputs (current pipeline)
- Photo catalog: `dev_data/record_catalog/data/outputs/photo_catalog.csv`
- OCR raw: `dev_data/record_catalog/data/ocr_texts.csv`
- Parsed metadata: `dev_data/record_catalog/data/parsed_metadata.csv`
- Review suggestions: `dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv`
- Enrichment candidates: `dev_data/record_catalog/data/outputs/enrichment_candidates.csv`
- Resolved enrichment: `dev_data/record_catalog/data/outputs/enriched_resolved.csv`
- Final archival (all rows): `dev_data/record_catalog/data/outputs/final_archival_catalog.csv`
- Final archival (consolidated): `dev_data/record_catalog/data/outputs/final_archival_catalog_consolidated.csv`
- Validation report: `dev_data/record_catalog/data/outputs/catalog_validation_report.csv`

## End-to-end pipeline
- Non-interactive run through resolved outputs and final archival exports:
  - `python src/run_pipeline.py --stop-after resolve`

## Docs
- MASTER_PROJECT_CONTEXT.md - high-level architecture and workflow
- ROADMAP.md - milestone checklist
- docs/DEV_NOTES.md - current state, verified steps, tuning notes

## Repo notes
- Canonical tests live in src/tests (legacy tests in tests/ and src/tests_backup are kept for reference).
- Pipeline config is src/config.yaml (root config.yaml is Continue/IDE config).
- Legacy materials are tracked under legacy/ (archived tests and sample artifacts).
