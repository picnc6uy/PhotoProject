# PhotoProject

The repository now contains two tracks:

1. **Archived Continue Pipeline (Record Cataloging)** – feature-complete OCR and enrichment workflow retained for reference.
2. **Software Developer Agent Platform (Inception)** – new initiative to design agents capable of end-to-end software development assistance.

---

## Continue Pipeline (archived for maintenance)

### Quick start (if revisiting the pipeline)
1. Place source photos in `dev_data/record_catalog/data/inbox_photos`
2. Run photo cataloging:
   - `pytest -q src/test_photo_catalog.py`
3. Run preprocessing:
   - `pytest -q src/tests/test_batch_resize_images.py`
4. Run OCR (uses live API keys):
   - `pytest -q src/tests/test_ocr_service.py`
5. Run parsing:
   - `pytest -q src/tests/test_ocr_to_parser.py`
6. Run enrichment:
   - `pytest -q src/tests/test_enrich_consolidated.py`

### Outputs
- Photo catalog: `dev_data/record_catalog/data/outputs/photo_catalog.csv`
- OCR raw: `dev_data/record_catalog/data/ocr_texts.csv`
- Parsed metadata: `dev_data/record_catalog/data/parsed_metadata.csv`
- Review suggestions: `dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv`
- Enrichment candidates: `dev_data/record_catalog/data/outputs/enrichment_candidates.csv`
- Resolved enrichment: `dev_data/record_catalog/data/outputs/enriched_resolved.csv`
- Final archival (all rows): `dev_data/record_catalog/data/outputs/final_archival_catalog.csv`
- Final archival (consolidated): `dev_data/record_catalog/data/outputs/final_archival_catalog_consolidated.csv`
- Final total catalog: `dev_data/record_catalog/data/outputs/final_total_catalog.csv`
- Validation report: `dev_data/record_catalog/data/outputs/catalog_validation_report.csv`

### End-to-end pipeline
- Non-interactive run through resolved outputs and final archival exports:
  - `python src/run_pipeline.py --stop-after resolve`

---

## Software Developer Agent Platform (new)

### Mission
Build agents that can plan, implement, and evaluate software tasks in collaboration with human developers.

### Bootstrap status
- See `docs/agents/PROJECT_CHARTER.md` for goals, success criteria, and glossary.
- See `docs/agents/ROADMAP.md` for milestone planning.
- Review `docs/agents/AGENT_ARCHITECT.md` for the expert agent blueprint now available.
- Core Python package scaffolding lives under `src/agent_platform/`.

---

## Docs
- `MASTER_PROJECT_CONTEXT.md` – cross-project overview and current focus.
- `ROADMAP.md` – legacy pipeline checklist plus links into the agent roadmap.
- `docs/DEV_NOTES.md` – operational log with context on the project pivot and agent development.

## Repo notes
- Canonical tests live in `src/tests` (legacy tests remain under `tests/` and `src/tests_backup/`).
- Pipeline config is `src/config.yaml` (root `config.ts` is for the Continue IDE).
- Legacy materials are tracked under `legacy/` for historical reference.

