# RiskMonitor Contract

- **Purpose**: Identify risk level, dependencies, and mitigations.
- **Inputs**: `TaskSpec.metadata` (risk_level, dependencies, flags like `touches_ci`).
- **Outputs**:
  - `risk_report.risk_level`
  - `risk_report.dependencies`
  - `risk_report.mitigations`
  - `risk_notes`
- **Safety**: Read-only; provides guidance only.
- **Alert Conditions**: High risk triggers mitigations such as rollback planning and paired review.
