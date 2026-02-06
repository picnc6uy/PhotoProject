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

## Docs
- MASTER_PROJECT_CONTEXT.md — high-level architecture and workflow
- ROADMAP.md — milestone checklist
- docs/DEV_NOTES.md — current state, verified steps, tuning notes

## Repo notes
- Canonical tests live in src/tests (legacy tests in tests/ and src/tests_backup are kept for reference).
- Pipeline config is src/config.yaml (root config.yaml is Continue/IDE config).
