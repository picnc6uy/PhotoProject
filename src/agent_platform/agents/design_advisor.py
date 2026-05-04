"""Agent that suggests architectural considerations for milestones."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec


class DesignAdvisor(Agent):
    """Produces design notes and ADR recommendations."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Inspect milestones",
            "Recommend component changes",
            "Suggest ADR topics",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        design = state.artifacts.setdefault("design", {
            "components": [],
            "adr_topics": [],
        })

        metadata = task.metadata or {}
        milestones = metadata.get("milestones", [])

        if "Inspect" in step:
            design["components"] = self._identify_components(task, milestones)
            return {"step": step, "result": {"components": design["components"]}}

        if "Recommend" in step:
            advice = self._component_recommendations(design["components"])
            return {"step": step, "result": {"recommendations": advice}}

        adr_topics = self._suggest_adrs(task, design["components"])
        design["adr_topics"] = adr_topics
        return {"step": step, "result": {"adr_topics": adr_topics}}

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        key = next(iter(action["result"].keys()))
        value = action["result"][key]
        if isinstance(value, list):
            return f"Prepared {len(value)} {key}."
        return "Generated design insight."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("design_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        topic_count = len(state.artifacts.get("design", {}).get("adr_topics", []))
        return f"Produced design guidance for '{task.title}' covering {topic_count} ADR topic(s)."

    def _identify_components(self, task: TaskSpec, milestones: List[Dict[str, Any]]) -> List[str]:
        components = task.metadata.get("components") or []
        if not components:
            components = ["agent_platform", "docs", "tests"]
        if milestones:
            for milestone in milestones:
                if "knowledge" in milestone["description"].lower():
                    components.append("knowledge_base")
        # remove duplicates while preserving order
        seen = set()
        ordered = []
        for comp in components:
            if comp not in seen:
                ordered.append(comp)
                seen.add(comp)
        return ordered

    def _component_recommendations(self, components: List[str]) -> List[str]:
        recommendations: List[str] = []
        for component in components:
            if component == "agent_platform":
                recommendations.append("Ensure orchestrator contracts are codified in ADRs.")
            elif component == "tests":
                recommendations.append("Add scenario tests validating agent DAG execution.")
            elif component == "knowledge_base":
                recommendations.append("Automate syncing of knowledge summaries before planning.")
            else:
                recommendations.append(f"Review {component} for documentation updates.")
        return recommendations

    def _suggest_adrs(self, task: TaskSpec, components: List[str]) -> List[str]:
        topics: List[str] = []
        if "agent_platform" in components:
            topics.append("ADR: Orchestrator DAG responsibilities")
        if task.metadata.get("risk_level") == "high":
            topics.append("ADR: Safety gating for high-risk agent actions")
        if task.metadata.get("touches_docs"):
            topics.append("ADR: Documentation workflow for agent-generated changes")
        return topics or ["ADR: Confirm architectural impact assessment"]
