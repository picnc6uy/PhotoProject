"""Agent that prepares implementation steps for a milestone."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec
from ..tools import ToolContext


class ImplementerAgent(Agent):
    """Generates change proposals and shell command drafts for milestones."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Select milestone",
            "Draft implementation steps",
            "Propose code changes",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        work = state.artifacts.setdefault("work_plan", {
            "milestone": None,
            "steps": [],
            "proposed_changes": [],
        })

        metadata = task.metadata or {}
        milestones = metadata.get("milestones") or []

        if "Select" in step:
            milestone = milestones[0] if milestones else {
                "id": "MS-00",
                "description": task.summary,
            }
            work["milestone"] = milestone
            return {"step": step, "result": {"milestone": milestone}}

        if "Draft implementation" in step:
            steps = self._draft_steps(work["milestone"], task)
            work["steps"] = steps
            return {"step": step, "result": {"steps": steps}}

        proposed = self._propose_changes(work["steps"], task)
        work["proposed_changes"] = proposed
        return {"step": step, "result": {"proposed_changes": proposed}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Outlined {len(value)} {key}."
        return "Selected target milestone."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("implementation_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        change_count = len(state.artifacts.get("work_plan", {}).get("proposed_changes", []))
        return f"Prepared {change_count} proposed change(s) for '{task.title}'."

    def _draft_steps(self, milestone: Dict[str, Any], task: TaskSpec) -> List[str]:
        description = milestone.get("description", task.summary)
        steps = [
            f"Review existing modules related to '{description}'.",
            "Update implementation according to design notes.",
            "Write or update tests covering new behaviour.",
        ]
        if task.metadata.get("touches_docs"):
            steps.append("Prepare documentation updates to reflect changes.")
        return steps

    def _propose_changes(self, steps: List[str], task: TaskSpec) -> List[Dict[str, Any]]:
        tool = self.tools.get("shell")
        proposals: List[Dict[str, Any]] = []
        for idx, step in enumerate(steps, start=1):
            command = f"echo TODO step {idx}: {step}"
            output = ""
            if tool:
                output = tool.run(command, ToolContext(working_dir="/workspace"))
            proposals.append({
                "step": step,
                "command": command,
                "tool_output": output,
            })
        return proposals
