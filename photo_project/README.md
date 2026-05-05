# Photo_Project

This folder contains the archived record cataloging pipeline originally located at `src/record_catalog/`. It includes image preprocessing, OCR extraction, parsing, enrichment, and export stages.

## Layout

```
photo_project/
├── src/record_catalog/          # pipeline modules
├── tests/                       # legacy pytest suites (OCR, enrichment, etc.)
├── scripts/                     # utility scripts for comparison/debugging
└── dev_data/record_catalog/     # sample data outputs (if provided)
```

The agent platform project can operate on this workspace by passing the folder path to `run_workflow.py` or `evaluate_workflow.py`.

To develop the pipeline separately, you can initialize a standalone repository from this directory:

```bash
cd photo_project
git init
# add remote, etc.
```

All historical documentation (DEV_NOTES, ROADMAP) referencing the record catalog project is still applicable; adjust paths to account for the new location.
