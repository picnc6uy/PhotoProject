# Agent Orchestration Best Practices

_Last updated: 2026-02-10_

## High-level Design
- **Plan → Act → Observe → Reflect loop**: Encourage agents to generate a plan, execute incremental actions, and reflect on outcomes before proceeding.
- **Explicit state management**: Track iterations, decisions, and artifacts (plans, code diffs, test results) to support reproducibility and auditing.
- **Composable agents**: Design agents with clear capabilities (planner, implementer, reviewer) so they can be orchestrated in pipelines or multi-agent scenarios.

## Tool Integration
- **Declarative tool registry**: Register tools with names, descriptions, and permission levels; make availability explicit to agents.
- **Structured inputs/outputs**: Use JSON schemas or dataclasses for tool I/O to reduce parsing errors.
- **Safety guards**: Wrap shell/git operations with allowlists, dry-run options, and logging. Require human approval for destructive commands.

## Memory & Context
- **Short-term memory**: Maintain iteration state (current plan index, recent observations).
- **Long-term knowledge**: Store reusable insights (e.g., knowledge-base Markdown files) and load them before planning.
- **Citation discipline**: Encourage agents to cite which documents or experiments informed their decisions.

## Evaluation & Testing
- **Unit tests for components**: Each reasoning capability or tool adapter should have targeted unit tests.
- **Scenario/acceptance tests**: Simulate end-to-end tasks that mirror real developer workflows (ticket intake → code change → tests → summary).
- **Regression dashboards**: Track pass/fail history to catch performance drift.

## Collaboration Patterns
- **Coordinator agent**: Oversees task decomposition, assigns subtasks, and aggregates results.
- **Reviewer agent**: Provides independent critique of plans, code, or documentation before final delivery.
- **Escalation protocol**: If agents detect ambiguity or unsafe requirements, escalate to the human operator.

## Operational Recommendations
- **Version control discipline**: Agents should make atomic changes, run tests, and prepare diffs with clear commit messages.
- **Documentation updates**: Modify README/roadmaps/dev notes alongside code to keep humans informed.
- **Telemetry**: Log actions, decisions, and observations for debugging and compliance.

Use this document to validate orchestration logic and to inform new agent designs.
