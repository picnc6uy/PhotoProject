"""Agent that coordinates release activities."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec


class ReleaseCoordinator(Agent):
    """Handles release checklist, deployment commands, and notifications."""

    __test__ = False

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Compile release checklist",
            "Prepare deployment commands",
            "Draft stakeholder notification",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        release = state.artifacts.setdefault("release", {
            "checklist": [],
            "commands": [],
            "notification": "",
        })

        metadata = task.metadata or {}

        if "Compile" in step:
            checklist = self._build_checklist(metadata)
            release["checklist"] = checklist
            return {"step": step, "result": {"checklist": checklist}}

        if "Prepare deployment" in step:
            commands = metadata.get("deployment_commands", ["./deploy.sh"])
            release["commands"] = commands
            return {"step": step, "result": {"commands": commands}}

        notification = self._draft_notification(task, release["checklist"])
        release["notification"] = notification
        return {"step": step, "result": {"notification": notification}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Prepared {len(value)} {key}."
        return "Notification drafted."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("release_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        checklist = state.artifacts.get("release", {}).get("checklist", [])
        return f"Release checklist prepared with {len(checklist)} item(s) for '{task.title}'."

    def _build_checklist(self, metadata: Dict[str, Any]) -> List[str]:
        checklist = [
            "Confirm approvals",
            "Tag release",
            "Notify stakeholders",
        ]
        if metadata.get("requires_rollback_plan"):
            checklist.append("Review rollback plan")
        if metadata.get("compliance_review"):
            checklist.append("Document compliance review")
        return checklist

    def _draft_notification(self, task: TaskSpec, checklist: List[str]) -> str:
        title = task.title
        summary = task.summary
        checklist_str = "\n".join(f"- {item}" for item in checklist)
        return f"Release Update: {title}\n\nSummary:\n{summary}\n\nChecklist:\n{checklist_str}"
