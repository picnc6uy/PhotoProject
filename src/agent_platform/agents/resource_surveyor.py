"""Agent that surveys workspace resources relevant to a task."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

from .base import Agent
from ..tasks import TaskSpec


class ResourceSurveyor(Agent):
    """Collects documentation, knowledge topics, and tool listings."""

    def __init__(self, config, tools):  # type: ignore[override]
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec) -> Iterable[str]:
        return [
            "Collect documentation references",
            "List available tools",
            "Summarize knowledge topics",
        ]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        if self._step_index >= len(state.plan):
            return True
        return super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, Any]:  # type: ignore[override]
        step = state.plan[self._step_index]
        self._step_index += 1

        survey = state.artifacts.setdefault("survey", {
            "documents": [],
            "tools": [],
            "knowledge_topics": [],
        })

        metadata = task.metadata or {}
        if "documentation" in step.lower():
            docs = metadata.get("workspace_docs") or self._default_workspace_docs()
            survey["documents"] = docs
            result = {"documents": docs}
        elif "tools" in step.lower():
            tools = [f"{tool.name}: {tool.description}" for tool in self.tools.list_tools()]
            survey["tools"] = tools
            result = {"tools": tools}
        else:
            topics = metadata.get("knowledge_topics") or self._default_knowledge_topics()
            survey["knowledge_topics"] = topics
            result = {"knowledge_topics": topics}

        return {
            "step": step,
            "result": result,
        }

    def observe(self, task: TaskSpec, state, action: Dict[str, Any]) -> str:  # type: ignore[override]
        kind = next(iter(action["result"].keys()))
        count = len(action["result"][kind])
        return f"Captured {count} {kind.replace('_', ' ')}."

    def after_iteration(self, task, state, action, observation):  # type: ignore[override]
        notes = state.artifacts.setdefault("survey_notes", [])
        notes.append({
            "step": action["step"],
            "observation": observation,
            "result": action["result"],
        })

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        survey = state.artifacts.get("survey", {})
        doc_count = len(survey.get("documents", []))
        tool_count = len(survey.get("tools", []))
        topic_count = len(survey.get("knowledge_topics", []))
        return (
            f"Surveyed {doc_count} docs, {tool_count} tools, {topic_count} knowledge topics for '{task.title}'."
        )

    def _default_knowledge_topics(self) -> List[str]:
        knowledge_dir = Path("docs/agents/knowledge")
        if not knowledge_dir.exists():
            return []
        return [path.name for path in sorted(knowledge_dir.glob("*.md"))]

    def _default_workspace_docs(self) -> List[str]:
        defaults = [
            "MASTER_PROJECT_CONTEXT.md",
            "docs/agents/PROJECT_CHARTER.md",
            "docs/agents/ROADMAP.md",
            "docs/agents/AGENT_PLATFORM_ARCHITECTURE.md",
        ]
        return defaults
