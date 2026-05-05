from __future__ import annotations

from agent_platform.agents import AgentConfig, ResourceSurveyor
from agent_platform.orchestrator import Orchestrator
from agent_platform.tasks import TaskSpec
from agent_platform.tools import ShellCommandTool, ToolRegistry


def test_run_workflow_executes_agents(tmp_path):
    registry = ToolRegistry()
    registry.register(ShellCommandTool(working_dir=str(tmp_path)))
    orchestrator = Orchestrator(registry, cache_dir=tmp_path / "cache")

    task = TaskSpec(title="Workflow smoke test", summary="", requirements=["Collect docs"])

    records = orchestrator.run_workflow([ResourceSurveyor], task)
    assert "ResourceSurveyor" in records
    record = records["ResourceSurveyor"]
    assert record["state"]["artifacts"]["survey"]["documents"]
