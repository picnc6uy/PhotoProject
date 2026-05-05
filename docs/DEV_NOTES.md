# Project Progress and Backup Note
#
# Maintain version control (e.g., Git) and regular backups of:
# - MASTER_PROJECT_CONTEXT.md
# - ROADMAP.md
# - docs/DEV_NOTES.md
#
# This file is for current state, recent changes, and operational notes.

## Status Update (Feb 10, 2026)
- Record cataloging pipeline v1 (now under `photo_project/`) is feature-complete and moving into maintenance/archival mode.
- The exploratory `feature/version2` branch has been created and shelved until the cataloging domain is revisited.
- Focus is shifting to a new project centered on building agents capable of acting as software developers; new documentation will capture planning for that effort.
- Agent platform bootstrapped with base abstractions (`Agent`, `TaskSpec`, `ToolRegistry`) and corresponding unit tests.
- AgentArchitect reference agent added to guide agent-development workflows (see `docs/agent_platform/AGENT_ARCHITECT.md`).
- Knowledge base initialized under `docs/agent_platform/knowledge/` with best-practice summaries, distilled notes, and placeholders for external research.
- Orchestrator implemented (`src/agent_platform/orchestrator.py`) with JSON cache support and unit coverage (`src/tests/test_orchestrator_workflow.py`).
- Drafted agent rollout sequence (`docs/agent_platform/AGENT_ROSTER.md`) to guide implementation order.
- Implemented first-stage agents (ResourceSurveyor, TaskRefiner, RiskMonitor) with unit tests and integrated exports.
- Added mid-stage agents (PlannerAgent, DesignAdvisor, ImplementerAgent) with dedicated workflow tests.
- Implemented execution-stage agents (TestRunnerAgent, CodeReviewer, RequirementsVerifier) and validated workflows.
- Completed release pipeline agents (IntegratorAgent, ReleaseCoordinator, PostMergeObserver) with scenario tests.
- Consolidated documentation under `docs/agent_platform/` and added `tools/agent_platform/` helpers.

## Archived Pipeline State (Feb 9, 2026)

- Photo cataloging test passes and writes CSV to:
  - photo_project/dev_data/record_catalog/data/outputs/photo_catalog.csv
- Preprocessing uses smooth mode by default (see photo_project/src/config.yaml).
- OCR inbox populated with smooth output:
  - photo_project/dev_data/record_catalog/data/inbox_photos_ocr
- OCR CSV generated and parsed metadata CSV produced:
  - photo_project/dev_data/record_catalog/data/ocr_texts.csv
  - photo_project/dev_data/record_catalog/data/parsed_metadata.csv
- Review suggestions CSV generated for potential OCR catalog conflicts:
  - photo_project/dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv
- Enrichment candidate scoring CSV generated (Discogs-backed):
  - photo_project/dev_data/record_catalog/data/outputs/enrichment_candidates.csv
- Resolved enrichment output generated:
  - photo_project/dev_data/record_catalog/data/outputs/enriched_resolved.csv
- Final archival exports generated:
  - photo_project/dev_data/record_catalog/data/outputs/final_archival_catalog.csv
  - photo_project/dev_data/record_catalog/data/outputs/final_archival_catalog_consolidated.csv
- Final total export (A/B sides merged) generated:
  - photo_project/dev_data/record_catalog/data/outputs/final_total_catalog.csv
- Validation report generated:
  - photo_project/dev_data/record_catalog/data/outputs/catalog_validation_report.csv

## Preprocessing Summary
Implemented in photo_project/src/record_catalog/image_processor.py:
- Grayscale, CLAHE, bilateral denoise.
- Smooth-plus mode adds background normalization and gamma correction.
- Binary OCR mode (threshold + morph close) remains available but is not default.

Config keys (photo_project/src/config.yaml):
- PREPROCESS_MODE: ocr_smooth (active)
- CLAHE_CLIP_LIMIT, CLAHE_TILE_GRID_SIZE
- BILATERAL_D, BILATERAL_SIGMA_COLOR, BILATERAL_SIGMA_SPACE
- BACKGROUND_KERNEL_SIZE, GAMMA_CORRECTION
- SHARPEN_RADIUS, SHARPEN_PERCENT, SHARPEN_THRESHOLD
- AUTO_ROTATE: false (left off)

## Test Order (pipeline sequence)
1) Photo cataloging:
   - pytest -q photo_project/tests/test_photo_catalog.py
