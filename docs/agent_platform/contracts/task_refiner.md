# TaskRefiner Contract

- **Purpose**: Clarify requirements and produce structured acceptance criteria.
- **Inputs**: `TaskSpec` (requirements, metadata).
- **Outputs**:
  - `refined_spec.requirements` (baseline copies)
  - `refined_spec.clarifications`
  - `refined_spec.acceptance` (with automated/manual checks)
  - `refinement_notes`
- **Safety**: No external side effects; updates are confined to artefacts.
- **Special Considerations**: Automated checks mirror `metadata.test_commands`; manual notes enumerate clarifications.
