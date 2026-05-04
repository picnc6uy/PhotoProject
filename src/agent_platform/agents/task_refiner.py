"""Agent that refines task requirements and acceptance criteria."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import AcceptanceCriteria, TaskSpec


class TaskRefiner(Agent):
    """Produces clarified requirements and acceptance criteria."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Review current requirements",
            "Propose clarifications",
            "Draft acceptance criteria",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        refined = state.artifacts.setdefault("refined_spec", {
            "requirements": list(task.requirements),
            "clarifications": [],
            "acceptance": [],
        })

        if "Review" in step:
            summary = {
                "requirement_count": len(refined["requirements"]),
                "missing_acceptance": len(task.acceptance) == 0,
            }
            action_result = {"summary": summary}
        elif "clarifications" in step:
            clarifications = self._derive_clarifications(task)
            refined["clarifications"] = clarifications
            action_result = {"clarifications": clarifications}
        else:
            acceptance = self._derive_acceptance(task, refined["clarifications"])
            refined["acceptance"] = acceptance
            action_result = {"acceptance": acceptance}

        return {
            "step": step,
            "result": action_result,
        }

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            count = len(value)
            return f"Prepared {count} {key}."
        return "Reviewed existing requirements."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("refinement_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        refined = state.artifacts.get("refined_spec", {})
        clarifications = refined.get("clarifications", [])
        acceptance = refined.get("acceptance", [])
        return (
            f"Refined task '{task.title}' with {len(clarifications)} clarifications and {len(acceptance)} acceptance criteria."
        )

    def _derive_clarifications(self, task: TaskSpec) -> List[str]:
        clarifications: List[str] = []
        if not task.requirements:
            clarifications.append("Explicit requirements not provided; confirm scope with requester.")
        if task.metadata.get("risk_level") == "high":
            clarifications.append("High-risk change: require rollback plan and approvals.")
        if task.metadata.get("touches_docs"):
            clarifications.append("Ensure documentation updates are covered in acceptance criteria.")
        return clarifications or ["No additional clarifications identified."]

    def _derive_acceptance(
        self,
        task: TaskSpec,
        clarifications: List[str],
    ) -> List[Dict[str, Any]]:
        acceptance: List[Dict[str, Any]] = []
        base_requirements = task.requirements or [task.summary]
        for idx, requirement in enumerate(base_requirements, start=1):
            acceptance.append({
                "id": f"AC-{idx:02d}",
                "description": requirement,
                "automated_checks": task.metadata.get("test_commands", []),
                "manual_notes": clarifications,
            })
        if not acceptance:
            acceptance.append({
                "id": "AC-00",
                "description": "Task owner to confirm acceptance criteria.",
                "automated_checks": [],
                "manual_notes": clarifications,
            })
        return acceptance
