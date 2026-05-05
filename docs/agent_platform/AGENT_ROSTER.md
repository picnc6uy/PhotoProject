# Agent Roster & Design Progression

_Last updated: 2026-02-10_

This document enumerates the planned agents from simplest to most complex, capturing their purpose, key inputs/outputs, and dependencies. Agents inherit from the shared base classes in `agent_platform.agents` and rely on the Orchestrator for execution and caching.

| Order | Agent | Purpose | Key Inputs | Key Outputs | Dependencies |
|-------|-------|---------|------------|-------------|--------------|
| 1 | **ResourceSurveyor** | Compile workspace context and highlight relevant docs/tools for a task. | `TaskSpec` with minimal metadata. | Summary list of docs/tools/tests to load. | ToolRegistry (read-only), knowledge base. |
| 2 | **TaskRefiner** | Clarify and expand requirements, producing structured acceptance criteria. | TaskSpec + ResourceSurveyor summary. | Updated TaskSpec with refined requirements & acceptance. | ResourceSurveyor. |
| 3 | **RiskMonitor** | Surface dependencies, risk level, and mitigation guidance. | Refined TaskSpec (+ metadata). | Risk report (level, dependencies, mitigations). | TaskRefiner. |
| 4 | **PlannerAgent** | Break work into milestones and assign agent responsibilities. | Refined TaskSpec + risk report. | Structured plan (milestones, agent assignments). | TaskRefiner, RiskMonitor, ToolRegistry. |
| 5 | **DesignAdvisor** | Produce architecture sketches and component outlines for changes. | Planner output. | Design synopsis + ADR suggestions. | PlannerAgent. |
| 6 | **ImplementerAgent** | Generate code changes for a single work item. | Planner milestone + design notes. | Proposed diffs / patch instructions. | ToolRegistry (editor, git). |
| 7 | **TestRunnerAgent** | Run designated tests, lint, and static analysis. | Implementer output + configured test commands. | Test results, logs, failure summaries. | ToolRegistry (shell, pytest). |
| 8 | **CodeReviewer** | Evaluate code quality, style, and logical soundness. | Implementer output, test results. | Review comments, change requests. | ImplementerAgent, TestRunnerAgent. |
| 9 | **RequirementsVerifier** | Ensure acceptance criteria are satisfied and gaps flagged. | Implementer output, refined acceptance criteria. | Verification checklist, unmet criteria. | TaskRefiner, CodeReviewer. |
| 10 | **RedTeamReviewer** | Provide adversarial review and highlight escalation needs. | Planner/test/review metadata. | Risk findings, adversarial verdict. | CodeReviewer, RequirementsVerifier. |
| 11 | **IntegratorAgent** | Stage accepted changes, prepare commits, update docs. | Approved diffs + review notes. | Commit message, documentation updates, merge instructions. | CodeReviewer, RequirementsVerifier, RedTeamReviewer, ToolRegistry (git, docs). |
| 12 | **ReleaseCoordinator** | Orchestrate deployment tasks, publish artifacts, notify stakeholders. | Integrator output + release config. | Release checklist, deployment logs, notifications. | IntegratorAgent, external services. |
| 13 | **PostMergeObserver** | Monitor post-release signals and trigger rollback if needed. | Release artifacts, monitoring feeds. | Observation report, rollback recommendation. | ReleaseCoordinator, external telemetry. |

## Design Notes
- Early agents (ResourceSurveyor → RiskMonitor) are read-only and establish context before changes are proposed.
- Implementer/TestRunner/CodeReviewer/RequirementsVerifier form the execution core and must operate under strict safety controls.
- RedTeamReviewer adds adversarial scrutiny before integration.
- Integrator, ReleaseCoordinator, and PostMergeObserver depend on solid auditing and human checkpoints before automated promotion/rollback logic is trusted.

## Next Actions
1. Implement ResourceSurveyor, TaskRefiner, and RiskMonitor (✔️).
2. Implement PlannerAgent, DesignAdvisor, and ImplementerAgent with iterative tests (✔️).
3. Implement TestRunnerAgent, CodeReviewer, and RequirementsVerifier with workflow validation (✔️).
4. Implement IntegratorAgent, ReleaseCoordinator, and PostMergeObserver with stage-four tests (✔️).
5. Extend the Orchestrator to support DAG execution (ResourceSurveyor → TaskRefiner → RiskMonitor → PlannerAgent → …).
6. Define contracts/ADR entries for cross-agent orchestration and tooling policies, including red-team escalation paths.
