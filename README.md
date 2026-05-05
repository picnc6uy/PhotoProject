# picnc6uy (Agent-Platform)

[![Orchestrator Workflow](https://github.com/picnc6uy/Agent-Platform/actions/workflows/orchestrator.yml/badge.svg)](https://github.com/picnc6uy/Agent-Platform/actions/workflows/orchestrator.yml)

The repository now contains two tracks:

1. **Archived Continue Pipeline (Record Cataloging)** – feature-complete OCR and enrichment workflow retained for reference.
2. **picnc6uy / Agent-Platform (Inception)** – new initiative to design agents capable of end-to-end software development assistance.

---

## Continue Pipeline (archived for maintenance)

Legacy source remains under `src/record_catalog/`; consider it read-only unless explicitly reactivated.

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
- See `docs/agent_platform/PROJECT_CHARTER.md` for goals, success criteria, and glossary.
- See `docs/agent_platform/ROADMAP.md` for milestone planning.
- Review `docs/agent_platform/AGENT_ARCHITECT.md` for the expert agent blueprint now available.
- Browse `docs/agent_platform/knowledge/` for curated references and research notes.
- Review `docs/agent_platform/contracts/` for per-agent contracts.
- Task specification schema lives at `docs/agent_platform/task_schema.yaml`; evaluation harness validates loaded tasks.
- See `docs/agent_platform/adrs/` for recorded architecture decisions.
- Review `docs/agent_platform/ORCHESTRATOR_PLAN.md` for the orchestration roadmap.
- Check `docs/agent_platform/ARCHITECTURE.md` for the PlantUML architecture overview.
- Browse `docs/agent_platform/AGENT_ROSTER.md` for the ordered agent rollout.
- Core Python package scaffolding lives under `src/agent_platform/` (including `orchestrator.py`).
- Utility scripts live under `tools/agent_platform/` (e.g., `run_workflow.py`, `evaluate_workflow.py`).  Both accept `--allow-shell` to extend the shell allow-list per ADR-003.  The evaluation harness now emits a summary (test pass/fail, review verdicts, red-team status).

---

## Docs
- `MASTER_PROJECT_CONTEXT.md` – cross-project overview and current focus.
- `ROADMAP.md` – legacy pipeline checklist plus links into the agent roadmap.
- `docs/DEV_NOTES.md` – operational log covering the project pivot, agent development, and orchestration updates.

## Repo notes
- Canonical tests live in `src/tests` (legacy tests remain under `tests/` and `src/tests_backup/`).
- Pipeline config is `src/config.yaml` (root `config.ts` is for the Continue IDE).
- Legacy materials are tracked under `legacy/` for historical reference.

