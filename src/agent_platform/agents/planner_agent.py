"""Agent that produces milestone plans for tasks."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec


class PlannerAgent(Agent):
    """Breaks refined requirements into scheduled milestones."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Analyse requirements",
            "Draft milestones",
            "Assign agent roles",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        milestones = state.artifacts.setdefault("milestones", [])

        if "Analyse" in step:
            summary = {
                "requirement_count": len(task.requirements),
                "risk_level": task.metadata.get("risk_level", "medium"),
            }
            return {"step": step, "result": {"analysis": summary}}

        if "Draft" in step:
            drafted = self._draft_milestones(task)
            milestones.extend(drafted)
            return {"step": step, "result": {"milestones": drafted}}

        assignments = self._assign_roles(milestones)
        return {"step": step, "result": {"assignments": assignments}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Prepared {len(value)} {key}."
        return "Completed analysis."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("plan_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        milestone_count = len(state.artifacts.get("milestones", []))
        return f"Generated {milestone_count} milestones for '{task.title}'."

    def _draft_milestones(self, task: TaskSpec) -> List[Dict[str, Any]]:
        milestones: List[Dict[str, Any]] = []
        requirements = task.requirements or [task.summary]
        for idx, requirement in enumerate(requirements, start=1):
            milestones.append({
                "id": f"MS-{idx:02d}",
                "description": requirement,
                "risk_level": task.metadata.get("risk_level", "medium"),
            })
        return milestones

    def _assign_roles(self, milestones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        assignments: List[Dict[str, Any]] = []
        default_agents = ["DesignAdvisor", "ImplementerAgent", "TestRunnerAgent"]
        for index, milestone in enumerate(milestones):
            agent_role = default_agents[min(index, len(default_agents) - 1)]
            assignments.append({
                "milestone_id": milestone["id"],
                "agent": agent_role,
            })
        return assignments
