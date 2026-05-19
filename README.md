# picnc6uy (Agent-Platform)

Photo cataloging pipeline. OCR + structured metadata extraction + Discogs enrichment for record labels.

---

## Photo_Project (archived for maintenance)

Legacy source now lives under `photo_project/src/record_catalog/`; consider it read-only unless explicitly reactivated.

### Quick start (if revisiting the pipeline)
1. Place source photos in `photo_project/dev_data/record_catalog/data/inbox_photos`
2. Run photo cataloging:
   - `pytest -q photo_project/tests/test_photo_catalog.py`
3. Run preprocessing:
   - `pytest -q photo_project/tests/test_batch_resize_images.py`
4. Run OCR (uses live API keys):
   - `pytest -q photo_project/tests/test_ocr_service.py`
5. Run parsing:
   - `pytest -q photo_project/tests/test_ocr_to_parser.py`
6. Run enrichment:
   - `pytest -q photo_project/tests/test_enrich_consolidated.py`

### Outputs
- Photo catalog: `photo_project/dev_data/record_catalog/data/outputs/photo_catalog.csv`
- OCR raw: `photo_project/dev_data/record_catalog/data/ocr_texts.csv`
- Parsed metadata: `photo_project/dev_data/record_catalog/data/parsed_metadata.csv`
- Review suggestions: `photo_project/dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv`
- Enrichment candidates: `photo_project/dev_data/record_catalog/data/outputs/enrichment_candidates.csv`
- Resolved enrichment: `photo_project/dev_data/record_catalog/data/outputs/enriched_resolved.csv`
- Final archival (all rows): `photo_project/dev_data/record_catalog/data/outputs/final_archival_catalog.csv`
- Final archival (consolidated): `photo_project/dev_data/record_catalog/data/outputs/final_archival_catalog_consolidated.csv`
- Final total catalog: `photo_project/dev_data/record_catalog/data/outputs/final_total_catalog.csv`
- Validation report: `photo_project/dev_data/record_catalog/data/outputs/catalog_validation_report.csv`

### End-to-end pipeline
- Non-interactive run through resolved outputs and final archival exports:
  - `python photo_project/src/run_pipeline.py --stop-after resolve`

---

## Docs
- `MASTER_PROJECT_CONTEXT.md` – cross-project overview and current focus.
- `ROADMAP.md` – legacy pipeline checklist plus links into the agent roadmap.
- `docs/DEV_NOTES.md` – operational log covering the project pivot, agent development, and orchestration updates.

## Repo notes
- Canonical tests live in `src/tests` (legacy tests remain under `tests/` and `src/tests_backup/`).
- Pipeline config is `src/config.yaml` (root `config.ts` is for the Continue IDE).
- Legacy materials are tracked under `legacy/` for historical reference.
\n
