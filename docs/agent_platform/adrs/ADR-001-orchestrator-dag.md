# ADR-001: Orchestrator DAG Responsibilities

*Status*: Accepted  
*Date*: 2026-05-04

## Context
We have twelve production agents (plus RedTeamReviewer) that collectively transform a task into release-ready outputs. The `Orchestrator` currently supports single-agent runs with caching; a new `run_workflow` helper can now execute the entire sequence. We need a documented decision describing how the DAG should be constructed, what metadata is passed between agents, and how results are persisted for evaluation.

## Decision
- The canonical execution order is:
  1. ResourceSurveyor
  2. TaskRefiner
  3. RiskMonitor
  4. PlannerAgent
  5. DesignAdvisor
  6. ImplementerAgent
  7. TestRunnerAgent
  8. CodeReviewer
  9. RequirementsVerifier
  10. RedTeamReviewer
  11. IntegratorAgent
  12. ReleaseCoordinator
  13. PostMergeObserver
  14. AgentArchitect (retro/post-mortem)
- `Orchestrator.run_workflow` takes a sequence of agent classes and returns a mapping of agent name to serialized records (plan, actions, artefacts, notes, outcome).
- Each agent receives the same `TaskSpec`. Agents append metadata outputs to the spec via artefacts; downstream systems read the orchestrator records rather than mutating the task in-place.
- Evaluation scripts must store the `run_workflow` output in `dev_data/agent_platform/evaluations/<timestamp>.json` for regression tracking.

## Consequences
- The DAG order is encoded in both the ADR and `tools/agent_platform/run_workflow.py`; future changes require revising this ADR (or issuing a superseding ADR).
- Consumers that need cross-agent data consult the orchestrator records instead of relying on mutable shared state.
- The evaluation harness can replay runs deterministically by reusing the cache key and serialized record set.
