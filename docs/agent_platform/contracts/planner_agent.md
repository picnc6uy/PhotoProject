# PlannerAgent Contract

- **Purpose**: Translate refined requirements into milestones and agent assignments.
- **Inputs**: `TaskSpec.requirements`, `TaskSpec.metadata.risk_level`.
- **Outputs**:
  - `milestones` list with IDs, descriptions, risk levels
  - `plan_notes` (analysis, drafted milestones, assignments)
- **Safety**: No side effects; produces planning artefacts for downstream agents.
- **Dependencies**: Upstream clarifications from TaskRefiner and risk assessment from RiskMonitor.
