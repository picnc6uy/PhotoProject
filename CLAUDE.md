# CLAUDE.md — PhotoProject

> **Fresh session?** Start at [../planning/HANDOVER.md](../planning/HANDOVER.md) for the
> canonical session-start brief: project map, cross-repo state, the `agent-task`
> workflow, and operating principles. Then return here for repo-specific context.

## Repo-specific notes

PhotoProject is the photo cataloging pipeline. After the 2026-05-19 retire-duplicates
sprint (commits `766da10`, `ebe8b29` on `main`), this repo contains only the
`photo_project/` record-cataloging app. The duplicate `src/agent_platform/` and
`personal_record_system/` stubs were removed in favour of the canonical `spec_agents`
and `personal_os` siblings.

## Backlog

Single source of truth: [../planning/FIXES.md](../planning/FIXES.md) (tasks T-001 through T-040).

Recently landed: T-002 (`.gitignore` fix) and T-003 (`config.example.yaml` +
ConfigManager security patches). T-001 (Discogs PAT history scrub) ran locally
but force-push is blocked by GitHub branch protection on `main` and
`feature/version2` — awaiting operator decision.

## Active work

Check `.agent/tasks/` for the current task spec. If a worktree exists at
`../PhotoProject--T-XXX/`, that is where active work happens — never edit the
main checkout directly during an `agent-task` cycle.

## Conventions still to land

Per SYSTEM.md XR-004 (P1), this repo is not yet on the canonical-stack conventions:
no `pyproject.toml`, no ruff/pyright strict, no structlog, no pre-commit, no
alembic. The `MASTER_PROJECT_CONTEXT.md` and `AGENTS.md` in this repo are pre-pivot
and stale — do not rely on them for current state; use HANDOVER.md, SYSTEM.md,
and FIXES.md instead.

## Local dev quirks

- `pytest.ini` sets `pythonpath = src`; bare `python` invocations need
  `cd photo_project/src` or `PYTHONPATH=photo_project/src`.
- Tests live at `photo_project/tests/` (not the legacy `tests/` or `src/tests_backup/`).
- ConfigManager loads `.env` from CWD; pipeline scripts typically run from
  `photo_project/`.
- Real Azure CV + OpenAI API calls happen in tests marked `integration` (per
  `pytest.ini` markers). Exclude with `-m "not integration"` if you don't want
  to spend money.
