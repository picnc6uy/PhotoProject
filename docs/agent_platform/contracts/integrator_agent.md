# IntegratorAgent Contract

- **Purpose**: Stage approved changes, draft commit message, and plan documentation updates.
- **Inputs**: `metadata.proposed_changes`, review notes, doc updates, ToolRegistry (shell/git).
- **Outputs**:
  - `integration.staging`
  - `integration.commit_message`
  - `integration.docs`
  - `integration_notes`
- **Safety**: Respects ShellCommandTool allow-list; must not proceed if RedTeamReviewer verdict is `reject/escalate` without human approval.
- **Dependencies**: CodeReviewer approval, RequirementsVerifier coverage, RedTeamReviewer verdict.
