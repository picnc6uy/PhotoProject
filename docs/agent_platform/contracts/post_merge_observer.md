# PostMergeObserver Contract

- **Purpose**: Assess post-release telemetry and recommend follow-up actions.
- **Inputs**: `metadata.monitoring_signals`, release context (e.g., rollback plan requirement).
- **Outputs**:
  - `postmerge.signals`
  - `postmerge.analysis`
  - `postmerge.recommendation` (`monitor`, `extend_monitoring`, `rollback`)
  - `postmerge_notes`
- **Safety**: Read-only; ensures alerts surface before issues escalate.
- **Dependencies**: ReleaseCoordinator outputs, monitoring infrastructure.
