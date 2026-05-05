"""Agent that provides adversarial critique of plans and proposed changes."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec


class RedTeamReviewer(Agent):
    """Highlights risks, missing evidence, and escalation needs."""

    __test__ = False

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Question assumptions",
            "Probe evidence gaps",
            "Issue adversarial verdict",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        review = state.artifacts.setdefault("red_team", {
            "assumptions": [],
            "gaps": [],
            "verdict": "inconclusive",
        })

        metadata = task.metadata or {}

        if "Question" in step:
            assumptions = self._surface_assumptions(task, metadata)
            review["assumptions"] = assumptions
            return {"step": step, "result": {"assumptions": assumptions}}

        if "Probe" in step:
            gaps = self._find_gaps(metadata)
            review["gaps"] = gaps
            return {"step": step, "result": {"gaps": gaps}}

        verdict = self._form_verdict(review)
        review["verdict"] = verdict
        return {"step": step, "result": {"verdict": verdict}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Logged {len(value)} potential {key}."
        return f"Adversarial verdict: {value}."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("red_team_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        verdict = state.artifacts.get("red_team", {}).get("verdict", "inconclusive")
        return f"Red team verdict for '{task.title}': {verdict}."

    def _surface_assumptions(self, task: TaskSpec, metadata: Dict[str, Any]) -> List[str]:
        assumptions: List[str] = []
        if not task.requirements:
            assumptions.append("Scope may be under-specified; requirements list is empty.")
        if not metadata.get("test_commands"):
            assumptions.append("Plan assumes tests exist but none are configured.")
        if not metadata.get("risk_level"):
            assumptions.append("Risk level unspecified; defaulting to medium may hide exposure.")
        return assumptions or ["No obvious assumptions challenged."]

    def _find_gaps(self, metadata: Dict[str, Any]) -> List[str]:
        gaps: List[str] = []
        if metadata.get("test_results") is None:
            gaps.append("No test results provided for validation.")
        if metadata.get("review_decision") not in {"approved", "approve_with_comments"}:
            gaps.append("Review gate not satisfied; changes requested remain open.")
        if not metadata.get("rollback_plan") and metadata.get("requires_rollback_plan"):
            gaps.append("Rollback plan required but missing.")
        return gaps or ["No major evidence gaps detected."]

    def _form_verdict(self, review: Dict[str, Any]) -> str:
        gaps = review.get("gaps", [])
        if any("missing" in gap.lower() for gap in gaps):
            return "reject"
        if any("assumptions" in note.lower() for note in review.get("assumptions", [])):
            return "escalate"
        return "accept"
