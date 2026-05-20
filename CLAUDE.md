# CLAUDE.md — PhotoProject

> **Fresh session?** Start at [../planning/HANDOVER.md](../planning/HANDOVER.md) for the
> canonical session-start brief: project map, cross-repo state, the `agent-task`
> workflow, and operating principles. **Then** read this file and follow the
> session-start protocol below for PhotoProject-specific context.

---

## Session-Start Protocol

When starting a new session on PhotoProject, do these five things before
proposing or executing any work:

1. **Read [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)** — snapshot of where things are right now (commit, tests, recently landed, known issues).
2. **Read [../planning/FIXES.md](../planning/FIXES.md)** for the T-* backlog and [../planning/SYSTEM.md](../planning/SYSTEM.md) for cross-repo tasks affecting PhotoProject (XR-004, T-033).
3. **Verify the build:** `python -m pytest -m "not integration" -q` should match the test count in CURRENT_STATE.md (full suite hangs on external-service tests).
4. **Verify git is clean:** `git status --short` should be clean (or only show expected untracked files).
5. **Ask the operator which task to work on** — don't assume.

If you find drift between CURRENT_STATE.md and reality, **fix the doc first** before doing other work. CURRENT_STATE.md is the contract.

**main is linear-history only:** the branch protection rule forbids merge commits. Always rebase feature branches onto main before integrating; never `git merge --no-ff`.

---

## Repo-specific notes

PhotoProject is the photo cataloging pipeline. After the 2026-05-19 retire-duplicates
sprint (commits `766da10`, `ebe8b29` on `main`), this repo contains only the
`photo_project/` record-cataloging app. The duplicate `src/agent_platform/` and
`personal_record_system/` stubs were removed in favour of the canonical `spec_agents`
and `personal_os` siblings.

## Backlog

Single source of truth: [../planning/FIXES.md](../planning/FIXES.md) (tasks T-001 through T-040). CURRENT_STATE.md tracks the rolling "recently landed" list.

## Active work

Check `.agent/tasks/` for the current task spec. If a worktree exists at
`../PhotoProject--T-XXX/`, that is where active work happens — never edit the
main checkout directly during an `agent-task` cycle.

## Conventions still to land

Per SYSTEM.md XR-004 (P1, gated on D-4), this repo is not yet on the canonical-stack
conventions: no `pyproject.toml`, no ruff/pyright strict, no structlog, no pre-commit,
no alembic. `ROADMAP.md` and the older `docs/DEV_NOTES.md` predate the 2026-05-19
pivot and contain stale claims — treat as historical, not current state.

## Local dev quirks

- `pytest.ini` is fixed (BOM stripped, `pythonpath = photo_project/src`); bare
  `python -m pytest` from the repo root works without PYTHONPATH override.
- Tests live at `photo_project/tests/` (not the legacy `tests/` or `src/tests_backup/`).
- ConfigManager loads `.env` from CWD; pipeline scripts typically run from
  `photo_project/`.
- Real Azure CV + OpenAI API calls happen in tests marked `integration` (per
  `pytest.ini` markers). The full suite hangs on these — always use
  `-m "not integration"` for local runs.
