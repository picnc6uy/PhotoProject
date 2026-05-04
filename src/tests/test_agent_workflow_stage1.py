from __future__ import annotations

from agent_platform.agents import (
    AgentConfig,
    ResourceSurveyor,
    TaskRefiner,
    RiskMonitor,
)
from agent_platform.tasks import TaskSpec
from agent_platform.tools import Tool, ToolContext, ToolRegistry


class DummyTool(Tool):
    def __init__(self):
        super().__init__(name="shell", description="Execute limited shell commands")

    def run(self, command: str, context: ToolContext) -> str:
        return f"ran:{command}"


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(DummyTool())
    return registry


def make_task() -> TaskSpec:
    return TaskSpec(
        title="Bootstrap developer agent",
        summary="Stand up initial agent workflow components.",
        requirements=["Document architecture", "Implement orchestrator", "Seed knowledge base"],
        metadata={
            "risk_level": "high",
            "touches_docs": True,
            "touches_ci": True,
            "dependencies": ["Knowledge base maintenance"],
            "test_commands": ["pytest -q"],
        },
    )


def test_resource_surveyor_collects_workspace_information():
    registry = build_registry()
    config = AgentConfig(name="survey", max_iterations=5)
    agent = ResourceSurveyor(config, registry)

    task = make_task()
    state = agent.run(task)

    survey = state.artifacts["survey"]
    assert survey["documents"]
    assert survey["tools"]
    assert survey["knowledge_topics"]
    assert "knowledge" in state.artifacts["survey_notes"][2]["observation"].lower()


def test_task_refiner_creates_acceptance_criteria():
    registry = build_registry()
    config = AgentConfig(name="refiner", max_iterations=5)
    agent = TaskRefiner(config, registry)

    task = make_task()
    state = agent.run(task)

    refined = state.artifacts["refined_spec"]
    assert len(refined["clarifications"]) >= 1
    assert len(refined["acceptance"]) == len(task.requirements)
    first_acceptance = refined["acceptance"][0]
    assert first_acceptance["automated_checks"] == ["pytest -q"]


def test_risk_monitor_flags_risks_and_mitigations():
    registry = build_registry()
    config = AgentConfig(name="risk", max_iterations=5)
    agent = RiskMonitor(config, registry)

    task = make_task()
    state = agent.run(task)

    report = state.artifacts["risk_report"]
    assert report["risk_level"] == "high"
    assert "Continuous Integration pipeline" in report["dependencies"]
    assert any("rollback" in m.lower() for m in report["mitigations"])
