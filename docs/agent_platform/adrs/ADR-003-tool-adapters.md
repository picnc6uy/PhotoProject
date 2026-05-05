# ADR-003: Tool Adapter Permissions

*Status*: Proposed  
*Date*: 2026-05-04

## Context
We introduced `ShellCommandTool`, `GitTool`, and `EditorTool` to enable command execution, git inspection, and file manipulation. Without explicit policies, scope creep could allow unsafe operations (e.g., arbitrary writes, commits, network use).

## Decision
- The default `ShellCommandTool` allow-list covers `echo`, `pytest`, `flake8`, `git status`, `git add`. Additional commands require explicit configuration in task metadata or orchestrator setup.
- `GitTool` is limited to non-destructive commands (`status`, `diff`, `add`). Commit, push, merge, or remote operations remain disallowed until an ADR authorises them.
- `EditorTool` supports `read`, `preview`, and optional `write`. Write actions must be opt-in (via `allow_write=True`) and their output is truncated to 16 KB per operation to prevent runaway writes.
- Task metadata may request additional commands via allow-lists, but orchestrator must log the override and red-team reviewer evaluates the change.
- All tool invocations log command strings and outputs in agent artefacts (already stored in orchestrator records).

## Consequences
- Workflow scripts must ensure the tool registry respects ADR-defined allow-lists.
- Integrator or release agents cannot mutate files or repo state without explicit configuration and human sign-off.
- Future ADRs must authorise any additional commands (e.g., `git commit`, package publishing) before adapters are expanded.
