# ReleaseCoordinator Contract

- **Purpose**: Prepare deployment checklist, commands, and stakeholder notification.
- **Inputs**: Integrator outputs, release metadata (`deployment_commands`, `requires_rollback_plan`).
- **Outputs**:
  - `release.checklist`
  - `release.commands`
  - `release.notification`
  - `release_notes`
- **Safety**: Generates plan only; actual deployment commands must remain allow-listed or require manual approval.
- **Dependencies**: IntegratorAgent staging outputs, change management policies.
