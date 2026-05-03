"""Expert agent for designing other agents within the current workspace."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List
from pathlib import Path

from .base import Agent
from ..tasks import TaskSpec


class AgentArchitect(Agent):
    """An agent specialised in planning agent-development workflows."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Review workspace context and existing documentation",
            "Map available tools, tests, and configuration",
            "Outline agent capabilities and safety constraints",
            "Define implementation milestones and deliverables",
            "Recommend validation and iteration strategy",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        environment = self._build_environment_snapshot(task)
        recommendations = self._generate_recommendations(step, task, environment)

        return {
            "step": step,
            "environment": environment,
            "recommendations": recommendations,
        }

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        rec_count = len(action.get("recommendations", []))
        doc_count = len(action.get("environment", {}).get("workspace_docs", []))
        return (
            f"Prepared {rec_count} recommendation(s) using {doc_count} documented source(s) "
            f"for step '{action['step']}'."
        )

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes: List[Dict[str, Any]] = state.artifacts.setdefault("architecture_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "recommendations": action.get("recommendations", []),
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        completed = len(state.actions)
        return (
            f"Architected plan for '{task.title}' with {completed} structured step(s)."
        )

    def _build_environment_snapshot(self, task: TaskSpec) -> Dict[str, Any]:
        metadata = task.metadata or {}
        registered_tools = [
            f"{tool.name}: {tool.description}"
            for tool in self.tools.list_tools()
        ]
        knowledge_topics = metadata.get("knowledge_topics") or self._default_knowledge_topics()
        return {
            "workspace_docs": metadata.get("workspace_docs", []),
            "available_tools": metadata.get("available_tools", registered_tools),
            "test_commands": metadata.get("test_commands", []),
            "branch": metadata.get("branch", "feature/version2"),
            "knowledge_topics": knowledge_topics,
        }

    def _generate_recommendations(
        self,
        step: str,
        task: TaskSpec,
        environment: Dict[str, Any],
    ) -> List[str]:
        recommendations: List[str] = []

        if "Review workspace" in step:
            docs = environment.get("workspace_docs", [])
            if docs:
                recommendations.append("Prioritise reading: " + ", ".join(docs))
            else:
                recommendations.append("Capture workspace documentation inventory.")
            knowledge = environment.get("knowledge_topics", [])
            if knowledge:
                recommendations.append("Consult knowledge base: " + ", ".join(knowledge))

        if "Map available tools" in step:
            tools = environment.get("available_tools", [])
            if tools:
                recommendations.append("Document tool affordances: " + "; ".join(tools))
            else:
                recommendations.append("Introduce baseline tooling (shell, git, editor).")
            commands = environment.get("test_commands", [])
            if commands:
                recommendations.append("Codify regression suite: " + ", ".join(commands))

        if "Outline agent capabilities" in step:
            recommendations.extend([
                "Define reasoning loop template (plan → act → reflect).",
                "Specify safety constraints for shell/network usage.",
                "Design memory strategy (short-term state + long-term knowledge).",
            ])

        if "Define implementation milestones" in step:
            recommendations.extend([
                "Break work into ADR-backed milestones with acceptance criteria.",
                "Align roadmap tasks with repository structure under src/agent_platform/.",
                "Ensure unit tests accompany each new capability.",
            ])

        if "Recommend validation" in step:
            recommendations.extend([
                "Establish evaluation harness entry-points (pytest suites, scenario scripts).",
                "Schedule regular retrospectives to refine agent behaviours.",
                "Document human-in-the-loop checkpoints for high-risk actions.",
            ])

        if not recommendations:
            recommendations.append(f"Record notes for step: {step}.")

        task_hint = task.metadata.get("focus_area") if task.metadata else None
        if task_hint and task_hint not in " ".join(recommendations):
            recommendations.append(f"Ensure focus area '{task_hint}' is addressed explicitly.")

        return recommendations

    def _default_knowledge_topics(self) -> List[str]:
        knowledge_dir = Path("docs/agents/knowledge")
        topics: List[str] = []
        if knowledge_dir.exists():
            for path in sorted(knowledge_dir.glob("*.md")):
                topics.append(path.name)
        return topics
