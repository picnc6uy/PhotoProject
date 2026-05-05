# RequirementsVerifier Contract

- **Purpose**: Check acceptance criteria against proposed changes.
- **Inputs**: `TaskSpec.acceptance`, `metadata.proposed_changes`.
- **Outputs**:
  - `verification.acceptance`
  - `verification.results` (per criterion coverage)
  - `verification.summary`
  - `verification_notes`
- **Safety**: No side effects; provides confidence signal before integration.
- **Dependencies**: TaskRefiner acceptance entries, ImplementerAgent proposals, CodeReviewer decision.
