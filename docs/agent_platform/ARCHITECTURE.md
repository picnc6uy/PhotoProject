# Agent Platform Architecture Overview

_Last updated: 2026-02-10_

This document describes the high-level design for the agentic software-development workflow, including orchestration, knowledge management, and the future DAG of collaborating agents. It is intended for the full team.

## Narrative Summary

1. **Inputs & Knowledge Loading**
   - The orchestrator receives a task specification or project brief.
   - Knowledge base summaries (e.g., OpenAI agent design, safety guidelines) are injected into the task metadata so agents begin with shared context.

2. **Orchestration & Caching**
   - The `Orchestrator` loads the appropriate agent (e.g., `AgentArchitect`, future planner, implementer, reviewer) from the registry.
   - `CacheStore` ensures repeat runs reuse JSON artefacts whenever inputs have not changed.

3. **Agent DAG Execution (Future State)**
   - `AgentArchitect` produces a roadmap and identifies required sub-agents/tools.
   - A planned DAG coordinates specialised agents: Planner → Implementer → Reviewer → QA/Eval.
   - Each agent is configured with the `ToolRegistry` for controlled access to shell, git, editor, tests, etc.

4. **Artefact Persistence & Evaluation**
   - All agent states (plans, actions, artefacts, notes) are serialised by the orchestrator.
   - Evaluation harnesses consume these artefacts to run regression suites and scenario-based tests.

## PlantUML Diagram

```plantuml
autonumber
title Agent Platform DAG Overview

actor "Task Requester" as requester
rectangle "Knowledge Base\n(docs/agent_platform/knowledge)" as knowledge
rectangle "Tool Registry" as tools
rectangle "CacheStore" as cache
rectangle "Evaluation Harness" as eval

package "Orchestrator" {
  rectangle "Orchestrator\n(src/agent_platform/orchestrator.py)" as orchestrator
}

package "Agents" {
  rectangle "AgentArchitect\n(plan & roadmap)" as architect
  rectangle "Planner Agent\n(task decomposition" as planner
  rectangle "Implementer Agent\n(code generation" as implementer
  rectangle "Reviewer Agent\n(code & plan critique" as reviewer
  rectangle "QA Agent\n(test execution" as qa
}

requester --> orchestrator : submit TaskSpec
knowledge --> orchestrator : load knowledge_topics
orchestrator --> cache : make_key/task lookup
cache --> orchestrator : cached record?
orchestrator --> architect : run initial plan
architect --> tools : enumerate required tools
architect --> planner : deliver roadmap
planner --> implementer : create work items
implementer --> tools : controlled shell/git/editor usage
implementer --> reviewer : deliver changes
reviewer --> qa : request validation
qa --> tools : *pytest*, linters, static analysis
qa --> orchestrator : results & artefacts
orchestrator --> cache : save record
orchestrator --> eval : provide run artefacts
orchestrator --> requester : deliver summary & artefacts

note bottom of tools
  Tool access is gated with permissions,
  logging, and human-in-the-loop checkpoints.
end note

note right of eval
  Future integration: scenario tests,
  regression dashboards, and metrics.
end note
```

## Implementation Considerations
- **Agent Expansion**: Planner/Implementer/Reviewer/QA agents will follow the same base class interfaces used by `AgentArchitect`.
- **Permissions**: Tool registry should encode allowlists (e.g., read-only git vs. commit) and escalate to humans for high-risk actions.
- **Evaluation Hooks**: Orchestrator records will feed an evaluation harness that runs regression suites and produces dashboards.
- **Multi-Agent Coordination**: DAG execution can be represented as a dependency graph where each agent emits artefacts consumed by downstream agents.

## Next Steps
1. Extend the orchestrator to spawn planner/implementer/reviewer agents following the DAG described above.
2. Formalise tool adapters (shell, git, editor, test runner) with sandboxing and auditing.
3. Define agent-specific contracts and structured output schemas (Pydantic) for each node in the DAG.
4. Document architecture decisions (ADRs) as components mature.
```}