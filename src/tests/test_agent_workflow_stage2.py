from __future__ import annotations

from agent_platform.agents import (
    AgentConfig,
    PlannerAgent,
    DesignAdvisor,
    ImplementerAgent,
)
from agent_platform.tasks import TaskSpec
from agent_platform.tools import Tool, ToolContext, ToolRegistry


class DummyTool(Tool):
    def __init__(self):
        super().__init__(name="shell", description="Execute limited shell commands")

    def run(self, command: str, context: ToolContext) -> str:
        return f"ran:{command}@{context.working_dir}"


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(DummyTool())
    return registry


def make_task() -> TaskSpec:
    return TaskSpec(
        title="Implement planner through implementer agents",
        summary="Plan milestones, provide design advice, and draft implementation steps.",
        requirements=[
            "Create planner milestones",
            "Produce design recommendations",
            "Draft implementation plan",
        ],
        metadata={
            "risk_level": "medium",
            "components": ["agent_platform", "tests"],
            "touches_docs": True,
            "test_commands": ["echo pytest -q", "echo flake8"],
        },
    )


def test_planner_agent_creates_milestones_and_assignments():
    registry = build_registry()
    config = AgentConfig(name="planner", max_iterations=5)
    agent = PlannerAgent(config, registry)

    task = make_task()
    state = agent.run(task)

    milestones = state.artifacts["milestones"]
    assert len(milestones) == len(task.requirements)
    assert state.artifacts["plan_notes"]


def test_design_advisor_suggests_components_and_adrs():
    registry = build_registry()
    planner = PlannerAgent(AgentConfig(name="planner", max_iterations=5), registry)
    task = make_task()
    planner_state = planner.run(task)

    design_task = TaskSpec(
        title=task.title,
        summary=task.summary,
        requirements=task.requirements,
        metadata={
            **task.metadata,
            "milestones": planner_state.artifacts["milestones"],
        },
    )

    advisor = DesignAdvisor(AgentConfig(name="design", max_iterations=5), registry)
    state = advisor.run(design_task)

    design = state.artifacts["design"]
    assert design["components"]
    assert design["adr_topics"]
    assert any("orchestrator" in topic.lower() for topic in design["adr_topics"])


def test_implementer_agent_prepares_proposed_changes():
    registry = build_registry()
    planner = PlannerAgent(AgentConfig(name="planner", max_iterations=5), registry)
    task = make_task()
    planner_state = planner.run(task)

    implement_task = TaskSpec(
        title=task.title,
        summary=task.summary,
        requirements=task.requirements,
        metadata={
            **task.metadata,
            "milestones": planner_state.artifacts["milestones"],
        },
    )

    implementer = ImplementerAgent(AgentConfig(name="implementer", max_iterations=5), registry)
    state = implementer.run(implement_task)

    work_plan = state.artifacts["work_plan"]
    assert work_plan["milestone"] is not None
    assert work_plan["steps"]
    assert work_plan["proposed_changes"]
    assert all(entry["tool_output"].startswith("ran:") for entry in work_plan["proposed_changes"])
