"""Agent that identifies potential risks and dependencies for a task."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec


class RiskMonitor(Agent):
    """Evaluates task metadata to surface risk considerations."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Assess inherent task risk",
            "List dependencies and impact areas",
            "Recommend mitigations",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        assessment = state.artifacts.setdefault("risk_report", {
            "risk_level": task.metadata.get("risk_level", "medium"),
            "dependencies": [],
            "mitigations": [],
        })

        metadata = task.metadata or {}
        if "Assess" in step:
            level = metadata.get("risk_level") or self._infer_risk_level(task)
            assessment["risk_level"] = level
            action_result = {"risk_level": level}
        elif "dependencies" in step.lower():
            deps = metadata.get("dependencies") or []
            if metadata.get("touches_ci"):
                deps.append("Continuous Integration pipeline")
            if metadata.get("touches_docs"):
                deps.append("Documentation updates")
            assessment["dependencies"] = deps
            action_result = {"dependencies": deps}
        else:
            mitigations = self._recommend_mitigations(assessment, metadata)
            assessment["mitigations"] = mitigations
            action_result = {"mitigations": mitigations}

        return {
            "step": step,
            "result": action_result,
        }

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Logged {len(value)} {key}."
        return f"Risk level set to {value}."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("risk_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        report = state.artifacts.get("risk_report", {})
        level = report.get("risk_level", "unknown")
        return f"Risk level for '{task.title}' recorded as {level}."

    def _infer_risk_level(self, task: TaskSpec) -> str:
        metadata = task.metadata or {}
        if metadata.get("touches_production"):
            return "high"
        if metadata.get("touches_ci"):
            return "medium"
        return "low"

    def _recommend_mitigations(
        self,
        report: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> List[str]:
        mitigations: List[str] = []
        level = report.get("risk_level")
        if level == "high":
            mitigations.append("Require rollback plan and change management approval.")
            mitigations.append("Schedule paired review session.")
        if metadata.get("touches_ci"):
            mitigations.append("Coordinate with DevOps to schedule CI downtime if needed.")
        if metadata.get("touches_docs"):
            mitigations.append("Ensure documentation PR follows code changes.")
        return mitigations or ["No additional mitigations required."]
