---
Last updated: 2026-02-10

## Current Status

- The Continue record-catalog pipeline (v1), now located under `photo_project/`, is feature-complete and in maintenance mode.

- Future enhancements captured on branch `feature/version2` are paused until work resumes.
- Active development is pivoting to a new initiative focused on building software developer agents.
- AgentArchitect reference agent established to advise on agent-building workflows within this repository.


## Project Summary (Archived Continue Pipeline)


The Continue project is an AI-powered photo cataloging and record metadata management system combining Python and TypeScript components in an object-oriented architecture.

Key features:
- Image preprocessing and resizing for OCR and description generation.
- Enhanced preprocessing pipeline using CLAHE and bilateral denoising, with smooth mode (CLAHE + bilateral + sharpen) as default; smooth-plus (background normalization + gamma) and binary threshold/morph close remain available.
- Azure Computer Vision OCR for raw text extraction.
- OpenAI GPT-based parsing of OCR text into structured metadata.
- Metadata enrichment via Discogs, MusicBrainz, and other sources.
- Normalization and reconciliation prior to enrichment, including review suggestions for likely OCR catalog conflicts.
- Resolved enrichment outputs and final archival exports (consolidated and non-consolidated) with validation reporting.
- Comprehensive metadata catalog management (loading, saving, searching).
- Configured via YAML files and environment variables.
- Local `.env` file is used for API tokens and is ignored by git.
- Testing covers preprocessing, OCR extraction, parsing, and pipeline integration; enrichment validation is pending.
- Designed incrementally with clear module separation, logging, error handling, and modular object-oriented pipeline components.
    - Operational details and tuning parameters live in docs/DEV_NOTES.md and photo_project/src/config.yaml.


---

## Architectural Overview and Data Flow

The project follows a sequential pipeline to process photos into enriched metadata catalog entries:

- Images are preprocessed (grayscale, denoising, sharpening). Default mode is smooth; smooth-plus and binary OCR modes are optional.
- Resized to Azure OCR max dimension constraints (4200 pixels max).
- Saved with JPEG compression quality targeting under 4 MB file size.
- Excessively large files are further compressed and resized iteratively.
- OCR text extraction via Azure OCR service.
- Parsing OCR text to structured JSON metadata using OpenAI GPT.
- Normalize parsed metadata (preserve raw values, add normalized fields) and generate review suggestions for likely OCR conflicts.
- Metadata enrichment querying external music data sources (Discogs active; MusicBrainz currently disabled due to SSL EOF errors).
- Validation and error handling of metadata for consistency.
- Final validated metadata compiled into archival catalogs with a validation report.

Each pipeline stage is implemented as a modular object-oriented component with comprehensive testing to ensure accuracy and reliability.

---

## Development and Agent Workflow Guidance

- On each agent session startup, load and read this master context file to maintain up-to-date project understanding.
- Follow incremental, test-driven development and prioritize reliability, logging, and error handling.
- Maintain clear commit messages and prompt documentation updates.
- Follow strict workspace path handling protocols:
  - All file operations must use absolute paths under the canonical workspace root.
  - The canonical root string is treated literally; no path normalization or rewriting (e.g., no removal of ".continue" dot segments).
  - Before any file edit, verify file existence via directory listings of parent paths.
  - Always execute terminal commands from the canonical root directory (e.g., cd /d "C:\Users\ghendrick\.continue" in Windows).
  - Detect and correct path mismatches, reporting them explicitly.
- Agent autonomy is granted for routine fixes but requires caution on breaking changes or secrets.
- Confirm before file deletions or renames to safeguard workspace integrity.

---

## Environment Facts

- Workspace Root: C:\Users\ghendrick\PhotoProject
- Python 3.12.8 with pip 25.3 installed.
- Project directories include agent_platform/ resources (`docs/agent_platform`, `tools/agent_platform`, etc.) and the archived photo pipeline under `photo_project/`.
- Key config files: photo_project/src/config.yaml (pipeline), package.json, tsconfig.json.

- Secrets should be stored in `.env` (not committed).

---

## Agent Contract Summary

- Agent uses OpenAI Codex with GPT-5.
- Full workspace file read/write access within workspace root.
- Internet usage limited to official docs and primary sources.
- Strict local system truthfulness: no claims without explicit tool outputs.
- Autonomy for routine maintenance, with pauses for major or secret-impacting changes.
- Confirm deletions or renames prior to execution.

---

## New Initiative: Software Developer Agent Platform

The next active project will focus on designing and implementing autonomous agents that can operate as end-to-end software developers. Initial objectives include:

- Defining requirements and success metrics for agent-assisted software delivery.
- Establishing architecture, tooling, and evaluation harnesses tailored to agent workflows.
- Capturing planning artifacts, roadmaps, and technical notes in new agent-specific documentation (see `docs/agent_platform/PROJECT_CHARTER.md`, `docs/agent_platform/ROADMAP.md`, and `docs/agent_platform/AGENT_ARCHITECT.md`).



## Additional Resources

- See [ROADMAP.md](ROADMAP.md) for the legacy pipeline checklist and maintenance notes, plus forthcoming agent-planning updates.
- See [docs/DEV_NOTES.md](docs/DEV_NOTES.md) for historical run summaries and the latest status on the project transition.

---

Thank you for contributing to Continue and the upcoming agent development initiative. Your careful work ensures robustness and adaptability.


