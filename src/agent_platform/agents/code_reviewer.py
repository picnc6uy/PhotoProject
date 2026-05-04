"""Agent that reviews proposed changes and test outcomes."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec


class CodeReviewer(Agent):
    """Provides review feedback on implementation proposals."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Review proposed changes",
            "Evaluate test results",
            "Issue review decision",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        review = state.artifacts.setdefault("review", {
            "comments": [],
            "decision": "pending",
            "risks": [],
        })

        metadata = task.metadata or {}
        if "Review proposed" in step:
            comments = self._review_changes(metadata.get("proposed_changes", []))
            review["comments"] = comments
            return {"step": step, "result": {"comments": comments}}

        if "Evaluate test" in step:
            risks = self._analyse_tests(metadata.get("test_results", []))
            review["risks"] = risks
            return {"step": step, "result": {"risks": risks}}

        decision = self._decide(review)
        review["decision"] = decision
        return {"step": step, "result": {"decision": decision}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Recorded {len(value)} {key}."
        return f"Review decision: {value}."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("review_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        decision = state.artifacts.get("review", {}).get("decision", "pending")
        return f"Review decision for '{task.title}': {decision}."

    def _review_changes(self, proposed_changes: List[Dict[str, Any]]) -> List[str]:
        comments: List[str] = []
        if not proposed_changes:
            comments.append("No proposed changes were supplied for review.")
            return comments
        for change in proposed_changes:
            step = change.get("step", "")
            if "tests" not in step.lower():
                comments.append(f"Confirm tests cover: {step}")
        return comments

    def _analyse_tests(self, test_results: List[Dict[str, Any]]) -> List[str]:
        risks: List[str] = []
        for result in test_results:
            if result.get("status") != "passed":
                risks.append(f"Test failed: {result.get('command')}")
        if not test_results:
            risks.append("No tests executed; require validation before merge.")
        return risks

    def _decide(self, review: Dict[str, Any]) -> str:
        if review.get("risks"):
            return "changes_requested"
        if review.get("comments"):
            return "approve_with_comments"
        return "approved"
