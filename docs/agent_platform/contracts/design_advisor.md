# DesignAdvisor Contract

- **Purpose**: Provide component-level guidance and ADR suggestions.
- **Inputs**: Planner milestones via `TaskSpec.metadata.milestones`, optional component hints.
- **Outputs**:
  - `design.components`
  - `design_notes` (recommendations)
  - `design.adr_topics`
- **Safety**: Read-only; ensures documentation and architectural impacts are identified.
- **Dependencies**: PlannerAgent milestones; knowledge base for architecture references.
