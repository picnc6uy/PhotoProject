# AgentArchitect Contract

- **Purpose**: Summarise planning insights, knowledge references, and future improvements.
- **Inputs**: `TaskSpec.metadata` (knowledge topics, focus area, test commands); ToolRegistry.
- **Outputs**:
  - `architecture_notes` with step observations and recommendations
  - `state.outcome` summarising plan coverage
- **Safety**: Read-only; ensures knowledge lenses are applied and future milestones recorded.
- **Dependencies**: Entire workflow artefacts; knowledge base for references.
