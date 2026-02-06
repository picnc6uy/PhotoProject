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
- Preprocessing uses smooth-plus mode by default (see src/config.yaml).
- OCR inbox populated with smooth-plus output:
  - dev_data/record_catalog/data/inbox_photos_ocr

## Preprocessing Summary
Implemented in src/record_catalog/image_processor.py:
- Grayscale, CLAHE, bilateral denoise.
- Smooth-plus mode adds background normalization and gamma correction.
- Binary OCR mode (threshold + morph close) remains available but is not default.

Config keys (src/config.yaml):
- PREPROCESS_MODE: ocr_smooth_plus (active)
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

## Verified Today (2026-02-06)
- Photo cataloging test passed:
  - Command: pytest -q src/test_photo_catalog.py
  - Output: dev_data/record_catalog/data/outputs/photo_catalog.csv
- Image preprocessing test passed:
  - Command: pytest -q src/tests/test_batch_resize_images.py
- OCR inbox repopulated with smooth-plus output:
  - Command: python src/batch_resize_images.py
  - Output: dev_data/record_catalog/data/inbox_photos_ocr
- Orientation auto-rotate tested and disabled (no improvement observed).
