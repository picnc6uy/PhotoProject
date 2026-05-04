"""Agent that executes configured test commands."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec
from ..tools import ToolContext


class TestRunnerAgent(Agent):
    """Runs lint/tests and records results."""

    __test__ = False

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Collect test commands",
            "Execute commands",
            "Summarize results",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        artifacts = state.artifacts.setdefault("test_run", {
            "commands": [],
            "results": [],
            "summary": {},
        })

        if "Collect" in step:
            commands = task.metadata.get("test_commands", []) if task.metadata else []
            artifacts["commands"] = commands
            return {"step": step, "result": {"commands": commands}}

        if "Execute" in step:
            results = self._execute_commands(artifacts.get("commands", []))
            artifacts["results"] = results
            return {"step": step, "result": {"results": results}}

        summary = self._summarize(artifacts.get("results", []))
        artifacts["summary"] = summary
        return {"step": step, "result": {"summary": summary}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Processed {len(value)} {key}."
        passed = value.get("passed", 0)
        failed = value.get("failed", 0)
        return f"Test summary recorded ({passed} passed / {failed} failed)."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("test_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        summary = state.artifacts.get("test_run", {}).get("summary", {})
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        return f"Executed tests for '{task.title}' ({passed} passed / {failed} failed)."

    def _execute_commands(self, commands: List[str]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        tool = self.tools.get("shell")
        for command in commands:
            if not tool:
                results.append({"command": command, "status": "skipped", "output": "shell tool unavailable"})
                continue
            output = tool.run(command, ToolContext(working_dir="/workspace"))
            status = "passed" if "error" not in output.lower() else "failed"
            results.append({
                "command": command,
                "status": status,
                "output": output,
            })
        return results

    def _summarize(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"passed": 0, "failed": 0, "skipped": 0}
        for result in results:
            status = result.get("status", "skipped")
            if status not in summary:
                summary[status] = 0
            summary[status] += 1
        return summary
