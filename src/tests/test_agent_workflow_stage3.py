from __future__ import annotations

from agent_platform.agents import (
    AgentConfig,
    PlannerAgent,
    ImplementerAgent,
    TestRunnerAgent,
    CodeReviewer,
    RequirementsVerifier,
)
from agent_platform.tasks import AcceptanceCriteria, TaskSpec
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


def base_task() -> TaskSpec:
    return TaskSpec(
        title="Stage 3 agents",
        summary="Exercise test runner, code reviewer, and requirements verifier.",
        requirements=["Implement feature", "Add tests", "Update docs"],
        acceptance=[
            AcceptanceCriteria(description="Implement feature"),
            AcceptanceCriteria(description="Add tests"),
            AcceptanceCriteria(description="Update docs"),
        ],
        metadata={
            "test_commands": ["pytest -q", "flake8"],
        },
    )


def prepare_implementer_outputs(registry: ToolRegistry, task: TaskSpec):
    planner = PlannerAgent(AgentConfig(name="planner", max_iterations=5), registry)
    planner_state = planner.run(task)
    implement_task = TaskSpec(
        title=task.title,
        summary=task.summary,
        requirements=task.requirements,
        metadata={
            **task.metadata,
            "milestones": planner_state.artifacts["milestones"],
            "touches_docs": True,
        },
    )
    implementer = ImplementerAgent(AgentConfig(name="implementer", max_iterations=5), registry)
    state = implementer.run(implement_task)
    return state.artifacts["work_plan"]


def test_test_runner_executes_commands():
    registry = build_registry()
    task = base_task()
    runner = TestRunnerAgent(AgentConfig(name="testrunner", max_iterations=5), registry)
    state = runner.run(task)

    summary = state.artifacts["test_run"]["summary"]
    assert summary["passed"] == len(task.metadata["test_commands"])
    assert not summary.get("failed")


def test_code_reviewer_flags_risks_when_tests_missing():
    registry = build_registry()
    task = base_task()
    work_plan = prepare_implementer_outputs(registry, task)

    reviewer_task = TaskSpec(
        title=task.title,
        summary=task.summary,
        requirements=task.requirements,
        metadata={
            "proposed_changes": work_plan["proposed_changes"],
            "test_results": [],
        },
    )
    reviewer = CodeReviewer(AgentConfig(name="reviewer", max_iterations=5), registry)
    state = reviewer.run(reviewer_task)

    review = state.artifacts["review"]
    assert review["decision"] == "changes_requested"
    assert review["risks"]


def test_requirements_verifier_reports_coverage():
    registry = build_registry()
    task = base_task()
    work_plan = prepare_implementer_outputs(registry, task)

    verifier_task = TaskSpec(
        title=task.title,
        summary=task.summary,
        requirements=task.requirements,
        acceptance=task.acceptance,
        metadata={
            "proposed_changes": work_plan["proposed_changes"],
        },
    )
    verifier = RequirementsVerifier(AgentConfig(name="verifier", max_iterations=5), registry)
    state = verifier.run(verifier_task)

    verification = state.artifacts["verification"]
    assert verification["results"]
    summary = verification["summary"]
    assert summary["satisfied"] <= len(verification["results"])
    assert summary["unsatisfied"] >= 0
