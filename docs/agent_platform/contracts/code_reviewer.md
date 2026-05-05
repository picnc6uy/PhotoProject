# CodeReviewer Contract

- **Purpose**: Inspect proposed changes and test results for issues.
- **Inputs**: `metadata.proposed_changes`, `metadata.test_results`.
- **Outputs**:
  - `review.comments`
  - `review.risks`
  - `review.decision` (`approved`, `approve_with_comments`, `changes_requested`)
  - `review_notes`
- **Safety**: Read-only; decisions influence downstream agents (RequirementsVerifier, RedTeamReviewer, Integrator).
- **Dependencies**: ImplementerAgent outputs, TestRunnerAgent results.
