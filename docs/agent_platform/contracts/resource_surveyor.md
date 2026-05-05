# ResourceSurveyor Contract

- **Purpose**: Collect workspace references (docs, tools, knowledge topics) before planning begins.
- **Inputs**:
  - `TaskSpec.metadata.workspace_docs` (optional override)
  - `ToolRegistry` listing registered tooling
- **Outputs**:
  - `survey.documents`, `survey.tools`, `survey.knowledge_topics`
  - `survey_notes` capturing step observations
- **Safety**: Read-only; no side effects beyond logging.
- **Dependencies**: Knowledge base at `docs/agent_platform/knowledge/`.
