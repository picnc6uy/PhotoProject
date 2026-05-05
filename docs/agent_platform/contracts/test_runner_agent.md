# TestRunnerAgent Contract

- **Purpose**: Execute configured test commands and report results.
- **Inputs**: `TaskSpec.metadata.test_commands`; ShellCommandTool via ToolRegistry.
- **Outputs**:
  - `test_run.commands`
  - `test_run.results` (per command)
  - `test_run.summary` (passed/failed/skipped counts)
  - `test_notes`
- **Safety**: Limited to allow-listed commands (default: echo, pytest, flake8, git status/add); additional commands require approval.
- **Dependencies**: ImplementerAgent outputs; ShellCommandTool configuration.
