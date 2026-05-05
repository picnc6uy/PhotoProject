# RedTeamReviewer Contract

- **Purpose**: Provide adversarial critique and escalate unresolved risks.
- **Inputs**: Planner/TestRunner/Reviewer metadata (test results, review decision, rollback plan).
- **Outputs**:
  - `red_team.assumptions`
  - `red_team.gaps`
  - `red_team.verdict` (`accept`, `escalate`, `reject`)
  - `red_team_notes`
- **Safety**: Must run before integration; `reject` or `escalate` requires human sign-off.
- **Dependencies**: CodeReviewer decision, RequirementsVerifier summary, risk metadata.
