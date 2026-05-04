"""Agent that verifies acceptance criteria coverage."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import AcceptanceCriteria, TaskSpec


class RequirementsVerifier(Agent):
    """Ensures acceptance criteria are addressed by proposed work."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Load acceptance criteria",
            "Evaluate coverage",
            "Summarize verification",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        verification = state.artifacts.setdefault("verification", {
            "acceptance": [],
            "results": [],
            "summary": {},
        })

        if "Load" in step:
            acceptance = self._normalize_acceptance(task.acceptance)
            verification["acceptance"] = acceptance
            return {"step": step, "result": {"acceptance": acceptance}}

        if "Evaluate" in step:
            coverage = self._evaluate_coverage(
                verification.get("acceptance", []),
                task.metadata.get("proposed_changes", []) if task.metadata else [],
            )
            verification["results"] = coverage
            return {"step": step, "result": {"results": coverage}}

        summary = self._summarize(verification.get("results", []))
        verification["summary"] = summary
        return {"step": step, "result": {"summary": summary}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            satisfied = sum(1 for item in value if item.get("satisfied"))
            total = len(value)
            return f"Verified {satisfied}/{total} criteria." if total else "No criteria to verify."
        return "Verification summary recorded."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("verification_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        summary = state.artifacts.get("verification", {}).get("summary", {})
        return (
            f"Verification summary for '{task.title}': {summary.get('satisfied', 0)} satisfied, "
            f"{summary.get('unsatisfied', 0)} unsatisfied."
        )

    def _normalize_acceptance(self, acceptance: List[AcceptanceCriteria] | List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for criterion in acceptance:
            if isinstance(criterion, AcceptanceCriteria):
                normalized.append({
                    "id": getattr(criterion, "description", ""),
                    "description": criterion.description,
                })
            else:
                normalized.append({
                    "id": criterion.get("id", criterion.get("description", "AC")),
                    "description": criterion.get("description", ""),
                })
        return normalized

    def _evaluate_coverage(
        self,
        acceptance: List[Dict[str, Any]],
        proposed_changes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        change_text = "\n".join(change.get("step", "") for change in proposed_changes)
        for criterion in acceptance:
            desc = criterion.get("description", "")
            satisfied = desc.lower() in change_text.lower()
            results.append({
                "id": criterion.get("id", ""),
                "description": desc,
                "satisfied": satisfied,
                "reason": "Found reference in proposed changes." if satisfied else "No matching change found.",
            })
        return results

    def _summarize(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"satisfied": 0, "unsatisfied": 0}
        for result in results:
            key = "satisfied" if result.get("satisfied") else "unsatisfied"
            summary[key] += 1
        return summary
