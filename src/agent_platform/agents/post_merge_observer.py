"""Agent that monitors post-release signals and recommends rollback if needed."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec


class PostMergeObserver(Agent):
    """Collects telemetry and assesses post-release health."""

    __test__ = False

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Gather monitoring data",
            "Analyse signals",
            "Recommend next steps",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        postmerge = state.artifacts.setdefault("postmerge", {
            "signals": [],
            "analysis": [],
            "recommendation": "monitor",
        })

        metadata = task.metadata or {}

        if "Gather" in step:
            signals = metadata.get("monitoring_signals", [
                {"metric": "error_rate", "value": 0.01},
                {"metric": "latency_ms", "value": 120},
            ])
            postmerge["signals"] = signals
            return {"step": step, "result": {"signals": signals}}

        if "Analyse" in step:
            analysis = self._analyse_signals(postmerge["signals"])
            postmerge["analysis"] = analysis
            return {"step": step, "result": {"analysis": analysis}}

        recommendation = self._recommend(postmerge["analysis"], metadata)
        postmerge["recommendation"] = recommendation
        return {"step": step, "result": {"recommendation": recommendation}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Processed {len(value)} {key}."
        return f"Recommendation: {value}."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("postmerge_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        recommendation = state.artifacts.get("postmerge", {}).get("recommendation", "monitor")
        return f"Post-merge recommendation for '{task.title}': {recommendation}."

    def _analyse_signals(self, signals: List[Dict[str, Any]]) -> List[str]:
        analysis: List[str] = []
        for signal in signals:
            metric = signal.get("metric")
            value = signal.get("value")
            if metric == "error_rate" and value and value > 0.05:
                analysis.append("Error rate exceeds threshold.")
            elif metric == "latency_ms" and value and value > 250:
                analysis.append("Latency degradation detected.")
        return analysis

    def _recommend(self, analysis: List[str], metadata: Dict[str, Any]) -> str:
        if analysis:
            return "rollback"
        if metadata.get("extended_monitoring"):
            return "extend_monitoring"
        return "monitor"
