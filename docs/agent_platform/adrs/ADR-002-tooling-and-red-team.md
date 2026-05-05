# ADR-002: Tooling Safeguards and Red-Team Escalation

*Status*: Accepted  
*Date*: 2026-05-04

## Context
Agents now invoke shell commands and perform automated reviews. To prevent unsafe execution and ensure skeptical oversight, we need agreed-upon policies for tool usage and red-team escalation before integrating code or triggering releases.

## Decision
- `ShellCommandTool` enforces an allow-list of command prefixes (default: `echo`, `pytest`, `flake8`, `git status`, `git add`). Commands outside the list are rejected unless explicitly configured.
- Agents should call `run_batch` when executing multiple commands to minimise repeated interpreter startup.
- Any agent that proposes changes (ImplementerAgent) or validates execution (TestRunnerAgent) must record their outputs so downstream reviewers can inspect artefacts.
- `RedTeamReviewer` runs after RequirementsVerifier. If the verdict is `reject` or `escalate`, IntegratorAgent must not proceed without human approval.
- Future tooling (git commit/push, package publish, deployment) must reside in dedicated tool classes with explicit permissions and tests.

## Consequences
- Tests use harmless `echo` commands to remain deterministic and to comply with the allow-list.
- When integrating real commands, the allow-list can be expanded on a per-task basis (e.g., `pytest`, `npm test`, `ruff`).
- The orchestrator and evaluation harness must check the red-team verdict before promoting artefacts.