2) Image preprocessing:
   - pytest -q photo_project/tests/test_batch_resize_images.py
3) OCR extraction:
   - pytest -q photo_project/tests/test_ocr_service.py
4) Parsing:
   - pytest -q photo_project/tests/test_ocr_to_parser.py
5) Enrichment:
   - pytest -q photo_project/tests/test_enrich_consolidated.py

## Notes / Known Issues
- Roadmap checkboxes may be ahead of verified status; keep ROADMAP.md accurate.
- OCR/Parser/Enrichment stages require live API keys and incur cost.
- MusicBrainz is currently disabled (SSL EOF errors); Discogs-only enrichment is active.
- Discogs token is now sourced from a local .env file (ignored by git). If Discogs returns 401, the run disables Discogs to finish the pipeline.
- Pipeline run logging writes to photo_project/dev_data/record_catalog/data/outputs/logs/ with UTF-8 and safe console output.

## Repo Standards (Canonical Sources)
- Tests: `src/tests` now covers the agent platform; photo pipeline tests live in `photo_project/tests/` and have their own pytest configuration.
- Config: pipeline config is `photo_project/src/config.yaml`. Root `config.ts` is a Continue/IDE config (not used by the pipeline).
- Legacy materials are tracked under legacy/ (archived tests and sample artifacts).
- Secrets: use a local `.env` for API tokens (ignored by git).

## Verified Today (2026-02-09)
- Git repo initialized; core files committed; legacy materials moved to legacy/ and tracked.
- Photo cataloging completed and CSV generated:
  - photo_project/dev_data/record_catalog/data/outputs/photo_catalog.csv
- Preprocessing completed (ocr_smooth mode) and OCR inbox repopulated:
  - photo_project/dev_data/record_catalog/data/inbox_photos_ocr
- OCR completed with throttling; OCR CSV written:
  - photo_project/dev_data/record_catalog/data/ocr_texts.csv
- Parsing completed; parsed metadata CSV written:
  - photo_project/dev_data/record_catalog/data/parsed_metadata.csv
- Review suggestions generated for potential OCR catalog conflicts:
  - photo_project/dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv
- Enrichment candidate ranking completed with Discogs lookups and fallback searches.
- Candidate scoring now includes field agreement penalties and side-pair reconciliation.
- Resolved enrichment CSV generated and final archival exports produced.
- Consolidated output merges duplicate catalog numbers (multi-photo sides) and auto-fixes Decca K-prefixes.
- Validation report produced (known missing catalog for photo_0047.jpg).
- Full pipeline run completed in one pass for 204 photos (approx. 1h44m), outputs updated in outputs/ and logs/ (see latest log).

## Data Handling Scheme (Current)
Primary data flow and outputs:
1) Source photos -> photo catalog CSV:
   - photo_project/dev_data/record_catalog/data/outputs/photo_catalog.csv
2) Preprocessed OCR images -> OCR inbox:
   - photo_project/dev_data/record_catalog/data/inbox_photos_ocr
3) OCR raw outputs -> OCR CSV:
   - photo_project/dev_data/record_catalog/data/ocr_texts.csv
4) Parsed metadata (raw + normalized fields) -> parsed CSV:
   - photo_project/dev_data/record_catalog/data/parsed_metadata.csv
5) OCR conflict review suggestions -> review CSV:
   - photo_project/dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv
6) Discogs candidate ranking (best-guess + evidence) -> candidate CSV:
   - photo_project/dev_data/record_catalog/data/outputs/enrichment_candidates.csv
7) Enrichment output (resolved metadata + confidence) -> resolved CSV:
   - photo_project/dev_data/record_catalog/data/outputs/enriched_resolved.csv
8) Final archival export (non-consolidated) -> archival CSV:
   - photo_project/dev_data/record_catalog/data/outputs/final_archival_catalog.csv
9) Final archival export (consolidated) -> archival CSV:
   - photo_project/dev_data/record_catalog/data/outputs/final_archival_catalog_consolidated.csv
10) Validation report -> report CSV:
   - photo_project/dev_data/record_catalog/data/outputs/catalog_validation_report.csv

## Next Steps: Software Developer Agent Initiative
- Formalise architecture documentation (diagrams, ADRs) for the new platform.
- Identify tooling, benchmarks, and evaluation harnesses to measure agent effectiveness on real coding tasks.
- Outline initial milestones and experimentation plan before bootstrapping the new repository/workspace.
- Prototype tooling adapters (shell, git, editor) and connect them to the ToolRegistry.
