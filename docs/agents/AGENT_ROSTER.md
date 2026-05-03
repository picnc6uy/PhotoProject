# Agent Roster & Design Progression

_Last updated: 2026-02-10_

This document enumerates the planned agents from simplest to most complex, capturing their purpose, key inputs/outputs, and dependencies. Agents inherit from the shared base classes in `agent_platform.agents` and rely on the Orchestrator for execution and caching.

| Order | Agent | Purpose | Key Inputs | Key Outputs | Dependencies |
|-------|-------|---------|------------|-------------|--------------|
| 1 | **ResourceSurveyor** | Compile workspace context and highlight relevant docs/tools for a task. | `TaskSpec` with minimal metadata. | Summary list of docs/tools/tests to load. | ToolRegistry (read-only), knowledge base. |
| 2 | **TaskRefiner** | Clarify and expand requirements, producing structured acceptance criteria. | TaskSpec + ResourceSurveyor summary. | Updated TaskSpec with refined requirements & acceptance. | ResourceSurveyor. |
| 3 | **PlannerAgent** | Break work into milestones and assign agent responsibilities. | Refined TaskSpec. | Structured plan (milestones, agent assignments). | TaskRefiner, ToolRegistry. |
| 4 | **DesignAdvisor** | Produce architecture sketches and component outlines for changes. | Planner output. | Design synopsis + ADR suggestions. | PlannerAgent. |
| 5 | **ImplementerAgent** | Generate code changes for a single work item. | Planner milestone + design notes. | Proposed diffs / patch instructions. | ToolRegistry (editor, git). |
| 6 | **TestRunnerAgent** | Run designated tests, lint, and static analysis. | Implementer output + configured test commands. | Test results, logs, failure summaries. | ToolRegistry (shell, pytest). |
| 7 | **ReviewerAgent** | Critique proposed changes, ensure requirements met, flag issues. | Implementer output, test results. | Approval status, review comments, risk flags. | ImplementerAgent, TestRunnerAgent. |
| 8 | **IntegratorAgent** | Stage accepted changes, prepare commits, update docs. | Approved diffs + review notes. | Commit message, documentation updates, merge instructions. | ReviewerAgent, ToolRegistry (git, docs). |
| 9 | **ReleaseCoordinator** | Orchestrate deployment tasks, publish artifacts, notify stakeholders. | Integrator output + release config. | Release checklist, deployment logs, notifications. | IntegratorAgent, external services. |

## Design Notes
- Early agents (ResourceSurveyor → Planner) are low-risk and read-only; focus on high accuracy and structured summaries.
- Implementer/TestRunner/Reviewer form the execution core; they require stricter safety checks and human approval gates.
- Integrator and ReleaseCoordinator should only run once the team is confident in upstream agent reliability and auditing.

## Next Actions
1. Implement ResourceSurveyor and TaskRefiner leveraging the knowledge base summaries.
2. Extend Orchestrator to chain agent executions according to the plan graph (ResourceSurveyor → TaskRefiner → Planner).
3. Document each agent’s contract (purpose, inputs, outputs, schema) before implementation.
