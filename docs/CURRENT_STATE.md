# PhotoProject — Current State Snapshot

This file is the **first thing** to read at the start of a new session.
It answers "where are we?" in 60 seconds. Keep it short. Update it when
material things change.

---

## As of 2026-05-20

**Main commit:** `bc335f5` (chore: fix pytest.ini — strip UTF-8 BOM and
update pythonpath).

**Pushed to:** `picnc6uy/PhotoProject` (private GitHub).

**Branches:** `main` (canonical, linear-history rule — no merge commits;
rebase feature branches before integrating). `feature/version2` still
present locally and on origin; its tip is the sanitized
`fa54a3c` post-T-001 (force-pushed 2026-05-19 after relaxing branch
protection — confirm protection has been restored).

**Tests:** 4 dedicated T-006 tests pass; 7 skipped; 1 pre-existing failure
in `test_batch_resize_images.py` (unrelated config path issue, not blocking).
Full suite hangs on integration-marked tests reaching external services
— always run with `-m "not integration"` for local work.

**Pre-commit:** none — XR-001 deferred PhotoProject to XR-004 once D-4
lands. No detect-secrets hook here yet.

**Worktrees:** none (the `PhotoProject--T-006` and `PhotoProject--T-001`
worktrees were cleaned up 2026-05-20).

---

## Project Overview

Photo cataloging pipeline. Images → OCR → parsed metadata → enrichment
(Discogs, MusicBrainz) → reconciliation → final archival catalog. After
the 2026-05-19 retire-duplicates sprint (commits `766da10`, `ebe8b29`),
this repo contains only the `photo_project/` record-cataloging app.
Duplicate `src/agent_platform/` and `personal_record_system/` stubs were
removed in favour of canonical `spec_agents` and `personal_os` siblings.

## What Works End-to-End

- Image preprocessing (CLAHE + bilateral + sharpen by default;
  smooth-plus and binary modes available).
- Azure Computer Vision OCR.
- OpenAI parsing of OCR text → structured metadata.
- Enrichment via Discogs + MusicBrainz.
- Normalization, reconciliation, and final archival catalog export.
- `.env`-loaded secrets; `config.yaml` gitignored; `config.example.yaml`
  ships as template.

## Recently Landed (2026-05-19 to 2026-05-20)

- **T-001:** Discogs PAT rotation + history scrub (revoked, purged from
  all reachable history, both refs force-pushed). Verification at
  `.agent/verifications/T-001.md`.
- **T-002:** `.gitignore` correctly excludes `config.yaml`.
- **T-003:** `config.example.yaml` ships; ConfigManager allow-list env
  merge; stops logging values.
- **T-006:** Fixed double-escaped regexes in normalizer + final_exporter
  (TDD lens; 4 new tests).
- **pytest.ini cleanup:** BOM removed; `pythonpath` updated for the
  post-restructure layout. Tests now run without needing PYTHONPATH
  override or pytest.ini deletion.

## What's Stubbed / Deferred

- **Pre-commit + detect-secrets** — XR-004 (gated on D-4).
- **Rename to `photo_archive` + restructure on `spec_agents`** — D-4
  **SIGNED 2026-05-20**; execution gated on operator initiation. Unlocks
  XR-004 (apply canonical conventions), XR-007 (retire-duplicates final
  pass), T-033 (Claude vision pipeline), LENS-002 (cataloging lens).
- **Claude vision end-to-end** — T-033 (P3 in FIXES.md, promote once
  D-4 lands).
- **Full pytest suite hang on integration tests** — pre-existing; gate
  with `-m "not integration"` until properly addressed.

## Active Sprint

⬜ Foundation pass per `planning/SYSTEM.md` 2026-05-20 reframe.
PhotoProject's next material milestone is **D-4** (rename +
restructure), followed by **XR-004** (apply canonical-stack conventions:
pre-commit, ruff/pyright, structlog, alembic).

## Known Issues / Cleanup Items

- Branch protection on `feature/version2` may still be relaxed from the
  2026-05-19 force-push — confirm restored in GitHub settings.
- `MASTER_PROJECT_CONTEXT.md` deleted in this commit (stale pre-pivot
  doc dated 2026-02-10; superseded by this file).
- `ROADMAP.md` and `docs/DEV_NOTES.md` predate the 2026-05-19
  retire-duplicates sprint — treat as historical, not current state.

## How To Resume Work

1. `cd c:/Users/ghendrick/PhotoProject`
2. Read this file (you just did)
3. Read [../planning/FIXES.md](../../../planning/FIXES.md) for the T-*
   backlog; [../planning/SYSTEM.md](../../../planning/SYSTEM.md) for
   cross-repo tasks
4. Confirm: `python -m pytest -m "not integration" -q` passes (or matches
   the 4-passing baseline above)
5. Confirm: `git log --oneline -3` matches the main commit above
6. Confirm: `git status` is clean
7. Ask the operator which task to work on

## How To Update This File

Edit it when:

- A task ships that changes commit / tests / surface
- A new T-* lands or moves out of scope
- Tests count or pre-commit posture changes
- A new known issue is discovered or resolved

Commit the update with the change that caused it. Never let this file
drift from reality — its whole job is to be accurate at-a-glance.
