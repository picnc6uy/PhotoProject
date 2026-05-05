from __future__ import annotations

from agent_platform.agents import (
    AgentConfig,
    IntegratorAgent,
    ReleaseCoordinator,
    PostMergeObserver,
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


def task_metadata() -> TaskSpec:
    return TaskSpec(
        title="Finalize release process",
        summary="Stage accepted changes, coordinate release, and monitor post-merge.",
        requirements=["Stage code", "Notify stakeholders", "Monitor release"],
        metadata={
            "touches_docs": True,
            "doc_updates": ["README.md", "docs/agent_platform/ARCHITECTURE.md"],
            "deployment_commands": ["./deploy.sh", "./notify.sh"],
            "monitoring_signals": [
                {"metric": "error_rate", "value": 0.02},
                {"metric": "latency_ms", "value": 180},
            ],
            "requires_rollback_plan": True,
        },
    )


def test_integrator_prepares_staging_and_docs():
    registry = build_registry()
    task = task_metadata()
    integrator = IntegratorAgent(AgentConfig(name="integrator", max_iterations=5), registry)
    state = integrator.run(task)

    integration = state.artifacts["integration"]
    assert integration["staging"]
    assert integration["commit_message"]
    assert integration["docs"] == task.metadata["doc_updates"]


def test_release_coordinator_builds_checklist_and_notification():
    registry = build_registry()
    task = task_metadata()
    coordinator = ReleaseCoordinator(AgentConfig(name="release", max_iterations=5), registry)
    state = coordinator.run(task)

    release = state.artifacts["release"]
    assert len(release["checklist"]) >= 3
    assert release["commands"] == task.metadata["deployment_commands"]
    assert "Release Update" in release["notification"]


def test_post_merge_observer_recommends_monitoring():
    registry = build_registry()
    task = task_metadata()
    observer = PostMergeObserver(AgentConfig(name="postmerge", max_iterations=5), registry)
    state = observer.run(task)

    postmerge = state.artifacts["postmerge"]
    assert postmerge["signals"]
    assert postmerge["analysis"] in ([], ["Error rate exceeds threshold.", "Latency degradation detected."])
    assert postmerge["recommendation"] in {"monitor", "rollback", "extend_monitoring"}
