# AGENTS.md

## Startup Context

On each new chat/session, read these files in order before proceeding:

1. **[docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)** — single source of truth for
   what's shipped, what's pending, what's broken. **Read this first.**
2. **[../planning/HANDOVER.md](../planning/HANDOVER.md)** — cross-repo session-start
   brief (project map, the `agent-task` workflow, operating principles).
3. **[CLAUDE.md](CLAUDE.md)** — PhotoProject-specific context + the five-step
   session-start protocol.
4. **[.agent/README.md](.agent/README.md)** — the on-disk task-contract loop.
   If a task is staged at `.agent/tasks/<id>.md`, read it AND the lens it names
   at `.agent/lenses/<type>.md` before touching code.

`ROADMAP.md` and `docs/DEV_NOTES.md` predate the 2026-05-19 retire-duplicates
sprint and contain stale claims (e.g. "agent uses OpenAI Codex with GPT-5" —
Codex was removed). Treat them as historical context, not current state.
`MASTER_PROJECT_CONTEXT.md` was removed 2026-05-20 (superseded by
CURRENT_STATE.md); recover from git history if needed.
