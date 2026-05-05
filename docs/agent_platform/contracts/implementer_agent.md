# ImplementerAgent Contract

- **Purpose**: Draft implementation steps and initial change proposals.
- **Inputs**: Planner milestone (`metadata.milestones`), design notes, tool registry (shell/editor).
- **Outputs**:
  - `work_plan.milestone`
  - `work_plan.steps`
  - `work_plan.proposed_changes` (commands + tool output)
  - `implementation_notes`
- **Safety**: Must avoid destructive commands; relies on ShellCommandTool allow-list.
- **Dependencies**: DesignAdvisor recommendations and current ToolRegistry.
