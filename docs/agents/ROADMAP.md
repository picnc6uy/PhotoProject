# Softo tware Developer Agent Platform — Roadmap

_Last updated: 2026-02-10 (evening update)_

## Phase 0 — Foundations
- [x] Draft project charter and glossary (`PROJECT_CHARTER.md`).
- [x] Update top-level documentation to reflect pivot from record catalog pipeline.
- [x] Seed agent knowledge base (`docs/agents/knowledge/`).
- [ ] Define repository layout and coding standards for agent platform modules.

## Phase 1 — Architecture & Scaffolding
- [ ] Finalize core abstractions (Agent, Task, Tool, Environment, Memory).
- [x] Implement base Python package `agent_platform` with interfaces and utilities.
- [x] Add unit tests covering abstract base class contracts and registries.
- [x] Deliver single-agent orchestrator with caching (`orchestrator.py`, `test_orchestrator.py`).
- [x] Publish architecture and agent roster docs (`AGENT_PLATFORM_ARCHITECTURE.md`, `AGENT_ROSTER.md`).
- [ ] Document architecture (sequence diagrams, component responsibilities).

## Phase 2 — Tooling & Integration
- [ ] Create tool registry with sandbox execution adapters (e.g., shell, git, editor diff).
- [ ] Implement configuration management and capability gating (safety checks, permissions).
- [ ] Prototype state/memory persistence (short-term reasoning context, long-term knowledge).
- [ ] Integrate logging/telemetry for agent decision tracing.

## Phase 3 — Evaluation Harness
- [ ] Define canonical software development task set (ticket format, acceptance tests).
- [ ] Build runner to provision tasks, run agents, and collect metrics.
- [ ] Implement scoring (pass/fail, code quality, plan adherence).
- [ ] Generate baseline reports and dashboards for regression tracking.

## Phase 4 — Agent Workflows
- [ ] Design reference reasoning loop(s) (plan-act-reflect, tree-of-thought, etc.).
- [ ] Implement planning strategy with milestone checkpoints for human oversight.
- [ ] Demonstrate agent completing a small coding task end-to-end (scaffold → code → test → summarize).
- [x] Deliver AgentArchitect blueprint as workspace expert (`docs/agents/AGENT_ARCHITECT.md`).
- [ ] Conduct post-mortem and iterate on safety/quality controls.

## Phase 5 — Expansion & Collaboration
- [ ] Explore multi-agent collaboration for larger tasks (planner + coder + reviewer roles).
- [ ] Add integrations with issue trackers and CI simulators. 
- [ ] Harden against failure modes (tool errors, ambiguous specs, flaky tests).
- [ ] Publish documentation and onboarding guide for contributors.

---

Progress on each phase should be reflected here and in `docs/DEV_NOTES.md`. Link major architectural decisions to ADRs (to be added) for traceability.
