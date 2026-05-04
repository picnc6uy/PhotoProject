"""Agent that stages approved changes and prepares documentation updates."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec
from ..tools import ToolContext


class IntegratorAgent(Agent):
    """Stages code changes, drafts commit messages, and updates docs."""

    __test__ = False

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Prepare staging area",
            "Draft commit message",
            "Plan documentation updates",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        integration = state.artifacts.setdefault("integration", {
            "staging": [],
            "commit_message": "",
            "docs": [],
        })

        if "Prepare" in step:
            staging = self._prepare_staging(task)
            integration["staging"] = staging
            return {"step": step, "result": {"staging": staging}}

        if "Draft commit" in step:
            message = self._draft_commit_message(task)
            integration["commit_message"] = message
            return {"step": step, "result": {"commit_message": message}}

        docs = self._plan_docs(task)
        integration["docs"] = docs
        return {"step": step, "result": {"docs": docs}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Prepared {len(value)} {key}."
        return "Committed integration step."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("integration_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        return (
            f"Prepared integration plan for '{task.title}' with commit message and {len(state.artifacts.get('integration', {}).get('docs', []))} doc updates."
        )

    def _prepare_staging(self, task: TaskSpec) -> List[str]:
        tool = self.tools.get("shell")
        commands = [
            "git status",
            "git add .",
        ]
        outputs: List[str] = []
        for command in commands:
            if tool:
                outputs.append(tool.run(command, ToolContext(working_dir="/workspace")))
            else:
                outputs.append("shell tool unavailable")
        return outputs

    def _draft_commit_message(self, task: TaskSpec) -> str:
        title = task.title
        requirements = task.requirements or [task.summary]
        bullet_points = "\n".join(f"- {req}" for req in requirements)
        return f"{title}\n\nSummary:\n{bullet_points}"

    def _plan_docs(self, task: TaskSpec) -> List[str]:
        docs = task.metadata.get("doc_updates") if task.metadata else None
        if docs:
            return docs
        if task.metadata.get("touches_docs") if task.metadata else False:
            return ["README.md", "docs/DEV_NOTES.md"]
        return []
